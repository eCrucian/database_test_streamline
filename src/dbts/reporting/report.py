"""Relatório formal de um teste executado: estrutura fixa; o LLM só redige análise e conclusão."""

import csv
from collections.abc import Callable
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import ClassVar

from jinja2 import Environment, PackageLoader, StrictUndefined
from pydantic import BaseModel, ConfigDict, Field

from dbts.audit.log import AuditEvent, AuditLog
from dbts.domain.models import Origin
from dbts.domain.testing import TestPlan, TestProposal
from dbts.execution.library import RunRecord
from dbts.mapping.guide import slugify
from dbts.ports import LLMProvider

PREVIEW_ROWS = 20

PROMPT = """Você é um validador de modelos redigindo a análise de um teste de dados.
Use APENAS as informações abaixo. Não invente números que não aparecem no resultado.

TESTE: {title}
DESCRIÇÃO: {description}
CRITÉRIO DE INTERPRETAÇÃO: {criterio}
SQL EXECUTADO:
{sql}
RESULTADO ({rows} linhas; primeiras {shown}):
{table}

Responda em JSON com:
- status: aprovado (critério atendido), reprovado (critério violado) ou inconclusivo;
- analise: 2 a 4 frases formais interpretando o resultado à luz do critério;
- conclusao: 1 a 2 frases com a conclusão e, se couber, a recomendação.
"""


class Verdict(StrEnum):
    APPROVED = "aprovado"
    REJECTED = "reprovado"
    INCONCLUSIVE = "inconclusivo"


class ReportAnalysis(BaseModel):
    status: Verdict
    analise: str = Field(description="2 a 4 frases formais interpretando o resultado.")
    conclusao: str = Field(description="1 a 2 frases com conclusão e recomendação.")


class TestReport(BaseModel):
    __test__: ClassVar[bool] = False  # não é classe de teste do pytest
    model_config = ConfigDict(frozen=True)

    plan: str
    proposal: TestProposal
    run: RunRecord
    sql: str
    columns: list[str]
    preview: list[list[str | None]]
    analysis: ReportAnalysis | None = None
    analysis_model: str | None = None
    generated_at: datetime


def _table(columns: list[str], rows: list[list[str | None]]) -> str:
    lines = [" | ".join(columns), *(" | ".join(v or "NULL" for v in row) for row in rows)]
    return "\n".join(lines)


class Analyst:
    def __init__(self, llm: LLMProvider, audit: AuditLog, user: str) -> None:
        self._llm = llm
        self._audit = audit
        self._user = user

    @property
    def model(self) -> str:
        return f"{self._llm.name}/{self._llm.model}"

    def analyze(self, report: TestReport) -> ReportAnalysis:
        prompt = PROMPT.format(
            title=report.proposal.title,
            description=report.proposal.description,
            criterio=report.proposal.criterio,
            sql=report.sql,
            rows=report.run.rows,
            shown=len(report.preview),
            table=_table(report.columns, report.preview),
        )
        analysis = self._llm.complete(prompt, ReportAnalysis)
        self._audit.append(
            AuditEvent(
                action="analyze",
                user=self._user,
                origin=Origin.LLM,
                query_hash=report.run.query_hash,
                llm_provider=self._llm.name,
                llm_model=self._llm.model,
                decision=analysis.status,
                detail=f"plan={report.plan} proposal={report.proposal.id}",
            )
        )
        return analysis


def _now() -> datetime:
    return datetime.now(UTC)


def build_report(
    proposal: TestProposal,
    plan: TestPlan,
    run: RunRecord,
    sql: str,
    result: tuple[list[str], list[list[str | None]]],
    analyst: Analyst | None = None,
    clock: Callable[[], datetime] = _now,
) -> TestReport:
    columns, rows = result
    report = TestReport(
        plan=plan.name,
        proposal=proposal,
        run=run,
        sql=sql.strip(),
        columns=columns,
        preview=rows[:PREVIEW_ROWS],
        generated_at=clock(),
    )
    if analyst is None:
        return report
    return report.model_copy(
        update={"analysis": analyst.analyze(report), "analysis_model": analyst.model}
    )


def load_csv(path: Path) -> tuple[list[str], list[list[str | None]]]:
    """Lê um resultado gravado pelo CsvSink (NULL e vazio ficam indistintos no CSV)."""
    with path.open(newline="", encoding="utf-8") as handle:
        rows: list[list[str | None]] = [list(row) for row in csv.reader(handle)]
    header = [value or "" for value in rows[0]] if rows else []
    return header, rows[1:]


def strip_header(query_file_text: str) -> str:
    """SQL de um arquivo da biblioteca, sem o cabeçalho de comentários."""
    lines = query_file_text.splitlines()
    first = next((i for i, line in enumerate(lines) if not line.startswith("--")), len(lines))
    return "\n".join(lines[first:]).strip()


def _cell(value: str | None) -> str:
    return "NULL" if value is None else value.replace("|", "\\|")


# Gera Markdown, não HTML: autoescape HTML corromperia o texto.
_ENV = Environment(  # nosec B701
    loader=PackageLoader("dbts.reporting", "templates"),
    undefined=StrictUndefined,
    keep_trailing_newline=True,
    autoescape=False,  # Markdown, não HTML
)
_ENV.filters["cell"] = _cell


def render_report(report: TestReport) -> str:
    return _ENV.get_template("report.md.j2").render(r=report, p=report.proposal, run=report.run)


class ReportWriter:
    def __init__(self, directory: Path, audit: AuditLog, user: str) -> None:
        self._dir = directory
        self._audit = audit
        self._user = user

    def write(self, report: TestReport) -> Path:
        name = f"{report.proposal.id}-{report.run.execution_id}.md"
        path = self._dir / slugify(report.plan) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_report(report), encoding="utf-8")
        self._audit.append(
            AuditEvent(
                action="report",
                user=self._user,
                origin=Origin.PARSER,
                query_hash=report.run.query_hash,
                detail=f"plan={report.plan} proposal={report.proposal.id} path={path}",
            )
        )
        return path
