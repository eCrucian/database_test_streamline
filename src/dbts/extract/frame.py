from collections.abc import Mapping
from dataclasses import dataclass, field

Column = tuple[str, str]


@dataclass(frozen=True)
class Frame:
    """DataFrame rastreado: tabelas de origem e, por coluna conhecida, suas colunas físicas."""

    tables: frozenset[str] = frozenset()
    columns: Mapping[str, frozenset[Column]] = field(default_factory=dict)

    def resolve(self, name: str) -> frozenset[Column]:
        name = name.lower()
        if name in self.columns:
            return self.columns[name]
        if len(self.tables) == 1:
            return frozenset({(next(iter(self.tables)), name)})
        return frozenset()

    def resolve_one(self, name: str) -> Column | None:
        sources = self.resolve(name)
        return next(iter(sources)) if len(sources) == 1 else None

    def with_columns(self, columns: Mapping[str, frozenset[Column]]) -> "Frame":
        lowered = {name.lower(): sources for name, sources in columns.items()}
        return Frame(self.tables, {**self.columns, **lowered})

    def only_columns(self, columns: Mapping[str, frozenset[Column]]) -> "Frame":
        return Frame(self.tables).with_columns(columns)

    def merge(self, other: "Frame") -> "Frame":
        return Frame(self.tables | other.tables).with_columns({**self.columns, **other.columns})

    def __bool__(self) -> bool:
        return bool(self.tables or self.columns)
