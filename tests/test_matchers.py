from factories import validation_facts

from dbts.mapping.graph import Graph
from dbts.testing.matchers import (
    date_columns,
    divergent_definitions,
    join_keys,
    key_columns,
    split_column,
)


def _graph() -> Graph:
    return Graph.from_facts(validation_facts())


def test_split_column_keeps_dotted_table() -> None:
    assert split_column("column:cat.db.t.col") == ("cat.db.t", "col")


def test_join_keys() -> None:
    (match,) = join_keys(_graph())
    assert match.params == {
        "left_table": "raw.clientes",
        "left_col": "id_cliente",
        "right_table": "raw.pagamentos",
        "right_col": "id_cliente",
    }
    assert match.evidence[0].line == 3


def test_key_columns_only_in_written_tables() -> None:
    matches = list(key_columns(_graph()))
    assert [m.params for m in matches] == [{"table": "analytics.base", "column": "id_cliente"}]
    assert matches[0].evidence[0].path == "base.sql"


def test_date_columns_need_two_dates() -> None:
    (match,) = date_columns(_graph())
    assert match.params == {"table": "analytics.base", "date_columns": "dt_evento, dt_ref"}


def test_divergent_definitions() -> None:
    (match,) = divergent_definitions(_graph())
    assert match.params == {
        "column": "limite",
        "table_a": "analytics.base",
        "table_b": "analytics.outra",
        "sources_a": "raw.clientes.renda",
        "sources_b": "raw.clientes.salario",
    }
    assert {e.repo for e in match.evidence} == {"risco", "outro"}


def test_same_definition_is_not_divergent() -> None:
    from dbts.domain.models import EdgeKind, FileRef
    from dbts.extract.facts import FactBuilder

    builder = FactBuilder(FileRef(repo="r", path="x.sql", commit_sha="c"))
    for table in ("t1", "t2"):
        builder.edge(
            builder.column("src", "a", 1), builder.column(table, "a", 1), EdgeKind.DERIVES_FROM, 1
        )
    assert list(divergent_definitions(Graph.from_facts(builder.build()))) == []


def test_filters_one_match_per_table_and_predicate() -> None:
    from dbts.testing.matchers import filters

    (match,) = filters(_graph())
    assert match.params == {
        "table": "raw.clientes",
        "predicate": "status <> 'INADIMPLENTE' AND renda > 0",
    }
    assert len(match.evidence) == 1


def test_pass_through_downstream_is_not_divergent() -> None:
    from dbts.domain.models import EdgeKind, FileRef
    from dbts.extract.facts import FactBuilder

    builder = FactBuilder(FileRef(repo="r", path="x.sql", commit_sha="c"))
    builder.edge(
        builder.column("raw", "id", 1), builder.column("base", "id", 1), EdgeKind.DERIVES_FROM, 1
    )
    builder.edge(
        builder.column("base", "id", 1), builder.column("abt", "id", 1), EdgeKind.DERIVES_FROM, 1
    )
    builder.edge(
        builder.column("base", "id", 1), builder.column("abt2", "id", 1), EdgeKind.DERIVES_FROM, 1
    )
    assert list(divergent_definitions(Graph.from_facts(builder.build()))) == []
