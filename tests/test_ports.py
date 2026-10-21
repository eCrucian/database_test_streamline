from pathlib import Path

from dbts.adapters.fake_llm import FakeLLMProvider
from dbts.adapters.ollama import OllamaProvider
from dbts.adapters.sql_store import DuckDBMapStore, SQLiteMapStore
from dbts.extract.sql import SQLExtractor
from dbts.ports import Extractor, LLMProvider, MapStore


def test_adapters_satisfy_llm_provider() -> None:
    providers: list[LLMProvider] = [FakeLLMProvider([]), OllamaProvider("m")]
    assert [p.name for p in providers] == ["fake", "ollama"]


def test_sql_satisfies_extractor() -> None:
    extractors: list[Extractor] = [SQLExtractor()]
    assert ".sql" in extractors[0].extensions


def test_sqlite_satisfies_map_store(tmp_path: Path) -> None:
    stores: list[MapStore] = [
        SQLiteMapStore(tmp_path / "m.sqlite"),
        DuckDBMapStore(tmp_path / "m.duckdb"),
    ]
    assert [s.repo_commit("x") for s in stores] == [None, None]
