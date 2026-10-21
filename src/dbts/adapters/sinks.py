"""Destinos de resultado. Cada um devolve a localização onde gravou."""

import csv
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from dbts.domain.execution import QueryResult
from dbts.ports import QueryExecutor


class CsvSink:
    name = "csv"

    def __init__(self, directory: Path) -> None:
        self._dir = directory

    def write(self, digest: str, sql: str, result: QueryResult) -> str:
        path = self._dir / digest / f"{result.execution_id}.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(result.columns)
            writer.writerows(result.rows)
        return str(path)


def unique_names(names: list[str]) -> list[str]:
    """Parquet com nomes repetidos não é legível: `a, a` vira `a, a_2`."""
    seen: dict[str, int] = {}
    unique = []
    for name in names:
        seen[name] = seen.get(name, 0) + 1
        unique.append(name if seen[name] == 1 else f"{name}_{seen[name]}")
    return unique


class ParquetSink:
    """Colunas como string: o Athena devolve tudo como texto pela API de resultados."""

    name = "parquet"

    def __init__(self, directory: Path) -> None:
        self._dir = directory

    def write(self, digest: str, sql: str, result: QueryResult) -> str:
        path = self._dir / digest / f"{result.execution_id}.parquet"
        path.parent.mkdir(parents=True, exist_ok=True)
        arrays = [
            pa.array([row[i] for row in result.rows], type=pa.string())
            for i in range(len(result.columns))
        ]
        pq.write_table(pa.Table.from_arrays(arrays, names=unique_names(result.columns)), path)
        return str(path)


def _now() -> datetime:
    return datetime.now(UTC)


class AthenaTableSink:
    """Materializa o resultado como tabela no schema sandbox via CTAS (reexecuta a query)."""

    name = "table"

    def __init__(
        self, executor: QueryExecutor, sandbox: str, clock: Callable[[], datetime] = _now
    ) -> None:
        self._executor = executor
        self._sandbox = sandbox
        self._clock = clock

    def write(self, digest: str, sql: str, result: QueryResult) -> str:
        table = f"{self._sandbox}.dbts_{digest[:12]}_{self._clock():%Y%m%d%H%M%S}"
        self._executor.execute(f"CREATE TABLE {table} AS\n{sql}")
        return table
