from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from factories import FakeExecutor, query_result

from dbts.adapters.sinks import CsvSink
from dbts.audit.log import AuditLog
from dbts.domain.execution import QueryFailedError
from dbts.domain.models import SourceLocation
from dbts.domain.testing import Severity, TestPlan, TestProposal
from dbts.execution.library import QueryLibrary
from dbts.execution.repair import RepairFailedError
from dbts.execution.runner import TestRunner

NOW = datetime(2026, 10, 20, 12, tzinfo=UTC)


def _proposal(template: str = "SELECT a FROM ${table}") -> TestProposal:
    return TestProposal(
        id="p1",
        hypothesis_id="h",
        title="Teste X",
        description="d",
        severity=Severity.HIGH,
        criterio="c",
        template=template,
        params={"table": "db.t"},
        evidence=[SourceLocation(repo="r", path="a.sql", line=1, commit_sha="abc")],
    )


def _runner(tmp_path: Path, executor: FakeExecutor) -> tuple[TestRunner, AuditLog, QueryLibrary]:
    audit, library = AuditLog(tmp_path / "audit"), QueryLibrary(tmp_path / "queries")
    sinks = [CsvSink(tmp_path / "results")]
    runner = TestRunner(
        executor, library, audit, "u", "sandbox", sinks, max_fixes=2, clock=lambda: NOW
    )
    return runner, audit, library


def test_run_saves_fixed_query_result_index_and_audit(tmp_path: Path) -> None:
    executor = FakeExecutor([QueryFailedError("COLUMN_NOT_FOUND: a\nlinha 2"), query_result()])
    runner, audit, library = _runner(tmp_path, executor)
    plan = TestPlan(name="plano")

    result = runner.run(_proposal(), plan, lambda sql, err, n: ("SELECT b FROM db.t", "llm"))

    assert executor.received == ["SELECT a FROM db.t", "SELECT b FROM db.t"]
    text = result.query_path.read_text()
    assert "-- Teste: Teste X" in text
    assert "-- Correções até executar: 1" in text
    assert "--   1. erro: COLUMN_NOT_FOUND: a | corrigido por: llm" in text
    assert f"-- Executado em: {NOW.isoformat()} | Execução: exec-1" in text
    assert text.endswith("SELECT b FROM db.t\n")
    assert Path(result.record.results["csv"]).exists()
    (run,) = library.runs()
    assert run == result.record
    assert (run.fixes, run.rows) == (1, 1)
    (record,) = audit.records()
    assert (record.action, record.decision, record.query_hash) == (
        "execute",
        "sucesso",
        result.record.query_hash,
    )


def test_guard_blocks_before_aws_and_feeds_repair(tmp_path: Path) -> None:
    executor = FakeExecutor([query_result()])
    runner, _, _ = _runner(tmp_path, executor)
    decisions: list[str] = []

    def decide(sql: str, error: str, attempt: int) -> tuple[str, str]:
        decisions.append(error)
        return "SELECT 1", "usuario"

    runner.run(_proposal("DROP TABLE ${table}"), TestPlan(name="p"), decide)
    assert executor.received == ["SELECT 1"]
    assert "apenas SELECT" in decisions[0]


def test_failure_is_audited_and_raised(tmp_path: Path) -> None:
    runner, audit, library = _runner(tmp_path, FakeExecutor([QueryFailedError("x")]))
    with pytest.raises(RepairFailedError):
        runner.run(_proposal(), TestPlan(name="p"), lambda *_: None)
    (record,) = audit.records()
    assert record.decision == "falhou"
    assert library.runs() == []


def test_default_clock_is_utc(tmp_path: Path) -> None:
    library = QueryLibrary(tmp_path)
    runner = TestRunner(FakeExecutor([query_result()]), library, AuditLog(tmp_path), "u", "s", [])
    runner.run(_proposal(), TestPlan(name="p"), lambda *_: None)
    assert library.runs()[0].executed_at.utcoffset() == timedelta(0)


class _BrokenSink:
    name = "table"

    def write(self, digest: str, sql: str, result: object) -> str:
        raise QueryFailedError("sem permissão")


def test_sink_failure_is_recorded_without_losing_run(tmp_path: Path) -> None:
    library = QueryLibrary(tmp_path)
    executor = FakeExecutor([query_result()])
    runner = TestRunner(executor, library, AuditLog(tmp_path), "u", "s", [_BrokenSink()])
    result = runner.run(_proposal(), TestPlan(name="p"), lambda *_: None)
    assert result.record.results == {"table": "erro: sem permissão"}
    assert library.runs() == [result.record]
