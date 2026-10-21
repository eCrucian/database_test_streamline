from dbts.domain.models import EdgeKind, EntityKind, FileRef, Origin
from dbts.extract.facts import FactBuilder, column_id, job_id, table_id

REF = FileRef(repo="r", path="etl/q.sql", commit_sha="c")


def test_ids_are_normalized() -> None:
    assert table_id("DB.Tab") == "table:db.tab"
    assert column_id("DB.Tab", "Col") == "column:db.tab.col"
    assert job_id(REF) == "job:r/etl/q.sql"
    assert table_id("s3://Bucket/Raw/") == "table:s3://Bucket/Raw"
    assert column_id("s3://b/p/", "X") == "column:s3://b/p.x"


def test_column_registers_its_table_and_dedupes_keeping_first_line() -> None:
    builder = FactBuilder(REF)
    builder.column("db.t", "id", 3)
    builder.column("db.t", "id", 9)
    facts = builder.build()
    assert [(f.entity.kind, f.location.line) for f in facts if f.entity] == [
        (EntityKind.TABLE, 3),
        (EntityKind.COLUMN, 3),
    ]


def test_edges_are_deduped_and_carry_origin() -> None:
    builder = FactBuilder(REF, origin=Origin.LLM)
    job = builder.job()
    table = builder.table("t", 2)
    builder.edge(job, table, EdgeKind.READS, 2)
    builder.edge(job, table, EdgeKind.READS, 5)
    edges = [f for f in builder.build() if f.edge]
    assert len(edges) == 1
    assert edges[0].is_hypothesis
    assert edges[0].location.path == "etl/q.sql"
