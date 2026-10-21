from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from dbts.audit.log import AuditEvent, AuditLog
from dbts.domain.execution import QueryFailedError, QueryResult
from dbts.domain.models import Origin
from dbts.domain.testing import TestPlan, TestProposal
from dbts.execution.library import QueryLibrary, RunRecord
from dbts.execution.repair import Decide, RepairFailedError, RepairOutcome, run_with_repair
from dbts.execution.sql import ensure_safe
from dbts.ports import QueryExecutor, ResultSink
from dbts.testing.codegen import header_lines


@dataclass(frozen=True)
class RunResult:
    query_path: Path
    record: RunRecord
    outcome: RepairOutcome


def _now() -> datetime:
    return datetime.now(UTC)


def _execution_lines(outcome: RepairOutcome, executed_at: datetime) -> list[str]:
    fixes = [
        f"  {i}. erro: {a.error.splitlines()[0][:160]} | corrigido por: {a.fixed_by}"
        for i, a in enumerate(outcome.attempts, start=1)
    ]
    return [
        f"Executado em: {executed_at.isoformat()} | Execução: {outcome.result.execution_id}",
        f"Linhas: {len(outcome.result.rows)} | Bytes escaneados: {outcome.result.bytes_scanned}",
        f"Correções até executar: {len(fixes)}",
        *fixes,
    ]


def _write(sink: ResultSink, digest: str, outcome: RepairOutcome) -> str:
    """Falha em um destino não invalida a execução já feita: vira registro de erro."""
    try:
        return sink.write(digest, outcome.sql, outcome.result)
    except QueryFailedError as error:
        return f"erro: {error}"


class TestRunner:
    """Executa uma proposta com guarda, loop de correção, biblioteca e auditoria."""

    __test__ = False  # não é classe de teste do pytest

    def __init__(
        self,
        executor: QueryExecutor,
        library: QueryLibrary,
        audit: AuditLog,
        user: str,
        sandbox: str,
        sinks: Sequence[ResultSink],
        max_fixes: int = 3,
        clock: Callable[[], datetime] = _now,
    ) -> None:
        self._executor = executor
        self._library = library
        self._audit = audit
        self._user = user
        self._sandbox = sandbox
        self._sinks = sinks
        self._max_fixes = max_fixes
        self._clock = clock

    def run(self, proposal: TestProposal, plan: TestPlan, decide: Decide) -> RunResult:
        try:
            outcome = run_with_repair(proposal.render(), self._guarded, decide, self._max_fixes)
        except RepairFailedError as error:
            self._record(proposal, plan, decision="falhou", detail=str(error))
            raise
        executed_at = self._clock()
        header = header_lines(proposal, plan) + _execution_lines(outcome, executed_at)
        digest, query_path = self._library.save_query(outcome.sql, header)
        results = {sink.name: _write(sink, digest, outcome) for sink in self._sinks}
        record = RunRecord(
            query_hash=digest,
            plan=plan.name,
            proposal_id=proposal.id,
            execution_id=outcome.result.execution_id,
            executed_at=executed_at,
            bytes_scanned=outcome.result.bytes_scanned,
            rows=len(outcome.result.rows),
            fixes=len(outcome.attempts),
            query_path=str(query_path),
            results=results,
        )
        self._library.record(record)
        detail = f"rows={len(outcome.result.rows)} bytes={outcome.result.bytes_scanned}"
        self._record(proposal, plan, decision="sucesso", detail=detail, query_hash=digest)
        return RunResult(query_path, record, outcome)

    def _guarded(self, sql: str) -> QueryResult:
        ensure_safe(sql, self._sandbox)
        return self._executor.execute(sql)

    def _record(
        self,
        proposal: TestProposal,
        plan: TestPlan,
        decision: str,
        detail: str,
        query_hash: str | None = None,
    ) -> None:
        self._audit.append(
            AuditEvent(
                action="execute",
                user=self._user,
                origin=Origin.USER,
                query_hash=query_hash,
                decision=decision,
                detail=f"plan={plan.name} proposal={proposal.id} {detail}",
            )
        )
