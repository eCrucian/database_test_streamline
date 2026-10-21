"""Código dos testes aceitos, com cabeçalho que descreve o teste e a evidência no código."""

from collections.abc import Mapping
from enum import StrEnum

from dbts.domain.testing import ProposalStatus, TestPlan, TestProposal


class Language(StrEnum):
    SQL = "sql"
    PYTHON = "python"


class MissingParamsError(ValueError):
    def __init__(self, missing: Mapping[str, list[str]]) -> None:
        detail = "; ".join(f"{pid}: {', '.join(names)}" for pid, names in missing.items())
        super().__init__(f"parâmetros faltando ({detail})")
        self.missing = dict(missing)


def header_lines(proposal: TestProposal, plan: TestPlan) -> list[str]:
    params = ", ".join(f"{k}={v}" for k, v in sorted(proposal.params.items())) or "—"
    evidence = [f"  {e.repo}/{e.path}:{e.line} @ {e.commit_sha[:8]}" for e in proposal.evidence]
    return [
        f"Teste: {proposal.title}",
        f"Id: {proposal.id} | Hipótese: {proposal.hypothesis_id} | Severidade: {proposal.severity}",
        f"Origem: {proposal.origin} | Plano: {plan.name}",
        f"Descrição: {proposal.description}",
        f"Critério: {proposal.criterio}",
        f"Parâmetros: {params}",
        "Evidência no código:",
        *(evidence or ["  —"]),
    ]


def _sql(proposal: TestProposal, plan: TestPlan) -> str:
    rule = "-- " + "=" * 76
    header = [rule, *(f"-- {line}" for line in header_lines(proposal, plan)), rule]
    return "\n".join([*header, proposal.render(), ""])


def _python(proposal: TestProposal, plan: TestPlan) -> str:
    docstring = "\n".join(header_lines(proposal, plan))
    sql = proposal.render().replace('"""', '\\"\\"\\"')
    return f'''"""{docstring}
"""

import sys

import awswrangler as wr

SQL = """
{sql}
"""


def run(database: str, workgroup: str = "primary"):
    return wr.athena.read_sql_query(SQL, database=database, workgroup=workgroup)


if __name__ == "__main__":
    print(run(sys.argv[1]))
'''


def generate(plan: TestPlan, language: Language) -> dict[str, str]:
    """Código por id de proposta aceita. Falha se alguma tiver parâmetros faltando."""
    accepted = [p for p in plan.proposals if p.status is ProposalStatus.ACCEPTED]
    missing = {p.id: p.missing for p in accepted if p.missing}
    if missing:
        raise MissingParamsError(missing)
    render = _sql if language is Language.SQL else _python
    return {p.id: render(p, plan) for p in accepted}
