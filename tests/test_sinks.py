from datetime import UTC, datetime
from pathlib import Path

import pyarrow.parquet as pq
from factories import FakeExecutor, query_result

from dbts.adapters.sinks import AthenaTableSink, CsvSink, ParquetSink


def test_csv_sink(tmp_path: Path) -> None:
    location = CsvSink(tmp_path).write("h", "SELECT 1", query_result(2))
    assert location == str(tmp_path / "h" / "exec-1.csv")
    assert Path(location).read_text().splitlines() == ["a,b", "1,", "1,"]


def test_parquet_sink_keeps_nulls_and_duplicate_names(tmp_path: Path) -> None:
    result = query_result(1).model_copy(update={"columns": ["a", "a"]})
    location = ParquetSink(tmp_path).write("h", "SELECT 1", result)
    table = pq.read_table(location)
    assert table.column_names == ["a", "a_2"]
    assert table.to_pylist() == [{"a": "1", "a_2": None}]


def test_unique_names() -> None:
    from dbts.adapters.sinks import unique_names

    assert unique_names(["a", "b", "a", "a"]) == ["a", "b", "a_2", "a_3"]


def test_table_sink_runs_ctas_in_sandbox() -> None:
    executor = FakeExecutor([query_result()])
    clock = datetime(2026, 10, 20, 9, 30, 5, tzinfo=UTC)
    sink = AthenaTableSink(executor, "sb", clock=lambda: clock)
    location = sink.write("abcdef1234567890", "SELECT 1", query_result())
    assert location == "sb.dbts_abcdef123456_20261020093005"
    assert executor.received == [f"CREATE TABLE {location} AS\nSELECT 1"]


def test_table_sink_default_clock() -> None:
    sink = AthenaTableSink(FakeExecutor([query_result()]), "sb")
    assert sink.write("h" * 12, "SELECT 1", query_result()).startswith("sb.dbts_hhhhhhhhhhhh_20")
