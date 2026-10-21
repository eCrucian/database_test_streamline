import getpass
import os
import shlex

# Abre o $EDITOR do usuário, sem shell.
import subprocess  # nosec B404
import tempfile
from collections.abc import Callable
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import boto3
import typer

from dbts import __version__
from dbts.adapters.athena import AthenaExecutor
from dbts.adapters.duckdb_executor import DuckDBExecutor
from dbts.adapters.llm import build_llm
from dbts.adapters.sinks import AthenaTableSink, CsvSink, ParquetSink
from dbts.adapters.sql_store import open_store
from dbts.audit.log import AuditLog
from dbts.config import Settings, resolve_settings
from dbts.domain.execution import QueryFailedError
from dbts.domain.testing import ProposalStatus, TestPlan, TestProposal
from dbts.enrich.tables import TableEnricher
from dbts.execution.fixer import SqlFixer
from dbts.execution.library import QueryLibrary
from dbts.execution.repair import Decide
from dbts.execution.runner import RunResult, TestRunner
from dbts.extract.registry import EXTRACTORS, extractors_fingerprint
from dbts.mapping.guide import build_guide, load_subgraph, slugify
from dbts.mapping.scanner import Scanner
from dbts.mcp_server import build_server
from dbts.ports import LLMProvider, QueryExecutor, ResultSink
from dbts.reporting.report import Analyst, ReportWriter, build_report, load_csv, strip_header
from dbts.testing.codegen import Language, MissingParamsError
from dbts.testing.plans import PlanBook

app = typer.Typer(no_args_is_help=True)
audit_app = typer.Typer(no_args_is_help=True, help="Trilha de auditoria.")
app.add_typer(audit_app, name="audit")
plan_app = typer.Typer(no_args_is_help=True, help="Refinar planos de teste.")
app.add_typer(plan_app, name="plan")


MapDirOption = Annotated[
    Path | None,
    typer.Option("--map-dir", help="Diretório do mapa (padrão: $DBTS_MAP_DIR ou ~/.dbts)."),
]


def _settings(map_dir: Path | None) -> Settings:
    return resolve_settings(os.environ, Path.home(), map_dir)


def _llm(settings: Settings) -> LLMProvider:
    return build_llm(settings)


@app.command()
def version() -> None:
    """Mostra a versão."""
    typer.echo(__version__)


@app.command()
def config(map_dir: MapDirOption = None) -> None:
    """Mostra a configuração resolvida."""
    settings = _settings(map_dir)
    typer.echo(f"map_dir: {settings.map_dir}")
    typer.echo(f"llm: {settings.llm_provider}/{settings.llm_model}")


@app.command()
def scan(
    root: Annotated[
        Path, typer.Argument(exists=True, file_okay=False, help="Diretório com repos.")
    ],
    map_dir: MapDirOption = None,
) -> None:
    """Mapeia os repos de ROOT, reprocessando só o que mudou desde o último scan."""
    settings = _settings(map_dir)
    store = open_store(settings)
    try:
        audit = AuditLog(settings.audit_dir)
        fingerprint = extractors_fingerprint()
        scanner = Scanner(store, audit, getpass.getuser(), EXTRACTORS, fingerprint)
        plans = scanner.scan(root)
    finally:
        store.close()
    for plan in plans:
        status = (
            "sem mudanças"
            if plan.is_noop
            else f"{len(plan.changed)} alterados, {len(plan.removed)} removidos"
        )
        typer.echo(f"{plan.snapshot.name} @ {plan.snapshot.commit_sha[:8]}: {status}")


@app.command()
def facts(repo: str, map_dir: MapDirOption = None) -> None:
    """Lista as arestas mapeadas de um repo, com origem e localização."""
    store = open_store(_settings(map_dir))
    try:
        items = store.facts(repo)
    finally:
        store.close()
    for fact in items:
        if fact.edge:
            loc = fact.location
            edge = fact.edge
            typer.echo(f"{edge.source} -[{edge.kind}]-> {edge.target}  ({loc.path}:{loc.line})")


