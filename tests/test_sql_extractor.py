from dbts.domain.models import EdgeKind, EntityKind, Fact, FileRef
from dbts.extract.sql import SQLExtractor, neutralize_templates, split_statements

REF = FileRef(repo="r", path="q.sql", commit_sha="c")
JOB = "job:r/q.sql"


def _extract(sql: str) -> list[Fact]:
    return SQLExtractor().extract(sql, REF)


def _edges(facts: list[Fact], kind: EdgeKind) -> set[tuple[str, str]]:
    return {(f.edge.source, f.edge.target) for f in facts if f.edge and f.edge.kind is kind}


def _lines(facts: list[Fact], kind: EdgeKind) -> dict[str, int]:
    return {f.edge.target: f.location.line for f in facts if f.edge and f.edge.kind is kind}


CTAS = """-- cabeçalho
create table db.out as
select a.id, a.v + b.w as total, upper(b.nome) as nome
from db.a a
join db.b b on a.id = b.id and a.dt = b.dt
where a.dt = '${dt}';
"""


def test_ctas_reads_writes_and_joins() -> None:
    facts = _extract(CTAS)
    assert _edges(facts, EdgeKind.READS) == {(JOB, "table:db.a"), (JOB, "table:db.b")}
    assert _edges(facts, EdgeKind.WRITES) == {(JOB, "table:db.out")}
    assert _edges(facts, EdgeKind.JOINS_ON) == {
        ("column:db.a.id", "column:db.b.id"),
        ("column:db.a.dt", "column:db.b.dt"),
    }


def test_ctas_column_lineage() -> None:
    assert _edges(_extract(CTAS), EdgeKind.DERIVES_FROM) == {
        ("column:db.a.id", "column:db.out.id"),
        ("column:db.a.v", "column:db.out.total"),
        ("column:db.b.w", "column:db.out.total"),
        ("column:db.b.nome", "column:db.out.nome"),
    }


def test_statement_lines_are_tracked() -> None:
    facts = _extract("select 1;\n\ninsert into t2 select x from t1;")
    assert _lines(facts, EdgeKind.WRITES) == {"table:t2": 3}


def test_unqualified_columns_resolve_with_single_source() -> None:
    facts = _extract("insert into dst select x as y from src")
    assert _edges(facts, EdgeKind.DERIVES_FROM) == {("column:src.x", "column:dst.y")}


def test_unqualified_columns_unresolved_with_multiple_sources() -> None:
    facts = _extract("insert into dst select x from a join b on a.k = b.k")
    assert _edges(facts, EdgeKind.DERIVES_FROM) == set()


def test_ctes_are_not_tables_and_star_is_skipped() -> None:
    sql = "insert into dst with c as (select * from src) select * from c"
    facts = _extract(sql)
    assert _edges(facts, EdgeKind.READS) == {(JOB, "table:src")}
    assert _edges(facts, EdgeKind.DERIVES_FROM) == set()


def test_join_with_non_column_equality_is_ignored() -> None:
    facts = _extract("select a.x from a join b on a.k = 1 and a.z = q.z")
    assert _edges(facts, EdgeKind.JOINS_ON) == set()


def test_cross_join_without_on() -> None:
    facts = _extract("select a.x from a cross join b")
    assert _edges(facts, EdgeKind.JOINS_ON) == set()
    assert len(_edges(facts, EdgeKind.READS)) == 2


def test_ddl_registers_columns() -> None:
    facts = _extract("create external table db.t (id bigint, valor double) location 's3://b/'")
    columns = {f.entity.name for f in facts if f.entity and f.entity.kind is EntityKind.COLUMN}
    assert columns == {"db.t.id", "db.t.valor"}
    assert _edges(facts, EdgeKind.WRITES) == {(JOB, "table:db.t")}


def test_create_view_with_catalog() -> None:
    facts = _extract("create view cat.db.v as select id from cat.db.src")
    assert _edges(facts, EdgeKind.DERIVES_FROM) == {("column:cat.db.src.id", "column:cat.db.v.id")}


def test_invalid_statement_is_skipped_but_others_survive() -> None:
    facts = _extract("selec from where;\ninsert into t2 select x from t1;")
    assert _edges(facts, EdgeKind.WRITES) == {(JOB, "table:t2")}


def test_untokenizable_sql_yields_job_and_warning() -> None:
    facts = _extract("select 'unterminated")
    kinds = [(f.entity.kind, f.location.line) for f in facts if f.entity]
    assert kinds == [(EntityKind.JOB, 1), (EntityKind.WARNING, 1)]


def test_neutralize_templates() -> None:
    sql = "{% if x %}select {{ col }} from t where dt = ${dt}{% endif %}{# c #}"
    assert neutralize_templates(sql) == "select __param__ from t where dt = __param__"


