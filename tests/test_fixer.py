from pathlib import Path

from dbts.adapters.fake_llm import FakeLLMProvider
from dbts.audit.log import AuditLog
from dbts.domain.models import Origin
from dbts.execution.fixer import SqlFixer


def test_fix_prompts_with_error_and_sql_and_audits(tmp_path: Path) -> None:
    llm = FakeLLMProvider(['{"sql": "SELECT b FROM t", "explicacao": "coluna a não existe"}'])
    audit = AuditLog(tmp_path)
    fix = SqlFixer(llm, audit, "u").fix("SELECT a FROM t", "COLUMN_NOT_FOUND: a")
    assert fix.sql == "SELECT b FROM t"
    assert "COLUMN_NOT_FOUND: a" in llm.prompts[0] and "SELECT a FROM t" in llm.prompts[0]
    (record,) = audit.records()
    assert (record.action, record.origin, record.detail) == (
        "fix",
        Origin.LLM,
        "coluna a não existe",
    )