@app.command("map")
def map_command(
    term: Annotated[str | None, typer.Argument(help="Termo (tabela, coluna, job).")] = None,
    all_: Annotated[bool, typer.Option("--all", help="Mapa completo de todos os repos.")] = False,
    depth: Annotated[int, typer.Option(min=0, help="Saltos a partir do termo.")] = 2,
    enrich: Annotated[bool, typer.Option(help="Resumir tabelas com o LLM (com cache).")] = False,
    map_dir: MapDirOption = None,
) -> None:
    """Gera um guia (Markdown + Mermaid + JSON) em torno de TERM, ou o mapa completo."""
    if (term is None) == (not all_):
        typer.echo("informe um TERMO ou --all (não ambos)", err=True)
        raise typer.Exit(code=2)
    settings = _settings(map_dir)
    store = open_store(settings)
    try:
        audit, user = AuditLog(settings.audit_dir), getpass.getuser()
        enricher = TableEnricher(_llm(settings), store, audit, user) if enrich else None
        result = build_guide(store, settings.guides_dir, audit, user, term, depth, enricher)
    finally:
        store.close()
    if result is None:
        typer.echo(f"nenhuma entidade casa com '{term}'", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"{result.entities} entidades")
    typer.echo(str(result.markdown))
    typer.echo(str(result.json))


def _book(settings: Settings) -> PlanBook:
    return PlanBook(settings.plans_dir, AuditLog(settings.audit_dir), getpass.getuser())


def _print_plan(plan: TestPlan) -> None:
    for p in plan.proposals:
        missing = f"  [faltando: {', '.join(p.missing)}]" if p.missing else ""
        typer.echo(f"{p.id}  {p.status:<9} {p.severity:<5} {p.title}{missing}")


def _parse_params(items: list[str]) -> dict[str, str]:
    pairs = [item.split("=", 1) for item in items]
    if any(len(pair) != 2 or not pair[0] for pair in pairs):
        raise typer.BadParameter("use chave=valor")
    return {key: value for key, value in pairs}


@app.command("propose")
def propose_command(
    term: Annotated[str, typer.Argument(help="Termo (tabela, coluna, job).")],
    depth: Annotated[int, typer.Option(min=0, help="Saltos a partir do termo.")] = 2,
    plan: Annotated[str | None, typer.Option(help="Nome do plano (padrão: o termo).")] = None,
    map_dir: MapDirOption = None,
) -> None:
    """Propõe testes a partir da biblioteca de hipóteses, em torno de TERM."""
    settings = _settings(map_dir)
    store = open_store(settings)
    try:
        graph, commits = load_subgraph(store, term, depth), store.repo_commits()
    finally:
        store.close()
    if graph is None:
        typer.echo(f"nenhuma entidade casa com '{term}'", err=True)
        raise typer.Exit(code=1)
    result = _book(settings).propose(plan or slugify(term), graph, term, commits)
    _print_plan(result)


@plan_app.command("show")
def plan_show(
    name: str,
    sql: Annotated[bool, typer.Option(help="Mostrar o SQL de cada proposta.")] = False,
    map_dir: MapDirOption = None,
) -> None:
    """Lista as propostas do plano."""
    plan = _book(_settings(map_dir)).load(name)
    _print_plan(plan)
    for p in plan.proposals if sql else ():
        typer.echo(f"\n-- {p.id}: {p.description}\n-- critério: {p.criterio}\n{p.render()}")


@plan_app.command("accept")
def plan_accept(name: str, ids: list[str], map_dir: MapDirOption = None) -> None:
    """Aceita propostas (vão para a geração de código)."""
    _print_plan(_book(_settings(map_dir)).set_status(name, ids, ProposalStatus.ACCEPTED))


@plan_app.command("reject")
def plan_reject(name: str, ids: list[str], map_dir: MapDirOption = None) -> None:
    """Rejeita propostas."""
    _print_plan(_book(_settings(map_dir)).set_status(name, ids, ProposalStatus.REJECTED))


@plan_app.command("set")
def plan_set(name: str, pid: str, params: list[str], map_dir: MapDirOption = None) -> None:
    """Define parâmetros de uma proposta: chave=valor ..."""
    _print_plan(_book(_settings(map_dir)).set_params(name, pid, _parse_params(params)))


@plan_app.command("add")
def plan_add(
    name: str,
    title: Annotated[str, typer.Option(help="Título do teste.")],
    sql_file: Annotated[Path, typer.Option(exists=True, dir_okay=False, help="Arquivo SQL.")],
    description: Annotated[str, typer.Option(help="O que o teste verifica.")] = "",
    map_dir: MapDirOption = None,
) -> None:
    """Adiciona um teste escrito pelo usuário (entra aceito)."""
    sql = sql_file.read_text(encoding="utf-8")
    proposal = _book(_settings(map_dir)).add_custom(name, title, description, sql)
    typer.echo(proposal.id)


