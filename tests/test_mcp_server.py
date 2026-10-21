import asyncio
from pathlib import Path
from typing import Any

import pytest
from conftest import GitRepo
from factories import FakeExecutor, query_result

from dbts.config import resolve_settings
from dbts.domain.execution import QueryFailedError
from dbts.domain.testing import ProposalStatus
from dbts.mcp_server import TOOL_NAMES, DbtsTools, build_server
from dbts.testing.codegen import Language

SQL = (
    "insert into m.base select c.id_cliente from raw.c c "
    "join raw.p p on c.id_cliente = p.id_cliente"
)


def _tools(tmp_path: Path, executor: FakeExecutor | None = None) -> DbtsTools:
    settings = resolve_settings({}, tmp_path, tmp_path / "map")
    fake = executor or FakeExecutor([])
    return DbtsTools(settings, lambda database, workgroup: fake)


def _scanned(tmp_path: Path, git_repo: GitRepo, executor: FakeExecutor | None = None) -> DbtsTools:
    git_repo("a", {"q.sql": SQL})
    tools = _tools(tmp_path, executor)
    tools.scan(str(tmp_path / "repos"))
    return tools


def test_server_registers_all_tools(tmp_path: Path) -> None:
    server = build_server(resolve_settings({}, tmp_path))
    names = [tool.name for tool in asyncio.run(server.list_tools())]
    assert names == list(TOOL_NAMES)


def test_tool_call_over_protocol(tmp_path: Path, git_repo: GitRepo) -> None:
    git_repo("a", {"q.sql": SQL})
    server = build_server(resolve_settings({}, tmp_path, tmp_path / "map"))
    result: Any = asyncio.run(server.call_tool("scan", {"root": str(tmp_path / "repos")}))
    assert not result.is_error
    assert result.structured_content["result"][0]["repo"] == "a"


def test_scan_guide_and_lineage(tmp_path: Path, git_repo: GitRepo) -> None:
    tools = _scanned(tmp_path, git_repo)
    assert tools.scan(str(tmp_path / "repos"))[0]["changed"] == 0
    assert "### `m.base`" in tools.guide("m.base")
    assert '"title": "mapa-completo"' in tools.lineage_json()
    with pytest.raises(ValueError, match="nenhuma entidade"):
        tools.guide("nada")
    with pytest.raises(ValueError, match="nenhuma entidade"):
        tools.lineage_json("nada")


def test_plan_refinement_and_generation(tmp_path: Path, git_repo: GitRepo) -> None:
    tools = _scanned(tmp_path, git_repo)
    proposals = tools.propose("m.base", plan="p")
    dup = next(p["id"] for p in proposals if p["title"].startswith("Duplicidade"))
    tools.set_status("p", [dup], ProposalStatus.ACCEPTED)
    detail = tools.set_params("p", dup, {"extra": "1"})
    assert detail["params"]["extra"] == "1" and "evidence" in detail
    assert tools.set_sql("p", dup, "SELECT 1")["sql"] == "SELECT 1"
    custom = tools.add_test("p", "Meu", "SELECT 2", "desc")
    assert custom["status"] == ProposalStatus.ACCEPTED
    code = tools.generate("p", Language.PYTHON)
    assert len(code) == 2 and all(path.endswith(".py") for path in code)
    assert len(tools.show_plan("p")) == len(proposals) + 1


def test_run_test_requires_confirmation_then_runs(tmp_path: Path, git_repo: GitRepo) -> None:
    executor = FakeExecutor([query_result(25)])
    tools = _scanned(tmp_path, git_repo, executor)
    pid = tools.add_test("p", "T", "SELECT 1")["id"]

    pending = tools.run_test("p", pid, "db", "wg", "sb")
    assert pending == {"status": "confirmacao_necessaria", "sql": "SELECT 1"}
    assert executor.received == []

    done = tools.run_test("p", pid, "db", "wg", "sb", confirm=True)
    assert done["status"] == "ok"
    assert (done["total_rows"], len(done["rows"])) == (25, 20)
    assert Path(done["report_path"]).exists()
    assert tools.list_runs("p")[0]["proposal_id"] == pid
    assert tools.list_runs("outro") == []
    assert tools.audit_verify() == {"integra": True, "registro_adulterado": None}


def test_run_test_error_is_returned_for_client_to_fix(tmp_path: Path, git_repo: GitRepo) -> None:
    executor = FakeExecutor([QueryFailedError("COLUMN_NOT_FOUND")])
    tools = _scanned(tmp_path, git_repo, executor)
    pid = tools.add_test("p", "T", "SELECT a FROM t")["id"]
    result = tools.run_test("p", pid, "db", "wg", "sb", confirm=True)
    assert result["status"] == "erro" and "COLUMN_NOT_FOUND" in result["erro"]
    assert result["sql"] == "SELECT a FROM t"


def test_default_executor_factory_builds_athena(monkeypatch: pytest.MonkeyPatch) -> None:
    from dbts.adapters.athena import AthenaExecutor
    from dbts.mcp_server import _athena

    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    assert isinstance(_athena("db", "wg"), AthenaExecutor)
