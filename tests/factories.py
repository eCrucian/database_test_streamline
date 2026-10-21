"""Fatos de exemplo compartilhados pelos testes de grafo, renderização e guia."""

from dbts.domain.execution import QueryResult
from dbts.domain.models import EdgeKind, Fact, FileRef, Origin
from dbts.extract.facts import FactBuilder


def pipeline_facts() -> list[Fact]:
    """raw.clientes + raw.pagamentos -> score.sql -> analytics.base -> modelo.py -> models.abt."""
    sql = FactBuilder(FileRef(repo="risco", path="score.sql", commit_sha="c1"))
    job = sql.job()
    for name in ("raw.clientes", "raw.pagamentos"):
        sql.edge(job, sql.table(name, 2), EdgeKind.READS, 2)
    sql.edge(job, sql.table("analytics.base", 2), EdgeKind.WRITES, 2)
    left, right = sql.column("raw.clientes", "id", 5), sql.column("raw.pagamentos", "id", 5)
    sql.edge(left, right, EdgeKind.JOINS_ON, 5)
    renda, limite = (
        sql.column("raw.clientes", "renda", 3),
        sql.column("analytics.base", "limite", 3),
    )
    sql.edge(renda, limite, EdgeKind.DERIVES_FROM, 3)

    py = FactBuilder(FileRef(repo="modelos", path="modelo.py", commit_sha="c2"))
    pjob = py.job()
    py.edge(pjob, py.table("analytics.base", 3), EdgeKind.READS, 3)
    py.edge(pjob, py.table("models.abt", 6), EdgeKind.WRITES, 6)

    tf = FactBuilder(FileRef(repo="infra", path="glue.tf", commit_sha="c3"))
    tjob = tf.job()
    table = tf.table("raw.clientes", 4)
    tf.edge(table, tjob, EdgeKind.DEPLOYED_BY, 4)
    tf.edge(table, tf.table("s3://b/raw/clientes", 4), EdgeKind.STORED_AT, 4)

    llm = FactBuilder(FileRef(repo="risco", path="score.sql", commit_sha="c1"), Origin.LLM)
    llm.edge(
        llm.column("analytics.base", "limite", 9),
        llm.column("models.abt", "lim", 9),
        EdgeKind.DERIVES_FROM,
        9,
    )
    return sql.build() + py.build() + tf.build() + llm.build()


def validation_facts() -> list[Fact]:
    """Fatos que disparam todas as hipóteses do catálogo."""
    a = FactBuilder(FileRef(repo="risco", path="base.sql", commit_sha="aaaaaaaaaa"))
    job = a.job()
    a.edge(job, a.table("analytics.base", 1), EdgeKind.WRITES, 1)
    for out, source in (
        ("id_cliente", "id_cliente"),
        ("dt_ref", "dt_ref"),
        ("dt_evento", "dt_pagamento"),
        ("limite", "renda"),
    ):
        a.edge(
            a.column("raw.clientes", source, 2),
            a.column("analytics.base", out, 2),
            EdgeKind.DERIVES_FROM,
            2,
        )
    a.edge(
        a.column("raw.clientes", "id_cliente", 3),
        a.column("raw.pagamentos", "id_cliente", 3),
        EdgeKind.JOINS_ON,
        3,
    )
    for column in ("status", "renda"):
        a.edge(
            job,
            a.column("raw.clientes", column, 4),
            EdgeKind.FILTERS,
            4,
            detail="status <> 'INADIMPLENTE' AND renda > 0",
        )

    b = FactBuilder(FileRef(repo="outro", path="outra.sql", commit_sha="bbbbbbbbbb"))
    bjob = b.job()
    b.edge(bjob, b.table("analytics.outra", 1), EdgeKind.WRITES, 1)
    b.edge(
        b.column("raw.clientes", "salario", 4),
        b.column("analytics.outra", "limite", 4),
        EdgeKind.DERIVES_FROM,
        4,
    )
    return a.build() + b.build()


class FakeExecutor:
    """Devolve, em ordem, resultados ou levanta erros; registra o SQL recebido."""

    def __init__(self, outcomes: list[object]) -> None:
        self.outcomes = list(outcomes)
        self.received: list[str] = []

    def execute(self, sql: str) -> "QueryResult":
        self.received.append(sql)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        assert isinstance(outcome, QueryResult)
        return outcome


def query_result(rows: int = 1) -> "QueryResult":
    return QueryResult(
        execution_id="exec-1",
        columns=["a", "b"],
        rows=[["1", None]] * rows,
        bytes_scanned=1024,
    )
