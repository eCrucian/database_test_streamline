"""Servidor MCP: ferramentas determinísticas sobre o núcleo, para qualquer cliente MCP.

No MCP quem raciocina é o LLM do cliente; por isso nada aqui chama LLM. A execução não
corrige queries sozinha: devolve o erro e o cliente corrige via `set_sql`.
"""

import getpass
from collections.abc import Callable
from pathlib import Path
from typing import Any

import boto3
from mcp.server.mcpserver import MCPServer

from dbts.adapters.athena import AthenaExecutor
from dbts.adapters.sinks import CsvSink
from dbts.adapters.sql_store import open_store
from dbts.audit.log import AuditLog
from dbts.config import Settings
from dbts.domain.execution import QueryFailedError
from dbts.domain.testing import ProposalStatus, TestProposal
from dbts.execution.library import QueryLibrary
from dbts.execution.runner import RunResult, TestRunner
from dbts.extract.registry import EXTRACTORS, extractors_fingerprint
from dbts.mapping.graph import Graph
from dbts.mapping.guide import build_guide, load_subgraph, slugify
from dbts.mapping.render import render_json
from dbts.mapping.scanner import Scanner
from dbts.ports import QueryExecutor
from dbts.reporting.report import ReportWriter, build_report
from dbts.testing.codegen import Language
from dbts.testing.plans import PlanBook

ExecutorFactory = Callable[[str, str], QueryExecutor]
PREVIEW_ROWS = 20


def _athena(database: str, workgroup: str) -> QueryExecutor:
    """Credenciais e região vêm do ambiente (AWS_PROFILE, AWS_DEFAULT_REGION)."""
    return AthenaExecutor(boto3.Session().client("athena"), database, workgroup)


def _summary(proposal: TestProposal) -> dict[str, Any]:
    return {
        "id": proposal.id,
        "status": proposal.status,
        "severity": proposal.severity,
        "title": proposal.title,
        "missing": proposal.missing,
    }


def _detail(proposal: TestProposal) -> dict[str, Any]:
    evidence = [f"{e.repo}/{e.path}:{e.line}@{e.commit_sha[:8]}" for e in proposal.evidence]
    return _summary(proposal) | {
        "description": proposal.description,
        "criterio": proposal.criterio,
        "params": proposal.params,
        "evidence": evidence,
        "sql": proposal.render(),
    }


