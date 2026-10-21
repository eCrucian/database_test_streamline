from dbts.domain.models import EdgeKind, EntityKind, Fact, FileRef
from dbts.extract.pyspark import PySparkExtractor

REF = FileRef(repo="r", path="job.py", commit_sha="c")
JOB = "job:r/job.py"


def _extract(code: str) -> list[Fact]:
    return PySparkExtractor().extract(code, REF)


def _edges(facts: list[Fact], kind: EdgeKind) -> set[tuple[str, str]]:
    return {(f.edge.source, f.edge.target) for f in facts if f.edge and f.edge.kind is kind}


def test_reads_and_writes_tables_through_variables() -> None:
    code = """
clientes = spark.table("raw.clientes")
pag = spark.read.table("raw.pagamentos")
base = clientes.join(pag, "id_cliente", "left").filter("x > 1")
base.write.mode("overwrite").saveAsTable("analytics.base")
"""
    facts = _extract(code)
    assert _edges(facts, EdgeKind.READS) == {
        (JOB, "table:raw.clientes"),
        (JOB, "table:raw.pagamentos"),
    }
    assert _edges(facts, EdgeKind.WRITES) == {(JOB, "table:analytics.base")}
    assert _edges(facts, EdgeKind.JOINS_ON) == {
        ("column:raw.clientes.id_cliente", "column:raw.pagamentos.id_cliente")
    }


def test_join_on_list_and_on_keyword() -> None:
    code = """
a = spark.table("a")
b = spark.table("b")
a.join(b, on=["k1", "k2"])
"""
    assert _edges(_extract(code), EdgeKind.JOINS_ON) == {
        ("column:a.k1", "column:b.k1"),
        ("column:a.k2", "column:b.k2"),
    }


def test_join_on_column_expressions() -> None:
    code = """
a = spark.table("a")
b = spark.table("b")
a.join(b, (a.id == b.cliente_id) & (a["dt"] == b["dt_ref"]))
a.join(b, a.x > b.y)
a.join(b, F.col("x") == b.y)
"""
    assert _edges(_extract(code), EdgeKind.JOINS_ON) == {
        ("column:a.id", "column:b.cliente_id"),
        ("column:a.dt", "column:b.dt_ref"),
    }


def test_join_keys_skipped_when_side_has_multiple_tables() -> None:
    code = """
ab = spark.table("a").join(spark.table("b"))
c = spark.table("c")
ab.join(c, "k")
ab.join(c, ab.k == c.k)
"""
    assert _edges(_extract(code), EdgeKind.JOINS_ON) == set()


def test_spark_sql_with_variable_and_fstring() -> None:
    code = '''
query = f"""
insert into {db}.saida
select c.id from raw.clientes c
"""
df = spark.sql(query)
df.write.saveAsTable("x.y")
'''
    facts = _extract(code)
    assert _edges(facts, EdgeKind.WRITES) == {(JOB, "table:__param__.saida"), (JOB, "table:x.y")}
    assert (JOB, "table:raw.clientes") in _edges(facts, EdgeKind.READS)
    assert ("column:raw.clientes.id", "column:__param__.saida.id") in _edges(
        facts, EdgeKind.DERIVES_FROM
    )


def test_spark_sql_frame_carries_source_tables_into_joins() -> None:
    code = """
a = spark.sql("select * from raw.a")
b = spark.table("raw.b")
a.join(b, "id")
"""
    assert _edges(_extract(code), EdgeKind.JOINS_ON) == {("column:raw.a.id", "column:raw.b.id")}


def test_awswrangler_and_boto3_sql() -> None:
    code = """
wr.athena.read_sql_query(sql="select x from db.t1", database="db")
athena.start_query_execution(QueryString="insert into db.t2 select x from db.t1")
"""
    facts = _extract(code)
    assert _edges(facts, EdgeKind.WRITES) == {(JOB, "table:db.t2")}
    assert (JOB, "table:db.t1") in _edges(facts, EdgeKind.READS)


