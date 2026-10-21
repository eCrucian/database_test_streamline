from dbts.domain.models import EdgeKind, EntityKind, Fact, FileRef
from dbts.extract.terraform import TerraformExtractor, _line

REF = FileRef(repo="infra", path="glue.tf", commit_sha="c")
JOB = "job:infra/glue.tf"

GLUE = """
variable "env" {}

resource "aws_glue_catalog_table" "clientes" {
  name          = "clientes"
  database_name = "${var.env}_raw"
  storage_descriptor {
    location = "s3://bucket/raw/clientes/"
    columns {
      name = "id_cliente"
      type = "bigint"
    }
    columns {
      name = "renda"
      type = "double"
    }
  }
  partition_keys {
    name = "dt"
  }
}

resource "aws_athena_named_query" "carga" {
  name  = "carga"
  query = <<-EOT
    insert into analytics.base
    select id_cliente from raw.clientes
  EOT
}

resource "aws_s3_bucket" "ignorado" {
  bucket = "x"
}
"""


def _extract(content: str) -> list[Fact]:
    return TerraformExtractor().extract(content, REF)


def _edges(facts: list[Fact], kind: EdgeKind) -> set[tuple[str, str]]:
    return {(f.edge.source, f.edge.target) for f in facts if f.edge and f.edge.kind is kind}


def _entities(facts: list[Fact], kind: EntityKind) -> set[str]:
    return {f.entity.name for f in facts if f.entity and f.entity.kind is kind}


def test_glue_table_columns_partitions_and_location() -> None:
    facts = _extract(GLUE)
    table = "table:__param___raw.clientes"
    assert (table, JOB) in _edges(facts, EdgeKind.DEPLOYED_BY)
    assert _edges(facts, EdgeKind.STORED_AT) == {(table, "table:s3://bucket/raw/clientes")}
    assert {"__param___raw.clientes.id_cliente", "__param___raw.clientes.renda"} <= _entities(
        facts, EntityKind.COLUMN
    )
    assert "__param___raw.clientes.dt" in _entities(facts, EntityKind.COLUMN)


def test_glue_table_line_points_to_resource_block() -> None:
    facts = _extract(GLUE)
    lines = {
        f.edge.source: f.location.line
        for f in facts
        if f.edge and f.edge.kind is EdgeKind.STORED_AT
    }
    assert lines == {"table:__param___raw.clientes": 4}


def test_named_query_sql_is_extracted() -> None:
    facts = _extract(GLUE)
    assert (JOB, "table:analytics.base") in _edges(facts, EdgeKind.WRITES)
    assert ("column:raw.clientes.id_cliente", "column:analytics.base.id_cliente") in _edges(
        facts, EdgeKind.DERIVES_FROM
    )


def test_incomplete_resources_are_ignored() -> None:
    tf = """
resource "aws_glue_catalog_table" "sem_db" {
  name = "t"
}
resource "aws_glue_catalog_table" "sem_storage" {
  name          = "t"
  database_name = "db"
}
resource "aws_athena_named_query" "sem_query" {
  name = "q"
}
"""
    facts = _extract(tf)
    assert _edges(facts, EdgeKind.DEPLOYED_BY) == {("table:db.t", JOB)}
    assert _edges(facts, EdgeKind.STORED_AT) == set()
    assert _entities(facts, EntityKind.COLUMN) == set()


def test_invalid_hcl_yields_only_job() -> None:
    assert [f.entity.kind for f in _extract('resource "x" {') if f.entity] == [EntityKind.JOB]


def test_line_defaults_to_one_when_block_not_found() -> None:
    assert _line("", "aws_x", "y") == 1
