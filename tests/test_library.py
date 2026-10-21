from datetime import UTC, datetime
from pathlib import Path

from dbts.execution.library import QueryLibrary, RunRecord
from dbts.execution.sql import query_hash


def test_save_query_with_header_named_by_hash(tmp_path: Path) -> None:
    library = QueryLibrary(tmp_path / "q")
    digest, path = library.save_query("SELECT a FROM t\n", ["Teste: x", "Critério: y"])
    assert digest == query_hash("SELECT a FROM t")
    assert path == tmp_path / "q" / f"{digest}.sql"
    text = path.read_text()
    assert "-- Teste: x\n-- Critério: y\n" in text and f"-- Hash: {digest}" in text
    assert text.endswith("SELECT a FROM t\n")
    assert query_hash(text) == digest


def test_index(tmp_path: Path) -> None:
    library = QueryLibrary(tmp_path)
    assert library.runs() == []
    record = RunRecord(
        query_hash="h",
        plan="p",
        proposal_id="x",
        execution_id="e",
        executed_at=datetime(2026, 1, 1, tzinfo=UTC),
        bytes_scanned=1,
        rows=2,
        fixes=0,
        query_path="q.sql",
        results={"csv": "r.csv"},
    )
    library.record(record)
    assert library.runs() == [record]
