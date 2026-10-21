import hashlib
import json
from enum import StrEnum
from string import Template
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from dbts.domain.models import Origin, SourceLocation


class Severity(StrEnum):
    LOW = "baixa"
    MEDIUM = "media"
    HIGH = "alta"


class ProposalStatus(StrEnum):
    PROPOSED = "proposto"
    ACCEPTED = "aceito"
    REJECTED = "rejeitado"


class Hypothesis(BaseModel):
    """Hipótese de validação declarativa, carregada do catálogo."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    nome: str
    descricao: str
    categoria: str
    severidade: Severity
    padrao: str
    titulo: str
    sql: str
    criterio: str


class TestProposal(BaseModel):
    __test__: ClassVar[bool] = False  # não é classe de teste do pytest
    model_config = ConfigDict(extra="forbid")

    id: str
    hypothesis_id: str
    title: str
    description: str
    severity: Severity
    criterio: str
    template: str
    params: dict[str, str] = Field(default_factory=dict)
    evidence: list[SourceLocation] = Field(default_factory=list)
    status: ProposalStatus = ProposalStatus.PROPOSED
    origin: Origin = Origin.PARSER

    @property
    def missing(self) -> list[str]:
        """Parâmetros do template ainda sem valor."""
        identifiers = Template(self.template).get_identifiers()
        return [name for name in identifiers if name not in self.params]

    def render(self) -> str:
        return Template(self.template).safe_substitute(self.params).strip()


class TestPlan(BaseModel):
    __test__: ClassVar[bool] = False  # não é classe de teste do pytest
    model_config = ConfigDict(extra="forbid")

    name: str
    term: str | None = None
    commits: dict[str, str] = Field(default_factory=dict)
    proposals: list[TestProposal] = Field(default_factory=list)

    def get(self, proposal_id: str) -> TestProposal:
        for proposal in self.proposals:
            if proposal.id == proposal_id:
                return proposal
        raise KeyError(proposal_id)


def proposal_id(hypothesis_id: str, params: dict[str, str]) -> str:
    material = json.dumps([hypothesis_id, sorted(params.items())])
    return hashlib.sha256(material.encode()).hexdigest()[:8]
