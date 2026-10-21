"""Guarda de segurança e identidade (hash) de queries a executar."""

import hashlib

import sqlglot
from sqlglot import exp
from sqlglot.errors import SqlglotError

from dbts.domain.execution import QueryFailedError
from dbts.extract.sql import DIALECT


class GuardError(QueryFailedError):
    """Query bloqueada pela guarda: nunca chega à AWS."""


def _single_statement(sql: str) -> exp.Expr:
    try:
        trees = [tree for tree in sqlglot.parse(sql, read=DIALECT) if tree is not None]
    except SqlglotError as error:
        raise GuardError(f"SQL inválido: {error}") from error
    if len(trees) != 1:
        raise GuardError(f"esperado 1 statement, encontrados {len(trees)}")
    return trees[0]


def ensure_safe(sql: str, sandbox: str) -> None:
    """Só SELECT, ou CREATE TABLE AS no schema sandbox do usuário."""
    tree = _single_statement(sql)
    if isinstance(tree, exp.Query):
        return
    target = tree.this.find(exp.Table) if isinstance(tree, exp.Create) else None
    is_ctas = isinstance(tree, exp.Create) and isinstance(tree.expression, exp.Query)
    if is_ctas and target is not None and target.db.lower() == sandbox.lower():
        return
    raise GuardError(f"permitido apenas SELECT ou CREATE TABLE AS em '{sandbox}'")


def normalize(sql: str) -> str:
    """Forma canônica sem comentários: o cabeçalho não altera a identidade da query."""
    return _single_statement(sql).sql(dialect=DIALECT, comments=False)


def query_hash(sql: str) -> str:
    return hashlib.sha256(normalize(sql).encode()).hexdigest()