def test_sql_call_without_literal_is_ignored() -> None:
    facts = _extract("spark.sql(build_query())\ncursor.execute()")
    assert _edges(facts, EdgeKind.READS) == set()


def test_file_reads_and_writes() -> None:
    code = """
df = spark.read.parquet("s3://bucket/raw/")
df.write.format("delta").save(path="s3://bucket/out/")
df.write.parquet(output_path)
status = df.write.save("s3://bucket/status/")
"""
    facts = _extract(code)
    assert _edges(facts, EdgeKind.READS) == {(JOB, "table:s3://bucket/raw")}
    assert _edges(facts, EdgeKind.WRITES) == {
        (JOB, "table:s3://bucket/out"),
        (JOB, "table:s3://bucket/status"),
    }


def test_function_wrapping_frames_and_unknown_names() -> None:
    code = """
a = spark.table("a")
b = F.broadcast(spark.table("b"))
a.join(b, "k")
a.join(unknown, "k")
x, y = 1, 2
z = 42
"""
    assert _edges(_extract(code), EdgeKind.JOINS_ON) == {("column:a.k", "column:b.k")}


def test_join_without_arguments() -> None:
    facts = _extract('spark.table("a").join()')
    assert _edges(facts, EdgeKind.READS) == {(JOB, "table:a")}


def test_syntax_error_yields_only_job() -> None:
    facts = _extract("def broken(:")
    assert [f.entity.kind for f in facts if f.entity] == [EntityKind.JOB]


def test_reads_inside_functions_are_found() -> None:
    code = """
def load(spark):
    return spark.table("raw.x")
"""
    assert _edges(_extract(code), EdgeKind.READS) == {(JOB, "table:raw.x")}


def test_dynamic_table_name_is_not_guessed() -> None:
    assert _edges(_extract("spark.table(nome_dinamico)"), EdgeKind.READS) == set()


def test_with_column_lineage_is_transitive_until_write() -> None:
    code = """
from pyspark.sql import functions as F
df = spark.table("raw.clientes")
df = df.withColumn("limite", F.col("renda") * 0.3)
df = df.withColumn("limite_ajustado", F.col("limite") + F.col("bonus"))
df = df.withColumnRenamed("limite_ajustado", "limite_final")
df.write.saveAsTable("models.abt")
"""
    derives = _edges(_extract(code), EdgeKind.DERIVES_FROM)
    assert ("column:raw.clientes.renda", "column:models.abt.limite") in derives
    assert ("column:raw.clientes.renda", "column:models.abt.limite_final") in derives
    assert ("column:raw.clientes.bonus", "column:models.abt.limite_final") in derives


def test_select_with_alias_strings_and_frame_attributes() -> None:
    code = """
c = spark.table("raw.c")
out = c.select("id", c.renda, c["uf"], F.col("idade").alias("idade_anos"), F.lit(1).alias("um"))
out.write.saveAsTable("m.out")
"""
    assert _edges(_extract(code), EdgeKind.DERIVES_FROM) == {
        ("column:raw.c.id", "column:m.out.id"),
        ("column:raw.c.renda", "column:m.out.renda"),
        ("column:raw.c.uf", "column:m.out.uf"),
        ("column:raw.c.idade", "column:m.out.idade_anos"),
    }


def test_group_by_agg_lineage() -> None:
    code = """
p = spark.table("raw.pagamentos")
agg = p.groupBy("id_cliente").agg(
    F.sum("valor").alias("total"), F.max(p.atraso).alias("max_atraso")
)
agg.write.saveAsTable("m.agg")
"""
    assert _edges(_extract(code), EdgeKind.DERIVES_FROM) == {
        ("column:raw.pagamentos.id_cliente", "column:m.agg.id_cliente"),
        ("column:raw.pagamentos.valor", "column:m.agg.total"),
        ("column:raw.pagamentos.atraso", "column:m.agg.max_atraso"),
    }


