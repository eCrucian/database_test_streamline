from dbts.domain.models import (
    Edge,
    EdgeKind,
    Entity,
    EntityKind,
    Fact,
    FileRef,
    Origin,
    SourceLocation,
)


def normalize_table(name: str) -> str:
    """Tabelas em minúsculas (Athena ignora caixa); caminhos de storage (s3://...) mantêm a
    caixa, pois chaves S3 a diferenciam, e perdem a barra final."""
    return name.rstrip("/") if "://" in name else name.lower()


def table_id(name: str) -> str:
    return f"table:{normalize_table(name)}"


def column_id(table: str, column: str) -> str:
    return f"column:{normalize_table(table)}.{column.lower()}"


def job_id(ref: FileRef) -> str:
    return f"job:{ref.repo}/{ref.path}"


class FactBuilder:
    """Acumula fatos de um arquivo sem duplicatas, preservando a primeira linha vista."""

    def __init__(self, ref: FileRef, origin: Origin = Origin.PARSER) -> None:
        self._ref = ref
        self._origin = origin
        self._facts: dict[str, Fact] = {}

    def job(self, line: int = 1) -> str:
        return self._entity(job_id(self._ref), EntityKind.JOB, self._ref.path, line)

    def table(self, name: str, line: int) -> str:
        return self._entity(table_id(name), EntityKind.TABLE, normalize_table(name), line)

    def column(self, table: str, column: str, line: int) -> str:
        self.table(table, line)
        name = f"{normalize_table(table)}.{column.lower()}"
        return self._entity(column_id(table, column), EntityKind.COLUMN, name, line)

    def edge(
        self, source: str, target: str, kind: EdgeKind, line: int, detail: str | None = None
    ) -> None:
        key = f"edge:{kind}:{source}->{target}:{detail}"
        edge = Edge(source=source, target=target, kind=kind, detail=detail)
        self._facts.setdefault(key, self._fact(line, edge=edge))

    def warning(self, line: int, message: str) -> None:
        """Trecho que o extrator não conseguiu analisar (aparece nos guias)."""
        warning_id = f"warning:{self._ref.repo}/{self._ref.path}:{line}"
        self._entity(warning_id, EntityKind.WARNING, message, line)

    def build(self) -> list[Fact]:
        return list(self._facts.values())

    def _entity(self, entity_id: str, kind: EntityKind, name: str, line: int) -> str:
        entity = Entity(id=entity_id, kind=kind, name=name)
        self._facts.setdefault(entity_id, self._fact(line, entity=entity))
        return entity_id

    def _fact(self, line: int, entity: Entity | None = None, edge: Edge | None = None) -> Fact:
        location = SourceLocation(**self._ref.model_dump(), line=line)
        return Fact(entity=entity, edge=edge, location=location, origin=self._origin)
