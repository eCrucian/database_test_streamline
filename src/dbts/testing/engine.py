import tomllib
from importlib import resources
from string import Template

from dbts.domain.testing import Hypothesis, TestPlan, TestProposal, proposal_id
from dbts.mapping.graph import Graph
from dbts.testing.matchers import MATCHERS, Match


def load_catalog() -> list[Hypothesis]:
    """Hipóteses em `testing/catalog/*.toml`, ordenadas por id."""
    files = resources.files("dbts.testing").joinpath("catalog").iterdir()
    hypotheses = [
        Hypothesis(**tomllib.loads(f.read_text("utf-8"))) for f in files if f.name.endswith(".toml")
    ]
    unknown = [h.id for h in hypotheses if h.padrao not in MATCHERS]
    if unknown:
        raise ValueError(f"hipóteses com padrão desconhecido: {unknown}")
    return sorted(hypotheses, key=lambda h: h.id)


def _proposal(hypothesis: Hypothesis, match: Match) -> TestProposal:
    def fill(text: str) -> str:
        return Template(text).safe_substitute(match.params)

    return TestProposal(
        id=proposal_id(hypothesis.id, match.params),
        hypothesis_id=hypothesis.id,
        title=fill(hypothesis.titulo),
        description=fill(hypothesis.descricao),
        severity=hypothesis.severidade,
        criterio=fill(hypothesis.criterio),
        template=hypothesis.sql,
        params=dict(match.params),
        evidence=list(match.evidence),
    )


def propose(graph: Graph, catalog: list[Hypothesis]) -> list[TestProposal]:
    return [
        _proposal(hypothesis, match)
        for hypothesis in catalog
        for match in MATCHERS[hypothesis.padrao](graph)
    ]


def merge_plan(plan: TestPlan, fresh: list[TestProposal]) -> TestPlan:
    """Incorpora novas propostas preservando status e parâmetros já definidos pelo usuário.

    Propostas antigas que não reapareceram são mantidas (a decisão do usuário vale mais).
    """
    existing = {p.id: p for p in plan.proposals}
    merged = [existing.pop(p.id, p) for p in fresh]
    return plan.model_copy(update={"proposals": merged + list(existing.values())})
