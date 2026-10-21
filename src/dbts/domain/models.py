from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class Origin(StrEnum):
    PARSER = "parser"
    LLM = "llm"
    USER = "usuario"


class EntityKind(StrEnum):
    REPO = "repo"
    JOB = "job"
    TABLE = "table"
    COLUMN = "column"
    WARNING = "warning"


class EdgeKind(StrEnum):
    READS = "reads"
    WRITES = "writes"
    JOINS_ON = "joins_on"
    DERIVES_FROM = "derives_from"
    DEPLOYED_BY = "deployed_by"
    STORED_AT = "stored_at"
    FILTERS = "filters"


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class FileRef(_Frozen):
    repo: str
    path: str
    commit_sha: str


class SourceLocation(_Frozen):
    repo: str
    path: str
    line: int
    commit_sha: str


class Entity(_Frozen):
    id: str
    kind: EntityKind
    name: str


class Edge(_Frozen):
    source: str
    target: str
    kind: EdgeKind
    detail: str | None = None  # ex.: o predicado SQL de uma aresta `filters`


class Fact(_Frozen):
    """Unidade do mapa. Fatos com origem LLM são hipóteses até confirmação."""

    entity: Entity | None = None
    edge: Edge | None = None
    location: SourceLocation
    origin: Origin

    @property
    def is_hypothesis(self) -> bool:
        return self.origin is Origin.LLM