def test_split_statements_ignores_empty_statements() -> None:
    assert list(split_statements(";;select 1;\nselect 2")) == [(1, "select 1"), (2, "select 2")]


def test_lineage_through_ctes_and_subqueries() -> None:
    sql = """
insert into m.out
with pag as (
    select p.id_cliente, sum(p.valor) as total from raw.pagamentos p group by 1
),
base as (select c.id_cliente, c.renda * 0.3 as limite from raw.clientes c)
select b.id_cliente, b.limite / nullif(x.total, 0) as razao, s.score
from base b
join pag x on b.id_cliente = x.id_cliente
left join (select id, score from raw.bureau) s on s.id = b.id_cliente
"""
    facts = _extract(sql)
    assert _edges(facts, EdgeKind.DERIVES_FROM) == {
        ("column:raw.clientes.id_cliente", "column:m.out.id_cliente"),
        ("column:raw.clientes.renda", "column:m.out.razao"),
        ("column:raw.pagamentos.valor", "column:m.out.razao"),
        ("column:raw.bureau.score", "column:m.out.score"),
    }
    assert _edges(facts, EdgeKind.READS) == {
        (JOB, "table:raw.pagamentos"),
        (JOB, "table:raw.clientes"),
        (JOB, "table:raw.bureau"),
    }


def test_lineage_through_union() -> None:
    facts = _extract("insert into m.u select x from a union all select y as x from b")
    assert _edges(facts, EdgeKind.DERIVES_FROM) == {
        ("column:a.x", "column:m.u.x"),
        ("column:b.y", "column:m.u.x"),
    }


def test_falls_back_to_alias_resolution_when_lineage_fails() -> None:
    facts = _extract("insert into m.f select t.*, t.x, z.q from a t join a t on t.k = t.k")
    assert _edges(facts, EdgeKind.DERIVES_FROM) == {("column:a.x", "column:m.f.x")}


def test_looks_like_sql() -> None:
    from dbts.extract.sql import looks_like_sql

    assert looks_like_sql("\n  WITH x as (select 1) select * from x")
    assert not looks_like_sql("Selecione uma opção")
    assert not looks_like_sql("selection")


def _filters(facts: list[Fact]) -> set[tuple[str, str | None]]:
    return {
        (f.edge.target, f.edge.detail) for f in facts if f.edge and f.edge.kind is EdgeKind.FILTERS
    }


def test_where_conjuncts_become_filters_without_aliases() -> None:
    sql = """
insert into m.base
select c.id from raw.clientes c join raw.pag p on c.id = p.id
where c.status <> 'INADIMPLENTE'
  and (c.renda > 0 or c.renda is null)
  and c.dt = '${dt}'
  and c.id = p.id
  and c.id in (select id from raw.bloqueados)
"""
    assert _filters(_extract(sql)) == {
        ("column:raw.clientes.status", "status <> 'INADIMPLENTE'"),
        ("column:raw.clientes.renda", "renda > 0 OR renda IS NULL"),
    }


def test_single_filter_and_unresolved_columns() -> None:
    assert _filters(_extract("select x from t where x > 1")) == {("column:t.x", "x > 1")}
    assert _filters(_extract("select a.x from a join b on a.k = b.k where y > 1")) == set()
    assert _filters(_extract("select x from t where 1 = 1")) == set()


def test_unparsable_statement_becomes_warning_at_its_line() -> None:
    facts = _extract("select 1;\n\nselec from where;\n")
    warnings = [
        (f.entity.id, f.location.line)
        for f in facts
        if f.entity and f.entity.kind is EntityKind.WARNING
    ]
    assert warnings == [("warning:r/q.sql:3", 3)]


def test_parse_predicate() -> None:
    from dbts.extract.sql import parse_predicate

    assert parse_predicate("valor > 100 and uf = 'SP'") == (
        ["uf", "valor"],
        "valor > 100 AND uf = 'SP'",
    )
    assert parse_predicate("1 = 1") is None
    assert parse_predicate("x in (select 1)") is None
    assert parse_predicate("dt = '__param__'") is None
    assert parse_predicate("x >") is None


def test_join_and_filter_through_ctes() -> None:
    sql = """
insert into m.out
with pag as (select p.id_cliente, sum(p.valor) as total from raw.pagamentos p group by 1),
ren as (select c.id_cliente as chave, c.status as st, c.uf from raw.clientes c),
dup as (select * from ren)
select r.chave, x.total
from ren r
join pag x on r.chave = x.id_cliente
join pag y on r.chave = y.total
where r.uf = 'SP' and r.st <> 'X'
"""
    facts = _extract(sql)
    assert _edges(facts, EdgeKind.JOINS_ON) == {
        ("column:raw.clientes.id_cliente", "column:raw.pagamentos.id_cliente")
    }
    assert _filters(facts) == {("column:raw.clientes.uf", "uf = 'SP'")}
