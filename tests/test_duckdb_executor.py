from pathlib import Path

import duckdb
import pytest

from dbts.adapters.duckdb_executor import DuckDBExecutor
from dbts.domain.execution import QueryFailedError


@pytest.fixture
def database(tmp_path: Path) -> Path:
    path = tmp_path / "local.duckdb"
    connection = duckdb.connect(str(path))
    connection.execute("CREATE SCHEMA raw")
    connection.execute(
        "CREATE TABLE raw.t AS SELECT * FROM (VALUES (1, 'a'), (2, NULL)) v(id, nome)"
    )
    connection.close()
    return path


def test_translates_athena_sql_and_returns_text(database: Path) -> None:
    executor = DuckDBExecutor(database, new_id=lambda: "local-1")
    result = executor.execute(
        "SELECT id, nome, COUNT_IF(nome IS NULL) OVER () AS nulos FROM raw.t ORDER BY id"
    )
    assert result.columns == ["id", "nome", "nulos"]
    assert result.rows == [["1", "a", "1"], ["2", None, "1"]]
    assert (result.execution_id, result.bytes_scanned) == ("local-1", 0)


def test_ctas_and_default_id(database: Path) -> None:
    result = DuckDBExecutor(database).execute("CREATE TABLE raw.u AS SELECT 1 AS a")
    assert result.execution_id.startswith("local-")


def test_engine_error_becomes_query_failed(database: Path) -> None:
    with pytest.raises(QueryFailedError, match="inexistente"):
        DuckDBExecutor(database).execute("SELECT inexistente FROM raw.t")


def test_untranslatable_sql_becomes_query_failed(database: Path) -> None:
    with pytest.raises(QueryFailedError, match="tradução"):
        DuckDBExecutor(database).execute("SELECT (")
