import pytest
from factories import FakeExecutor, query_result

from dbts.domain.execution import QueryFailedError
from dbts.execution.repair import RepairFailedError, run_with_repair


def test_success_first_try() -> None:
    outcome = run_with_repair("q", FakeExecutor([query_result()]).execute, lambda *_: None, 3)
    assert outcome.sql == "q" and outcome.attempts == ()


def test_fixes_until_success_and_keeps_history() -> None:
    executor = FakeExecutor([QueryFailedError("e1"), QueryFailedError("e2"), query_result()])
    calls: list[tuple[str, str, int]] = []

    def decide(sql: str, error: str, attempt: int) -> tuple[str, str]:
        calls.append((sql, error, attempt))
        return f"{sql}+", "llm"

    outcome = run_with_repair("q", executor.execute, decide, 3)
    assert outcome.sql == "q++"
    assert calls == [("q", "e1", 1), ("q+", "e2", 2)]
    assert [(a.sql, a.error, a.fixed_by) for a in outcome.attempts] == [
        ("q", "e1", "llm"),
        ("q+", "e2", "llm"),
    ]


def test_abandon() -> None:
    executor = FakeExecutor([QueryFailedError("boom")])
    with pytest.raises(RepairFailedError) as error:
        run_with_repair("q", executor.execute, lambda *_: None, 3)
    assert error.value.reason == "execução abandonada"
    assert "boom" in str(error.value)


def test_limit_of_fixes() -> None:
    executor = FakeExecutor([QueryFailedError("e1"), QueryFailedError("e2")])
    with pytest.raises(RepairFailedError) as error:
        run_with_repair("q", executor.execute, lambda sql, *_: (sql + "!", "usuario"), 1)
    assert error.value.reason == "limite de correções atingido"
    assert [a.error for a in error.value.attempts] == ["e1", "e2"]