def test_lineage_through_join_uses_frame_attributes() -> None:
    code = """
a = spark.table("raw.a")
b = spark.table("raw.b")
j = a.join(b, a.id == b.id).withColumn("razao", a.valor / b.renda)
j.write.saveAsTable("m.j")
"""
    assert _edges(_extract(code), EdgeKind.DERIVES_FROM) == {
        ("column:raw.a.valor", "column:m.j.razao"),
        ("column:raw.b.renda", "column:m.j.razao"),
        # sem select, a chave de junção segue para a saída
        ("column:raw.a.id", "column:m.j.id"),
        ("column:raw.b.id", "column:m.j.id"),
    }


def test_join_key_resolves_derived_column() -> None:
    code = """
a = spark.table("raw.a").withColumnRenamed("cpf", "chave")
b = spark.table("raw.b")
a.join(b, a.chave == b.cpf_hash)
"""
    assert _edges(_extract(code), EdgeKind.JOINS_ON) == {
        ("column:raw.a.cpf", "column:raw.b.cpf_hash")
    }


def test_column_ops_with_non_literal_names_keep_frame() -> None:
    code = """
df = spark.table("raw.t")
df = df.withColumn(nome, F.col("x")).withColumnRenamed(velho, "novo").withColumn("y")
df = df.select(nome_dinamico, F.col(var), outro_df.x, F.lit(1).alias(alias_var))
df.write.saveAsTable(destino)
df.write.saveAsTable("m.t")
"""
    facts = _extract(code)
    assert _edges(facts, EdgeKind.DERIVES_FROM) == set()
    assert _edges(facts, EdgeKind.WRITES) == {(JOB, "table:m.t")}


def test_sql_in_loose_strings_and_fstrings() -> None:
    code = '''
QUERIES = {
    "base": """
        insert into analytics.base
        select id from raw.clientes
    """,
}
consulta = f"select valor from raw.pagamentos where dt = '{dt}'"
"""Select the documentation."""
msg = f"total: {n}"
'''
    facts = _extract(code)
    assert _edges(facts, EdgeKind.WRITES) == {(JOB, "table:analytics.base")}
    assert _edges(facts, EdgeKind.READS) == {
        (JOB, "table:raw.clientes"),
        (JOB, "table:raw.pagamentos"),
    }


def _filters(facts: list[Fact]) -> set[tuple[str, str | None]]:
    return {
        (f.edge.target, f.edge.detail) for f in facts if f.edge and f.edge.kind is EdgeKind.FILTERS
    }


def test_string_filters_on_physical_columns() -> None:
    code = """
df = spark.table("raw.c").filter("status <> 'X'").where(condition="renda > 0")
df = df.withColumn("limite", F.col("renda") * 2).filter("limite > 10")
df.filter(F.col("x") > 1)
df.filter(f"dt = '{dt}'")
ab = spark.table("a").join(spark.table("b"))
ab.filter("k = 1")
"""
    assert _filters(_extract(code)) == {
        ("column:raw.c.status", "status <> 'X'"),
        ("column:raw.c.renda", "renda > 0"),
    }


def test_filters_and_join_keys_disambiguate_columns_after_join() -> None:
    code = """
base = spark.table("analytics.base")
bureau = spark.table("raw.bureau").filter("score is not null").filter("score > 0")
abt = base.join(bureau, base.id_cliente == bureau.cpf_hash, "left")
abt = abt.withColumn("score_final", F.col("score") * 0.7)
abt.select("id_cliente", "score_final", "dt_ref").write.saveAsTable("models.abt")
"""
    assert _edges(_extract(code), EdgeKind.DERIVES_FROM) == {
        ("column:analytics.base.id_cliente", "column:models.abt.id_cliente"),
        ("column:raw.bureau.score", "column:models.abt.score_final"),
    }
