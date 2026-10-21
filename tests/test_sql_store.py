from collections.abc import Callable
from pathlib import Path

import pytest

from dbts.adapters.sql_store import DuckDBMapStore, SQLiteMapStore, SqlMapStore, open_store
from dbts.config import resolve_settings
from dbts.domain.models import Entity, EntityKind, Fact, Origin, SourceLocation
from dbts.domain.scan import RepoSnapshot, RepoUpdate, ScanPlan

StoreFactory = Callable[[Path], SqlMapStore]


@pytest.fixture(params=[SQLiteMapStore, DuckDBMapStore], ids=["sqlite", "duckdb"])
def make_store(request: pytest.FixtureRequest) -> StoreFactory:
    factory: StoreFactory = request.param
    return factory


def _fact(path: str, name: str) -> Fact:
    return Fact(
        entity=Entity(id=name, kind=EntityKind.TABLE, name=name),
        location=SourceLocation(repo="r", path=path, line=1, commit_sha="c"),
        origin=Origin.PARSER,
    )


def _update(
    commit: str,
    blobs: dict[str, str],
    changed: tuple[str, ...],
    removed: tuple[str, ...],
    facts: dict[str, list[Fact]],
) -> RepoUpdate:
    snap = RepoSnapshot(name="r", path="/r", commit_sha=commit, blobs=blobs)
    return RepoUpdate(plan=ScanPlan(snapshot=snap, changed=changed, removed=removed), facts=facts)


def test_unknown_repo_is_empty(tmp_path: Path, make_store: StoreFactory) -> None:
    store = make_store(tmp_path / "sub" / "map.db")
    assert store.repo_commit("r") is None
    assert store.repo_blobs("r") == {}
    assert store.facts("r") == []
    assert store.get_annotation("k") is None
    store.close()


def test_apply_replaces_changed_and_drops_removed(tmp_path: Path, make_store: StoreFactory) -> None:
    store = make_store(tmp_path / "map.db")
    first = {"a.sql": [_fact("a.sql", "t1")], "b.sql": [_fact("b.sql", "t2")]}
    store.apply(_update("c1", {"a.sql": "1", "b.sql": "2"}, ("a.sql", "b.sql"), (), first))

    second = {"a.sql": [_fact("a.sql", "t3")]}
    store.apply(_update("c2", {"a.sql": "9"}, ("a.sql",), ("b.sql",), second))

    assert store.repo_commit("r") == "c2"
    assert store.repo_blobs("r") == {"a.sql": "9"}
    assert [f.entity.name for f in store.facts("r") if f.entity] == ["t3"]
    store.close()


def test_apply_with_nothing_changed(tmp_path: Path, make_store: StoreFactory) -> None:
    store = make_store(tmp_path / "map.db")
    store.apply(_update("c1", {}, (), (), {}))
    assert store.repo_commit("r") == "c1"
    store.close()


def test_data_persists_across_connections(tmp_path: Path, make_store: StoreFactory) -> None:
    db = tmp_path / "map.db"
    store = make_store(db)
    store.apply(_update("c1", {"a.sql": "1"}, ("a.sql",), (), {}))
    store.close()
    reopened = make_store(db)
    assert reopened.repo_commit("r") == "c1"
    reopened.close()


def test_all_facts_and_repo_commits(tmp_path: Path, make_store: StoreFactory) -> None:
    store = make_store(tmp_path / "map.db")
    store.apply(_update("c1", {"a.sql": "1"}, ("a.sql",), (), {"a.sql": [_fact("a.sql", "t")]}))
    assert [f.entity.name for f in store.all_facts() if f.entity] == ["t"]
    assert store.repo_commits() == {"r": "c1"}
    store.close()


def test_annotations_upsert(tmp_path: Path, make_store: StoreFactory) -> None:
    store = make_store(tmp_path / "map.db")
    store.put_annotation("k", "table:t", "m", '{"a": 1}')
    store.put_annotation("k", "table:t", "m", '{"a": 2}')
    assert store.get_annotation("k") == '{"a": 2}'
    store.close()


def test_failed_apply_rolls_back(
    tmp_path: Path, make_store: StoreFactory, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = make_store(tmp_path / "map.db")
    store.apply(_update("c1", {"a.sql": "1"}, ("a.sql",), (), {"a.sql": [_fact("a.sql", "t")]}))
    calls = 0
    original = store._many

    def failing(sql: str, rows: object) -> None:
        nonlocal calls
        calls += 1
        if calls == 3:
            raise RuntimeError("falha no meio")
        original(sql, rows)  # type: ignore[arg-type]

    monkeypatch.setattr(store, "_many", failing)
    with pytest.raises(RuntimeError):
        store.apply(_update("c2", {"a.sql": "2"}, ("a.sql",), (), {}))

    assert store.repo_commit("r") == "c1"
    assert store.repo_blobs("r") == {"a.sql": "1"}
    assert len(store.facts("r")) == 1
    store.close()


def test_open_store_by_setting(tmp_path: Path) -> None:
    sqlite = open_store(resolve_settings({}, tmp_path))
    duck = open_store(resolve_settings({"DBTS_STORE": "duckdb"}, tmp_path))
    assert isinstance(sqlite, SQLiteMapStore) and isinstance(duck, DuckDBMapStore)
    assert (tmp_path / ".dbts" / "map.sqlite").exists()
    assert (tmp_path / ".dbts" / "map.duckdb").exists()
    sqlite.close()
    duck.close()


def test_meta_upsert(tmp_path: Path, make_store: StoreFactory) -> None:
    store = make_store(tmp_path / "map.db")
    assert store.get_meta("k") is None
    store.set_meta("k", "1")
    store.set_meta("k", "2")
    assert store.get_meta("k") == "2"
    store.close()
