from pathlib import Path

import pytest
from conftest import GitRepo
from typer.testing import CliRunner

from dbts import __version__
from dbts.audit.log import LOG_FILE, AuditEvent, AuditLog
from dbts.cli.app import app
from dbts.domain.models import Origin

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_config_shows_map_dir(tmp_path: Path) -> None:
    result = runner.invoke(app, ["config", "--map-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert f"map_dir: {tmp_path}" in result.output


def test_scan_reports_changes_then_noop(tmp_path: Path, git_repo: GitRepo) -> None:
    git_repo("a", {"q.sql": "select 1"})
    args = ["scan", str(tmp_path / "repos"), "--map-dir", str(tmp_path / "map")]

    first = runner.invoke(app, args)
    second = runner.invoke(app, args)

    assert first.exit_code == 0
    assert "a @" in first.output and "1 alterados, 0 removidos" in first.output
    assert "sem mudanças" in second.output


def test_facts_lists_edges_with_location(tmp_path: Path, git_repo: GitRepo) -> None:
    git_repo("a", {"q.sql": "\ninsert into t2 select x from t1"})
    map_dir = str(tmp_path / "map")
    runner.invoke(app, ["scan", str(tmp_path / "repos"), "--map-dir", map_dir])

    result = runner.invoke(app, ["facts", "a", "--map-dir", map_dir])

    assert result.exit_code == 0
    assert "job:a/q.sql -[writes]-> table:t2  (q.sql:2)" in result.output
    assert all("-[" in line for line in result.output.splitlines())


def test_audit_verify_ok(tmp_path: Path) -> None:
    AuditLog(tmp_path / "audit").append(AuditEvent(action="scan", user="u", origin=Origin.USER))
    result = runner.invoke(app, ["audit", "verify", "--map-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "íntegra" in result.output


def test_audit_verify_tampered(tmp_path: Path) -> None:
    AuditLog(tmp_path / "audit").append(AuditEvent(action="scan", user="u", origin=Origin.USER))
    path = tmp_path / "audit" / LOG_FILE
    path.write_text(path.read_text().replace('"scan"', '"x"'))
    result = runner.invoke(app, ["audit", "verify", "--map-dir", str(tmp_path)])
    assert result.exit_code == 1


def test_map_term_and_all(tmp_path: Path, git_repo: GitRepo) -> None:
    git_repo("a", {"q.sql": "insert into t2 select x from t1"})
    map_dir = str(tmp_path / "map")
    runner.invoke(app, ["scan", str(tmp_path / "repos"), "--map-dir", map_dir])

    by_term = runner.invoke(app, ["map", "t2", "--map-dir", map_dir])
    full = runner.invoke(app, ["map", "--all", "--map-dir", map_dir])

    assert by_term.exit_code == 0
    assert str(tmp_path / "map" / "guides" / "t2.md") in by_term.output
    assert full.exit_code == 0
    assert "mapa-completo.json" in full.output


def test_map_requires_exactly_one_of_term_or_all(tmp_path: Path) -> None:
    assert runner.invoke(app, ["map", "--map-dir", str(tmp_path)]).exit_code == 2
    assert runner.invoke(app, ["map", "x", "--all", "--map-dir", str(tmp_path)]).exit_code == 2


def test_map_unknown_term(tmp_path: Path) -> None:
    result = runner.invoke(app, ["map", "nada", "--map-dir", str(tmp_path)])
    assert result.exit_code == 1


def test_map_enrich_uses_configured_llm(
    tmp_path: Path, git_repo: GitRepo, monkeypatch: pytest.MonkeyPatch
) -> None:
    from dbts.adapters.fake_llm import FakeLLMProvider
    from dbts.cli import app as cli_module

    answer = '{"resumo": "R.", "papel": "saida", "pontos_de_atencao": []}'
    monkeypatch.setattr(cli_module, "_llm", lambda _: FakeLLMProvider([answer]))
    git_repo("a", {"q.sql": "insert into t2 select x from t1"})
    map_dir = str(tmp_path / "map")
    runner.invoke(app, ["scan", str(tmp_path / "repos"), "--map-dir", map_dir])

    result = runner.invoke(app, ["map", "t2", "--depth", "0", "--enrich", "--map-dir", map_dir])

    assert result.exit_code == 0
    assert "Resumo (LLM" in (tmp_path / "map" / "guides" / "t2.md").read_text()


def test_default_llm_is_ollama_with_configured_model(tmp_path: Path) -> None:
    from dbts.cli.app import _llm
    from dbts.config import resolve_settings

    llm = _llm(resolve_settings({"DBTS_LLM_MODEL": "qwen3:4b"}, tmp_path))
    assert (llm.name, llm.model) == ("ollama", "qwen3:4b")


def test_config_shows_llm(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DBTS_LLM_PROVIDER", "anthropic")
    result = runner.invoke(app, ["config", "--map-dir", str(tmp_path)])
    assert "llm: anthropic/claude-sonnet-5-5" in result.output


def _scanned(tmp_path: Path, git_repo: GitRepo) -> str:
    git_repo(
        "a",
        {
            "q.sql": "insert into m.base select c.id_cliente from raw.c c "
            "join raw.p p on c.id_cliente = p.id_cliente"
        },
    )
    map_dir = str(tmp_path / "map")
    runner.invoke(app, ["scan", str(tmp_path / "repos"), "--map-dir", map_dir])
    return map_dir


def test_propose_refine_and_generate(tmp_path: Path, git_repo: GitRepo) -> None:
    map_dir = _scanned(tmp_path, git_repo)
    proposed = runner.invoke(app, ["propose", "m.base", "--plan", "p", "--map-dir", map_dir])
    assert proposed.exit_code == 0
    lines = proposed.output.splitlines()
    fanout = next(line.split()[0] for line in lines if "Unicidade" in line)
    dup = next(line.split()[0] for line in lines if "Duplicidade" in line)
    other = next(line.split()[0] for line in lines if "órfãs" in line)

    shown = runner.invoke(app, ["plan", "show", "p", "--sql", "--map-dir", map_dir])
    assert "COUNT(DISTINCT id_cliente)" in shown.output

    assert (
        runner.invoke(app, ["plan", "accept", "p", fanout, dup, "--map-dir", map_dir]).exit_code
        == 0
    )
    assert runner.invoke(app, ["plan", "reject", "p", other, "--map-dir", map_dir]).exit_code == 0
    generated = runner.invoke(app, ["generate", "p", "--lang", "python", "--map-dir", map_dir])
    assert generated.exit_code == 0
    assert "awswrangler" in generated.output and f"{fanout}.py" in generated.output


def test_generate_blocks_on_missing_params_until_set(tmp_path: Path, git_repo: GitRepo) -> None:
    map_dir = _scanned(tmp_path, git_repo)
    sql = tmp_path / "t.sql"
    sql.write_text("SELECT COUNT(*) FROM ${tabela}")
    added = runner.invoke(
        app, ["plan", "add", "p", "--title", "Meu", "--sql-file", str(sql), "--map-dir", map_dir]
    )
    pid = added.output.strip()

    blocked = runner.invoke(app, ["generate", "p", "--map-dir", map_dir])
    assert blocked.exit_code == 1

    assert (
        runner.invoke(
            app, ["plan", "set", "p", pid, "tabela=m.base", "--map-dir", map_dir]
        ).exit_code
        == 0
    )
    generated = runner.invoke(app, ["generate", "p", "--map-dir", map_dir])
    assert "SELECT COUNT(*) FROM m.base" in generated.output


def test_plan_set_rejects_malformed_params(tmp_path: Path) -> None:
    result = runner.invoke(app, ["plan", "set", "p", "x", "semigual", "--map-dir", str(tmp_path)])
    assert result.exit_code == 2


def test_propose_unknown_term(tmp_path: Path) -> None:
    assert runner.invoke(app, ["propose", "nada", "--map-dir", str(tmp_path)]).exit_code == 1


def _accepted_plan(tmp_path: Path, template: str) -> str:
    map_dir = str(tmp_path / "map")
    sql = tmp_path / "t.sql"
    sql.write_text(template)
    added = runner.invoke(
        app, ["plan", "add", "p", "--title", "T", "--sql-file", str(sql), "--map-dir", map_dir]
    )
    return added.output.strip()


def _fake_aws(monkeypatch: pytest.MonkeyPatch, outcomes: list[object]) -> object:
    from factories import FakeExecutor

    from dbts.cli import app as cli_module

    executor = FakeExecutor(outcomes)
    monkeypatch.setattr(cli_module, "_executor", lambda *_: executor)
    return executor


ANALYSIS = '{"status": "aprovado", "analise": "Sem duplicidade.", "conclusao": "Aprovado."}'


def _fake_llm(monkeypatch: pytest.MonkeyPatch, *responses: str) -> None:
    from dbts.adapters.fake_llm import FakeLLMProvider
    from dbts.cli import app as cli_module

    llm = FakeLLMProvider(list(responses))
    monkeypatch.setattr(cli_module, "_llm", lambda _: llm)


def test_run_confirms_executes_and_stores(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from factories import query_result

    _accepted_plan(tmp_path, "SELECT 1")
    _fake_aws(monkeypatch, [query_result()])
    map_dir = str(tmp_path / "map")

    _fake_llm(monkeypatch, ANALYSIS)
    skipped = runner.invoke(app, ["run", "p", "--map-dir", map_dir], input="n\n")
    ran = runner.invoke(app, ["run", "p", "--map-dir", map_dir], input="y\n")

    assert skipped.exit_code == 0 and "ok:" not in skipped.output
    assert ran.exit_code == 0, ran.output
    assert "ok: 1 linhas" in ran.output
    assert list((tmp_path / "map" / "queries").glob("*.sql"))
    report = next((tmp_path / "map" / "reports" / "p").glob("*.md")).read_text()
    assert "## 7. Conclusões\n\nAprovado." in report


def test_run_auto_fix_with_llm_updates_plan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from factories import query_result

    from dbts.adapters.fake_llm import FakeLLMProvider
    from dbts.cli import app as cli_module
    from dbts.domain.execution import QueryFailedError

    pid = _accepted_plan(tmp_path, "SELECT a FROM t")
    _fake_aws(monkeypatch, [QueryFailedError("COLUMN_NOT_FOUND"), query_result()])
    fix = '{"sql": "SELECT b FROM t", "explicacao": "troca a por b"}'
    monkeypatch.setattr(cli_module, "_llm", lambda _: FakeLLMProvider([fix]))
    map_dir = str(tmp_path / "map")

    args = ["run", "p", pid, "--yes", "--no-analysis", "--map-dir", map_dir]
    result = runner.invoke(app, args, input="a\ny\n")

    assert result.exit_code == 0, result.output
    assert "troca a por b" in result.output
    shown = runner.invoke(app, ["plan", "show", "p", "--sql", "--map-dir", map_dir])
    assert "SELECT b FROM t" in shown.output


def test_run_manual_edit_and_skip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from factories import query_result

    from dbts.cli import app as cli_module
    from dbts.domain.execution import QueryFailedError

    _accepted_plan(tmp_path, "SELECT a FROM t")
    _fake_aws(monkeypatch, [QueryFailedError("e1"), query_result(), QueryFailedError("e2")])
    edits = iter(["SELECT ok FROM t", None])
    monkeypatch.setattr(cli_module, "_edit", lambda _: next(edits))
    map_dir = str(tmp_path / "map")

    args = ["run", "p", "--yes", "--no-analysis", "--map-dir", map_dir]
    edited = runner.invoke(app, args, input="m\n")
    assert edited.exit_code == 0, edited.output

    failed = runner.invoke(app, args, input="m\n")
    assert failed.exit_code == 1


def test_run_llm_fix_declined_and_skip_choice(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from dbts.adapters.fake_llm import FakeLLMProvider
    from dbts.cli import app as cli_module
    from dbts.domain.execution import QueryFailedError

    _accepted_plan(tmp_path, "SELECT a FROM t")
    _fake_aws(monkeypatch, [QueryFailedError("e1"), QueryFailedError("e2")])
    fix = '{"sql": "SELECT b FROM t", "explicacao": "x"}'
    monkeypatch.setattr(cli_module, "_llm", lambda _: FakeLLMProvider([fix]))
    map_dir = str(tmp_path / "map")

    args = ["run", "p", "--yes", "--no-analysis", "--map-dir", map_dir]
    declined = runner.invoke(app, args, input="a\nn\n")
    skipped = runner.invoke(app, args, input="p\n")

    assert declined.exit_code == 1 and skipped.exit_code == 1


def test_edit_uses_editor(monkeypatch: pytest.MonkeyPatch) -> None:
    from dbts.cli.app import _edit

    monkeypatch.setenv("EDITOR", "sed -i s/a/b/")
    assert _edit("SELECT a") == "SELECT b"
    monkeypatch.setenv("EDITOR", "true")
    assert _edit("SELECT a") is None


def test_default_executor_is_athena() -> None:
    from dbts.adapters.athena import AthenaExecutor
    from dbts.cli.app import _executor

    assert isinstance(_executor("db", "wg", None, "us-east-1"), AthenaExecutor)


def test_run_with_parquet_and_table_sinks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from factories import query_result

    _accepted_plan(tmp_path, "SELECT 1")
    executor = _fake_aws(monkeypatch, [query_result(), query_result()])
    _fake_llm(monkeypatch)
    args = ["run", "p", "--yes", "--no-analysis", "--sandbox", "sb", "--sink", "parquet"]
    result = runner.invoke(
        app, [*args, "--sink", "table", "--sink", "table", "--map-dir", str(tmp_path / "map")]
    )
    assert result.exit_code == 0, result.output
    assert "parquet: " in result.output and "table: sb.dbts_" in result.output
    assert executor.received[1].startswith("CREATE TABLE sb.dbts_")  # type: ignore[attr-defined]


def test_report_command_rebuilds_from_latest_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from factories import query_result

    pid = _accepted_plan(tmp_path, "SELECT 1")
    _fake_aws(monkeypatch, [query_result()])
    _fake_llm(monkeypatch, ANALYSIS)
    map_dir = str(tmp_path / "map")
    runner.invoke(app, ["run", "p", "--yes", "--no-analysis", "--map-dir", map_dir])

    result = runner.invoke(app, ["report", "p", pid, "--map-dir", map_dir])

    assert result.exit_code == 0, result.output
    report = Path(result.output.strip()).read_text()
    assert "Sem duplicidade." in report and "SELECT 1" in report


def test_report_command_without_csv_run(tmp_path: Path) -> None:
    result = runner.invoke(app, ["report", "p", "x", "--map-dir", str(tmp_path)])
    assert result.exit_code == 1


def test_mcp_command_starts_stdio_server(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from dbts.cli import app as cli_module

    calls: list[str] = []

    class FakeServer:
        def run(self, transport: str) -> None:
            calls.append(transport)

    monkeypatch.setattr(cli_module, "build_server", lambda settings: FakeServer())
    assert runner.invoke(app, ["mcp", "--map-dir", str(tmp_path)]).exit_code == 0
    assert calls == ["stdio"]


def test_local_db_selects_duckdb_executor(tmp_path: Path) -> None:
    from dbts.adapters.duckdb_executor import DuckDBExecutor
    from dbts.cli.app import _executor

    assert isinstance(_executor("db", "wg", None, None, tmp_path / "l.duckdb"), DuckDBExecutor)