@app.command("generate")
def generate_command(
    name: str,
    lang: Annotated[Language, typer.Option(help="Linguagem do código.")] = Language.SQL,
    map_dir: MapDirOption = None,
) -> None:
    """Gera o código das propostas aceitas do plano NAME e o exibe."""
    try:
        files = _book(_settings(map_dir)).generate(name, lang)
    except MissingParamsError as error:
        typer.echo(f"{error}; use 'dbts plan set'", err=True)
        raise typer.Exit(code=1) from error
    for path, code in files.items():
        typer.echo(f"# {path}\n{code}")


def _executor(
    database: str,
    workgroup: str,
    profile: str | None,
    region: str | None,
    local_db: Path | None = None,
) -> QueryExecutor:
    """Athena por padrão; com `local_db`, executa localmente em DuckDB (ensaio offline)."""
    if local_db is not None:
        return DuckDBExecutor(local_db)
    session = boto3.Session(profile_name=profile, region_name=region)
    return AthenaExecutor(session.client("athena"), database, workgroup)


def _edit(text: str) -> str | None:
    """Abre $EDITOR com `text`; None se nada mudou ou ficou vazio."""
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as tmp:
        tmp.write(text)
    path = Path(tmp.name)
    editor = shlex.split(os.environ.get("EDITOR", "vi"))
    # $EDITOR do próprio usuário, em lista e sem shell.
    subprocess.run([*editor, str(path)], check=False)  # nosec B603
    edited = path.read_text(encoding="utf-8")
    path.unlink()
    return edited if edited.strip() and edited != text else None


def _interactive_decide(fixer: SqlFixer) -> Decide:
    def decide(sql: str, error: str, attempt: int) -> tuple[str, str] | None:
        typer.echo(f"\nerro (tentativa {attempt}): {error}")
        choice = typer.prompt("[a]uto-corrigir com LLM, [m]anual no editor, [p]ular", default="a")
        if choice == "a":
            fix = fixer.fix(sql, error)
            typer.echo(f"\n-- correção sugerida: {fix.explicacao}\n{fix.sql}")
            return (fix.sql, "llm") if typer.confirm("Executar a versão corrigida?", True) else None
        if choice == "m":
            edited = _edit(sql)
            return (edited, "usuario") if edited else None
        return None

    return decide


class SinkName(StrEnum):
    CSV = "csv"
    PARQUET = "parquet"
    TABLE = "table"


def _sinks(
    names: list[SinkName], settings: Settings, executor: QueryExecutor, sandbox: str
) -> list[ResultSink]:
    results = settings.queries_dir / "results"
    factories: dict[SinkName, Callable[[], ResultSink]] = {
        SinkName.CSV: lambda: CsvSink(results),
        SinkName.PARQUET: lambda: ParquetSink(results),
        SinkName.TABLE: lambda: AthenaTableSink(executor, sandbox),
    }
    return [factories[name]() for name in dict.fromkeys(names)]


def _run_one(
    runner: TestRunner,
    proposal: TestProposal,
    plan: TestPlan,
    decide: Decide,
    reporting: tuple[ReportWriter, Analyst | None],
) -> RunResult:
    result = runner.run(proposal, plan, decide)
    writer, analyst = reporting
    outcome = result.outcome
    report = build_report(
        proposal,
        plan,
        result.record,
        outcome.sql,
        (outcome.result.columns, outcome.result.rows),
        analyst,
    )
    typer.echo(f"ok: {len(outcome.result.rows)} linhas; query: {result.query_path}")
    for name, location in result.record.results.items():
        typer.echo(f"{name}: {location}")
    typer.echo(f"relatório: {writer.write(report)}")
    return result


