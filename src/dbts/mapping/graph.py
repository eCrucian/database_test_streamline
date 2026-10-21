from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field

from dbts.domain.models import Edge, Entity, EntityKind, Fact, SourceLocation


@dataclass(frozen=True)
class EdgeInfo:
    """Aresta única do grafo com todas as localizações e origens que a sustentam."""

    edge: Edge
    locations: tuple[SourceLocation, ...]
    hypothesis: bool


@dataclass(frozen=True)
class Graph:
    entities: dict[str, Entity] = field(default_factory=dict)
    edges: tuple[EdgeInfo, ...] = ()

    @classmethod
    def from_facts(cls, facts: Iterable[Fact]) -> "Graph":
        entities: dict[str, Entity] = {}
        support: dict[Edge, list[Fact]] = defaultdict(list)
        for fact in facts:
            if fact.entity:
                entities.setdefault(fact.entity.id, fact.entity)
            if fact.edge:
                support[fact.edge].append(fact)
        edges = tuple(
            EdgeInfo(
                edge=edge,
                locations=tuple(sorted({f.location for f in items}, key=_location_key)),
                hypothesis=all(f.is_hypothesis for f in items),
            )
            for edge, items in support.items()
        )
        return cls(entities, edges)

    def find(self, term: str) -> set[str]:
        term = term.lower()
        return {eid for eid, entity in self.entities.items() if term in entity.name.lower()}

    def around(self, seeds: set[str], depth: int) -> "Graph":
        """Subgrafo com tudo a até `depth` arestas das sementes, em qualquer direção."""
        adjacency = self._adjacency()
        reached, frontier = set(seeds), set(seeds)
        for _ in range(depth):
            frontier = {n for node in frontier for n in adjacency[node]} - reached
            reached |= frontier
        return self._restricted(reached | self._warnings_of(reached))

    def _warnings_of(self, nodes: set[str]) -> set[str]:
        """Avisos de extração dos arquivos (jobs) alcançados."""
        files = {node.removeprefix("job:") for node in nodes if node.startswith("job:")}
        return {
            eid
            for eid in self.entities
            if eid.startswith("warning:")
            and eid.removeprefix("warning:").rsplit(":", 1)[0] in files
        }

    def of_kind(self, kind: EntityKind) -> list[Entity]:
        return sorted((e for e in self.entities.values() if e.kind is kind), key=lambda e: e.id)

    def edges_from(self, node: str) -> list[EdgeInfo]:
        return [info for info in self.edges if info.edge.source == node]

    def edges_to(self, node: str) -> list[EdgeInfo]:
        return [info for info in self.edges if info.edge.target == node]

    def _adjacency(self) -> dict[str, set[str]]:
        adjacency: dict[str, set[str]] = defaultdict(set)
        for info in self.edges:
            adjacency[info.edge.source].add(info.edge.target)
            adjacency[info.edge.target].add(info.edge.source)
        return adjacency

    def _restricted(self, nodes: set[str]) -> "Graph":
        entities = {eid: e for eid, e in self.entities.items() if eid in nodes}
        edges = tuple(info for info in self.edges if {info.edge.source, info.edge.target} <= nodes)
        return Graph(entities, edges)


def _location_key(location: SourceLocation) -> tuple[str, str, int]:
    return location.repo, location.path, location.line
