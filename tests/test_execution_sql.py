import pytest

from dbts.execution.sql import GuardError, ensure_safe, normalize, query_hash


@pytest.mark.parametrize(
    "sql",
    [
        "select 1",
        "-- cabeçalho\nwith a as (select 1) select * from a",
        "select 1 union all select 2;",
        "create table sandbox.t as select 1",
        "CREATE TABLE SANDBOX.t AS SELECT 1",
    ],
)
def test_allowed(sql: str) -> None:
    ensure_safe(sql, "sandbox")


@pytest.mark.parametrize(
    ("sql", "message"),
    [
        ("insert into x select 1", "apenas SELECT"),
        ("drop table x", "apenas SELECT"),
        ("create table prod.t as select 1", "apenas SELECT"),
        ("create table t as select 1", "apenas SELECT"),
        ("create table sandbox.t (id int)", "apenas SELECT"),
        ("select 1; drop table x", "esperado 1 statement"),
        ("", "esperado 1 statement"),
        ("select (", "SQL inválido"),
    ],
)
def test_blocked(sql: str, message: str) -> None:
    with pytest.raises(GuardError, match=message):
        ensure_safe(sql, "sandbox")


def test_hash_ignores_header_comments_and_formatting() -> None:
    a = "-- Teste: x\n-- Hash: y\nselect  a,\n b from t"
    b = "SELECT a, b FROM t"
    assert normalize(a) == "SELECT a, b FROM t"
    assert query_hash(a) == query_hash(b)
    assert query_hash(b) != query_hash("SELECT a FROM t")