@app.command("run")
def run_command(
    name: Annotated[str, typer.Argument(help="Plano de testes.")],
    ids: Annotated[list[str] | None, typer.Argument(help="Propostas (padrão: aceitas).")] = None,
    database: Annotated[str, typer.Option(envvar="DBTS_ATHENA_DATABASE")] = "default",
    workgroup: Annotated[str, typer.Option(envvar="DBTS_ATHENA_WORKGROUP")] = "primary",
    sandbox: Annotated[str, typer.Option(envvar="DBTS_SANDBOX", help="Schema de escrita.")] = "",
    profile: Annotated[str | None, typer.Option(envvar="AWS_PROFILE")] = None,
    region: Annotated[str | None, typer.Option(envvar="AWS_REGION")] = None,
    local_db: Annotated[
        Path | None,
        typer.Option(envvar="DBTS_LOCAL_DB", help="Banco DuckDB local: executa sem AWS."),
    ] = None,
    sink: Annotated[list[SinkName] | None, typer.Option(help="Destino(s) do resultado.")] = None,
    max_fixes: Annotated[int, typer.Option(min=0, help="Correções por query.")] = 3,
    analysis: Annotated[bool, typer.Option(help="Análise do relatório pelo LLM.")] = True,
    yes: Annotated[bool, typer.Option("--yes", help="Não pedir confirmação.")] = False,
    map_dir: MapDirOption = None,
) -> None:
    """Executa no Athena as propostas do plano, com guarda, correção, relatório e auditoria."""
    settings = _settings(map_dir)
    book, audit, user = _book(settings), AuditLog(settings.audit_dir), getpass.getuser()
    plan = book.load(name)
    selected = (
        [plan.get(pid) for pid in ids]
        if ids
        else [p for p in plan.proposals if p.status is ProposalStatus.ACCEPTED]
    )
    executor = _executor(database, workgroup, profile, region, local_db)
    sinks = _sinks(sink or [SinkName.CSV], settings, executor, sandbox)
    library = QueryLibrary(settings.queries_dir)
    runner = TestRunner(executor, library, audit, user, sandbox, sinks, max_fixes)
    llm = _llm(settings)
    decide = _interactive_decide(SqlFixer(llm, audit, user))
    reporting = (
        ReportWriter(settings.reports_dir, audit, user),
        Analyst(llm, audit, user) if analysis else None,
    )
    failures = 0
    for proposal in selected:
        typer.echo(f"\n== {proposal.id}: {proposal.title}\n{proposal.render()}")
        if not (yes or typer.confirm("Executar no Athena?", default=False)):
            continue
        try:
            result = _run_one(runner, proposal, plan, decide, reporting)
        except QueryFailedError as error:
            failures += 1
            typer.echo(f"falhou: {error}", err=True)
            continue
        if result.outcome.attempts:
            book.replace_sql(name, proposal.id, result.outcome.sql)
    if failures:
        raise typer.Exit(code=1)


@app.command("report")
def report_command(
    name: Annotated[str, typer.Argument(help="Plano de testes.")],
    pid: Annotated[str, typer.Argument(help="Proposta.")],
    analysis: Annotated[bool, typer.Option(help="Análise pelo LLM.")] = True,
    map_dir: MapDirOption = None,
) -> None:
    """Refaz o relatório da última execução de uma proposta (requer resultado em CSV)."""
    settings = _settings(map_dir)
    audit, user = AuditLog(settings.audit_dir), getpass.getuser()
    runs = [r for r in QueryLibrary(settings.queries_dir).runs() if r.proposal_id == pid]
    if not runs or "csv" not in runs[-1].results:
        typer.echo(f"nenhuma execução com resultado CSV para '{pid}'", err=True)
        raise typer.Exit(code=1)
    run = runs[-1]
    plan = _book(settings).load(name)
    sql = strip_header(Path(run.query_path).read_text(encoding="utf-8"))
    analyst = Analyst(_llm(settings), audit, user) if analysis else None
    report = build_report(
        plan.get(pid), plan, run, sql, load_csv(Path(run.results["csv"])), analyst
    )
    typer.echo(str(ReportWriter(settings.reports_dir, audit, user).write(report)))


@app.command("mcp")
def mcp_command(map_dir: MapDirOption = None) -> None:
    """Inicia o servidor MCP (stdio) com as ferramentas do dbts."""
    build_server(_settings(map_dir)).run("stdio")


@audit_app.command("verify")
def audit_verify(map_dir: MapDirOption = None) -> None:
    """Verifica a integridade da cadeia de hashes."""
    broken = AuditLog(_settings(map_dir).audit_dir).verify()
    if broken is None:
        typer.echo("trilha íntegra")
        return
    typer.echo(f"trilha adulterada no registro {broken}", err=True)
    raise typer.Exit(code=1)
