from factories import pipeline_facts

from dbts.domain.models import EdgeKind, EntityKind, FileRef
from dbts.extract.facts import FactBuilder
from dbts.mapping.graph import Graph


def test_from_facts_merges_entities_and_edge_locations() -> None:
    graph = Graph.from_facts(pipeline_facts())
    reads_base = [
        i for i in graph.edges_to("table:analytics.base") if i.edge.kind is EdgeKind.READS
    ]
    assert len(reads_base) == 1
    assert [loc.repo for loc in reads_base[0].locations] == ["modelos"]
    assert "table:raw.clientes" in graph.entities


def test_same_edge_from_two_files_keeps_both_locations_sorted() -> None:
    facts = []
    for path in ("b.sql", "a.sql"):
        builder = FactBuilder(FileRef(repo="r", path=path, commit_sha="c"))
        builder.edge("job:x", builder.table("t", 1), EdgeKind.READS, 1)
        facts += builder.build()
    (info,) = Graph.from_facts(facts).edges
    assert [loc.path for loc in info.locations] == ["a.sql", "b.sql"]


def test_hypothesis_only_when_all_support_is_llm() -> None:
    graph = Graph.from_facts(pipeline_facts())
    flags = {
        i.edge.target: i.hypothesis for i in graph.edges if i.edge.kind is EdgeKind.DERIVES_FROM
    }
    assert flags == {"column:analytics.base.limite": False, "column:models.abt.lim": True}


def test_find_is_case_insensitive_substring() -> None:
    graph = Graph.from_facts(pipeline_facts())
    assert graph.find("BASE") == {"table:analytics.base", "column:analytics.base.limite"}


def test_around_respects_depth() -> None:
    graph = Graph.from_facts(pipeline_facts())
    seeds = {"table:analytics.base"}
    assert set(graph.around(seeds, 0).entities) == seeds
    one_hop = set(graph.around(seeds, 1).entities)
    assert one_hop == {"table:analytics.base", "job:risco/score.sql", "job:modelos/modelo.py"}
    two_hops = graph.around(seeds, 2)
    assert "table:models.abt" in two_hops.entities
    assert all({i.edge.source, i.edge.target} <= set(two_hops.entities) for i in two_hops.edges)


def test_of_kind_is_sorted() -> None:
    graph = Graph.from_facts(pipeline_facts())
    jobs = [e.id for e in graph.of_kind(EntityKind.JOB)]
    assert jobs == sorted(jobs) and len(jobs) == 3


def test_around_keeps_warnings_of_reached_files_only() -> None:
    reached = FactBuilder(FileRef(repo="r", path="a.sql", commit_sha="c"))
    reached.edge(reached.job(), reached.table("t", 1), EdgeKind.READS, 1)
    reached.warning(5, "x")
    other = FactBuilder(FileRef(repo="r", path="b.sql", commit_sha="c"))
    other.warning(2, "y")
    graph = Graph.from_facts(reached.build() + other.build())
    entities = set(graph.around({"table:t"}, 1).entities)
    assert "warning:r/a.sql:5" in entities
    assert "warning:r/b.sql:2" not in entities
