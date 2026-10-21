from datetime import UTC, datetime
from pathlib import Path

from factories import query_result

from dbts.adapters.fake_llm import FakeLLMProvider
from dbts.audit.log import AuditLog
from dbts.domain.models import Origin, SourceLocation
from dbts.domain.testing import Severity, TestPlan, TestProposal
from dbts.execution.library import RunRecord
from dbts.reporting.report import (
    PREVIEW_ROWS,
    Analyst,
    ReportWriter,
    Verdict,
    build_report,
    load_csv,
    render_report,
    strip_header,
)

NOW = datetime(2026, 10, 20, 12, tzinfo=UTC)
ANALYSIS = '{"status": "reprovado", "analise": "Há duplicidade.", "conclusao": "Corrigir a chave."}'


def _proposal(evidence: bool = True) -> TestProposal:
    return TestProposal(
        id="p1",
        hypothesis_id="duplicate-keys",
        title="Duplicidade de id",
        description="Desc.",
        severity=Severity.MEDIUM,
        criterio="Resultado vazio.",
        template="SELECT 1",
        params={"table": "db.t", "column": "id"} if evidence else {},
        evidence=[SourceLocation(repo="r", path="a.sql", line=3, commit_sha="abcdef123")]
        if evidence
        else [],
        origin=Origin.PARSER if evidence else Origin.USER,
    )


def _run(rows: int = 2) -> RunRecord:
    return RunRecord(
        query_hash="h" * 64,
        plan="Plano X",
        proposal_id="p1",
        execution_id="exec-1",
        executed_at=NOW,
        bytes_scanned=1024,
        rows=rows,
        fixes=1,
        query_path="q.sql",
        results={"csv": "r.csv"},
    )


def _result(rows: int = 2) -> tuple[list[str], list[list[str | None]]]:
    result = query_result(rows)
    return result.columns, [["a|b", None], *result.rows[1:]]


def test_report_without_analysis_has_all_sections_in_order() -> None:
    report = build_report(
        _proposal(), TestPlan(name="Plano X"), _run(), "SELECT 1\n", _result(), clock=lambda: NOW
    )
    md = render_report(report)
    headings = [line for line in md.splitlines() if line.startswith("## ")]
    assert headings == [
        "## 1. O que é",
        "## 2. Por que foi feito",
        "## 3. O que se quis testar",
        "## 4. Como foi desenhado",
        "## 5. Resultados",
        "## 6. Análise",
        "## 7. Conclusões",
    ]
    assert md.startswith("# Relatório de Teste — Duplicidade de id")
    assert "| Status | pendente de análise |" in md
    assert "- `r/a.sql:3` (commit `abcdef12`)" in md
    assert "- `column` = `id`\n- `table` = `db.t`" in md
    assert "```sql\nSELECT 1\n```" in md
    assert "| a | b |\n|---|---|\n| a\\|b | NULL | \n| 1 | NULL | " in md
    assert "- Resultado (csv): `r.csv`" in md
    assert "_Pendente de análise do validador._" in md
    assert md.endswith("_Pendente de conclusão do validador._\n")


def test_report_with_llm_analysis_is_marked_and_audited(tmp_path: Path) -> None:
    audit = AuditLog(tmp_path)
    llm = FakeLLMProvider([ANALYSIS])
    report = build_report(
        _proposal(),
        TestPlan(name="Plano X"),
        _run(),
        "SELECT 1",
        _result(),
        Analyst(llm, audit, "u"),
    )
    assert report.analysis is not None and report.analysis.status is Verdict.REJECTED
    assert "CRITÉRIO DE INTERPRETAÇÃO: Resultado vazio." in llm.prompts[0]
    assert "a | b\na|b | NULL" in llm.prompts[0]
    md = render_report(report)
    assert "| Status | reprovado |" in md
    assert "Há duplicidade.\n\n> Texto redigido por LLM (`fake/fake-model`)" in md
    assert md.endswith("Corrigir a chave.\n")
    (record,) = audit.records()
    assert (record.action, record.decision) == ("analyze", "reprovado")


def test_custom_test_without_evidence_params_or_columns() -> None:
    report = build_report(
        _proposal(evidence=False), TestPlan(name="p"), _run(0), "SELECT 1", ([], [])
    )
    md = render_report(report)
    assert "Teste proposto diretamente pelo validador" in md
    assert "Parâmetros:" not in md
    results = md.split("## 5. Resultados")[1].split("## 6.")[0]
    assert "|---|" not in results


def test_preview_is_truncated() -> None:
    total = PREVIEW_ROWS + 5
    report = build_report(
        _proposal(), TestPlan(name="p"), _run(total), "SELECT 1", (["a"], [["x"]] * total)
    )
    assert len(report.preview) == PREVIEW_ROWS
    assert f"_Exibidas {PREVIEW_ROWS} de {total} linhas._" in render_report(report)


def test_writer_paths_and_audit(tmp_path: Path) -> None:
    audit = AuditLog(tmp_path / "audit")
    report = build_report(_proposal(), TestPlan(name="Plano X"), _run(), "SELECT 1", _result())
    path = ReportWriter(tmp_path / "reports", audit, "u").write(report)
    assert path == tmp_path / "reports" / "plano-x" / "p1-exec-1.md"
    assert next(audit.records()).action == "report"


def test_load_csv_and_strip_header(tmp_path: Path) -> None:
    csv_path = tmp_path / "r.csv"
    csv_path.write_text("a,b\n1,\n")
    assert load_csv(csv_path) == (["a", "b"], [["1", ""]])
    empty = tmp_path / "e.csv"
    empty.write_text("")
    assert load_csv(empty) == ([], [])
    assert strip_header("-- a\n-- b\nSELECT 1\n-- fim\n") == "SELECT 1\n-- fim"
    assert strip_header("-- só cabeçalho") == ""
