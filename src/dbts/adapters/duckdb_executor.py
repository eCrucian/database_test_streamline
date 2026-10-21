"""Executor local: traduz o SQL do Athena para DuckDB e roda sobre um banco local.

Serve para ensaiar testes offline (dados de amostra) antes de gastar no Athena.
O resultado imita o Athena: valores como texto e `bytes_scanned` = 0.
"""

import uuid
from collections.abc import Callable
from pathlib import Path

import duckdb
import sqlglot
from sqlglot.errors import SqlglotError

from dbts.domain.execution import QueryFailedError, QueryResult
from dbts.extract.sql import DIALECT


def _execution_id() -> str:
    return f"local-{uuid.uuid4().hex[:12]}"


def _text(value: object) -> str | None:
    return None if value is None else str(value)


class DuckDBExecutor:
    def __init__(self, database: Path, new_id: Callable[[], str] = _execution_id) -> None:
        self._database = database
        self._new_id = new_id

    def execute(self, sql: str) -> QueryResult:
        try:
            translated = sqlglot.transpile(sql, read=DIALECT, write="duckdb")[0]
        except SqlglotError as error:
            raise QueryFailedError(f"tradução para DuckDB falhou: {error}") from error
        connection = duckdb.connect(str(self._database))
        try:
            cursor = connection.execute(translated)
            columns = [column[0] for column in cursor.description or []]
            rows = [[_text(value) for value in row] for row in cursor.fetchall()]
        except duckdb.Error as error:
            raise QueryFailedError(str(error)) from error
        finally:
            connection.close()
        return QueryResult(execution_id=self._new_id(), columns=columns, rows=rows, bytes_scanned=0)