class DbtsTools:
    """Cada método público é uma ferramenta MCP; a docstring é a descrição para o cliente."""

    def __init__(self, settings: Settings, executor_factory: ExecutorFactory = _athena) -> None:
        self._settings = settings
        self._executor_factory = executor_factory
        self._user = f"{getpass.getuser()}@mcp"
        self._audit = AuditLog(settings.audit_dir)
        self._book = PlanBook(settings.plans_dir, self._audit, self._user)

    def scan(self, root: str) -> list[dict[str, Any]]:
        """Mapeia os repos Git em `root`, reprocessando só o que mudou desde o último scan."""
        store = open_store(self._settings)
        try:
            scanner = Scanner(store, self._audit, self._user, EXTRACTORS, extractors_fingerprint())
            plans = scanner.scan(Path(root))
        finally:
            store.close()
        return [
            {
                "repo": p.snapshot.name,
                "commit": p.snapshot.commit_sha,
                "changed": len(p.changed),
                "removed": len(p.removed),
            }
            for p in plans
        ]

    def guide(self, term: str | None = None, depth: int = 2) -> str:
        """Guia Markdown (Mermaid + cartões de tabela) em torno de `term`, ou mapa completo."""
        store = open_store(self._settings)
        try:
            out = self._settings.guides_dir
            result = build_guide(store, out, self._audit, self._user, term, depth)
        finally:
            store.close()
        if result is None:
            raise ValueError(f"nenhuma entidade casa com '{term}'")
        return result.markdown.read_text(encoding="utf-8")

    def lineage_json(self, term: str | None = None, depth: int = 2) -> str:
        """Grafo (entidades, arestas, localizações no código) em JSON legível por IA."""
        graph, commits = self._subgraph(term, depth)
        return render_json(graph, term or "mapa-completo", commits)

    def propose(self, term: str, depth: int = 2, plan: str | None = None) -> list[dict[str, Any]]:
        """Propõe testes (biblioteca de hipóteses) em torno de `term` no plano `plan`."""
        graph, commits = self._subgraph(term, depth)
        result = self._book.propose(plan or slugify(term), graph, term, commits)
        return [_summary(p) for p in result.proposals]

    def show_plan(self, plan: str) -> list[dict[str, Any]]:
        """Propostas do plano com descrição, critério, parâmetros, evidência e SQL."""
        return [_detail(p) for p in self._book.load(plan).proposals]

    def set_status(self, plan: str, ids: list[str], status: ProposalStatus) -> list[dict[str, Any]]:
        """Aceita ou rejeita propostas."""
        return [_summary(p) for p in self._book.set_status(plan, ids, status).proposals]

    def set_params(self, plan: str, proposal_id: str, params: dict[str, str]) -> dict[str, Any]:
        """Define parâmetros faltantes de uma proposta."""
        return _detail(self._book.set_params(plan, proposal_id, params).get(proposal_id))

    def set_sql(self, plan: str, proposal_id: str, sql: str) -> dict[str, Any]:
        """Substitui o SQL de uma proposta (ex.: após corrigir um erro de execução)."""
        return _detail(self._book.replace_sql(plan, proposal_id, sql).get(proposal_id))

    def add_test(self, plan: str, title: str, sql: str, description: str = "") -> dict[str, Any]:
        """Adiciona um teste escrito pelo usuário (entra aceito)."""
        return _detail(self._book.add_custom(plan, title, description, sql))

    def generate(self, plan: str, lang: Language = Language.SQL) -> dict[str, str]:
        """Código das propostas aceitas, com cabeçalho descritivo, por caminho do arquivo."""
        return {str(path): code for path, code in self._book.generate(plan, lang).items()}

    def run_test(
        self,
        plan: str,
        proposal_id: str,
        database: str,
        workgroup: str,
        sandbox: str,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Executa uma proposta no Athena (custa dinheiro: exige confirm=true).

        Em erro, devolve a mensagem e o SQL; corrija com set_sql e execute de novo.
        """
        test_plan = self._book.load(plan)
        proposal = test_plan.get(proposal_id)
        if not confirm:
            return {"status": "confirmacao_necessaria", "sql": proposal.render()}
        executor = self._executor_factory(database, workgroup)
        sinks = [CsvSink(self._settings.queries_dir / "results")]
        library = QueryLibrary(self._settings.queries_dir)
        runner = TestRunner(executor, library, self._audit, self._user, sandbox, sinks, 0)
        try:
            result = runner.run(proposal, test_plan, lambda *_: None)
        except QueryFailedError as error:
            return {"status": "erro", "erro": str(error), "sql": proposal.render()}
        return self._success(result, proposal, plan)

    def list_runs(self, plan: str | None = None) -> list[dict[str, Any]]:
        """Execuções registradas na biblioteca de queries (opcionalmente de um plano)."""
        runs = QueryLibrary(self._settings.queries_dir).runs()
        return [r.model_dump(mode="json") for r in runs if plan is None or r.plan == plan]

    def audit_verify(self) -> dict[str, Any]:
        """Verifica a integridade da trilha de auditoria (cadeia de hashes)."""
        broken = self._audit.verify()
        return {"integra": broken is None, "registro_adulterado": broken}

    def _subgraph(self, term: str | None, depth: int) -> tuple[Graph, dict[str, str]]:
        store = open_store(self._settings)
        try:
            graph, commits = load_subgraph(store, term, depth), store.repo_commits()
        finally:
            store.close()
        if graph is None:
            raise ValueError(f"nenhuma entidade casa com '{term}'")
        return graph, commits

    def _success(self, result: RunResult, proposal: TestProposal, plan: str) -> dict[str, Any]:
        query = result.outcome.result
        test_plan = self._book.load(plan)
        report = build_report(
            proposal, test_plan, result.record, result.outcome.sql, (query.columns, query.rows)
        )
        writer = ReportWriter(self._settings.reports_dir, self._audit, self._user)
        return {
            "status": "ok",
            "columns": query.columns,
            "rows": query.rows[:PREVIEW_ROWS],
            "total_rows": len(query.rows),
            "query_path": str(result.query_path),
            "results": result.record.results,
            "report_path": str(writer.write(report)),
        }


TOOL_NAMES = (
    "scan",
    "guide",
    "lineage_json",
    "propose",
    "show_plan",
    "set_status",
    "set_params",
    "set_sql",
    "add_test",
    "generate",
    "run_test",
    "list_runs",
    "audit_verify",
)


def build_server(settings: Settings, executor_factory: ExecutorFactory = _athena) -> MCPServer:
    tools = DbtsTools(settings, executor_factory)
    server = MCPServer("dbts", instructions=__doc__)
    for name in TOOL_NAMES:
        server.add_tool(getattr(tools, name))
    return server
