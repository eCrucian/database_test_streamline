from collections.abc import Callable
from dataclasses import dataclass

from dbts.domain.execution import Attempt, QueryFailedError, QueryResult

Decide = Callable[[str, str, int], tuple[str, str] | None]
"""(sql que falhou, erro, nº da tentativa) -> (novo sql, quem corrigiu) ou None para desistir."""


@dataclass(frozen=True)
class RepairOutcome:
    sql: str
    result: QueryResult
    attempts: tuple[Attempt, ...]


class RepairFailedError(QueryFailedError):
    def __init__(self, attempts: list[Attempt], reason: str) -> None:
        super().__init__(f"{reason} após {len(attempts)} falha(s): {attempts[-1].error}")
        self.attempts = attempts
        self.reason = reason


def run_with_repair(
    sql: str, execute: Callable[[str], QueryResult], decide: Decide, max_fixes: int
) -> RepairOutcome:
    """Executa; a cada falha pede uma correção a `decide`, até `max_fixes` correções."""
    attempts: list[Attempt] = []
    current = sql
    while True:
        try:
            return RepairOutcome(current, execute(current), tuple(attempts))
        except QueryFailedError as error:
            if len(attempts) >= max_fixes:
                attempts.append(Attempt(sql=current, error=str(error)))
                raise RepairFailedError(attempts, "limite de correções atingido") from error
            decision = decide(current, str(error), len(attempts) + 1)
            fixed_by = decision[1] if decision else None
            attempts.append(Attempt(sql=current, error=str(error), fixed_by=fixed_by))
            if decision is None:
                raise RepairFailedError(attempts, "execução abandonada") from error
            current = decision[0]
