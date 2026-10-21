"""MapStore em SQL embutido: mesmo esquema e consultas para SQLite e DuckDB."""

import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Protocol

import duckdb

from dbts.config import Settings, StoreName
from dbts.domain.models import Fact
from dbts.domain.scan import RepoUpdate

SCHEMA = (
    """CREATE TABLE IF NOT EXISTS repos (
        name TEXT PRIMARY KEY,
        path TEXT NOT NULL,
        commit_sha TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS files (
        repo TEXT NOT NULL,
        path TEXT NOT NULL,
        blob_sha TEXT NOT NULL,
        PRIMARY KEY (repo, path)
    )""",
    """CREATE TABLE IF NOT EXISTS facts (
        repo TEXT NOT NULL,
        path TEXT NOT NULL,
        payload TEXT NOT NULL
    )""",
    "CREATE INDEX IF NOT EXISTS facts_repo_path ON facts (repo, path)",
    "CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)",
    """CREATE TABLE IF NOT EXISTS annotations (
        key TEXT PRIMARY KEY,
        entity_id TEXT NOT NULL,
        model TEXT NOT NULL,
        payload TEXT NOT NULL
    )""",
)


class _Cursor(Protocol):
    def fetchone(self) -> Any: ...

    def fetchall(self) -> list[Any]: ...


class _Connection(Protocol):
    def execute(self, sql: str, parameters: Sequence[object] = ..., /) -> _Cursor: ...

    def executemany(self, sql: str, parameters: Sequence[Sequence[object]], /) -> object: ...

    def close(self) -> None: ...


class SqlMapStore:
    def __init__(self, connection: _Connection) -> None:
        self._conn = connection
        for statement in SCHEMA:
            self._conn.execute(statement)

    def close(self) -> None:
        self._conn.close()

    def repo_commit(self, repo: str) -> str | None:
        row = self._conn.execute("SELECT commit_sha FROM repos WHERE name = ?", (repo,)).fetchone()
        return None if row is None else str(row[0])

    def repo_blobs(self, repo: str) -> dict[str, str]:
        rows = self._conn.execute("SELECT path, blob_sha FROM files WHERE repo = ?", (repo,))
        return {path: sha for path, sha in rows.fetchall()}

    def facts(self, repo: str) -> list[Fact]:
        rows = self._conn.execute(
            "SELECT payload FROM facts WHERE repo = ? ORDER BY rowid", (repo,)
        )
        return [Fact.model_validate_json(payload) for (payload,) in rows.fetchall()]

    def all_facts(self) -> list[Fact]:
        rows = self._conn.execute("SELECT payload FROM facts ORDER BY rowid", ())
        return [Fact.model_validate_json(payload) for (payload,) in rows.fetchall()]

    def repo_commits(self) -> dict[str, str]:
        rows = self._conn.execute("SELECT name, commit_sha FROM repos ORDER BY name", ())
        return {name: sha for name, sha in rows.fetchall()}

    def get_meta(self, key: str) -> str | None:
        row = self._conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
        return None if row is None else str(row[0])

    def set_meta(self, key: str, value: str) -> None:
        with self._transaction():
            self._conn.execute("INSERT OR REPLACE INTO meta VALUES (?, ?)", (key, value))

    def get_annotation(self, key: str) -> str | None:
        row = self._conn.execute("SELECT payload FROM annotations WHERE key = ?", (key,)).fetchone()
        return None if row is None else str(row[0])

    def put_annotation(self, key: str, entity_id: str, model: str, payload: str) -> None:
        with self._transaction():
            self._conn.execute(
                "INSERT OR REPLACE INTO annotations VALUES (?, ?, ?, ?)",
                (key, entity_id, model, payload),
            )

    def apply(self, update: RepoUpdate) -> None:
        snap = update.plan.snapshot
        stale = [(snap.name, p) for p in (*update.plan.changed, *update.plan.removed)]
        files = [(snap.name, p, snap.blobs[p]) for p in update.plan.changed]
        facts = [
            (snap.name, path, fact.model_dump_json())
            for path, items in update.facts.items()
            for fact in items
        ]
        with self._transaction():
            self._many("DELETE FROM files WHERE repo = ? AND path = ?", stale)
            self._many("DELETE FROM facts WHERE repo = ? AND path = ?", stale)
            self._many("INSERT INTO files VALUES (?, ?, ?)", files)
            self._many("INSERT INTO facts VALUES (?, ?, ?)", facts)
            self._conn.execute(
                "INSERT OR REPLACE INTO repos VALUES (?, ?, ?)",
                (snap.name, snap.path, snap.commit_sha),
            )

    def _many(self, sql: str, rows: Sequence[Sequence[object]]) -> None:
        """DuckDB não aceita executemany com lista vazia."""
        if rows:
            self._conn.executemany(sql, rows)

    @contextmanager
    def _transaction(self) -> Iterator[None]:
        self._conn.execute("BEGIN TRANSACTION", ())
        try:
            yield
        except BaseException:
            self._conn.execute("ROLLBACK", ())
            raise
        self._conn.execute("COMMIT", ())


def _parent(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


class SQLiteMapStore(SqlMapStore):
    def __init__(self, db_path: Path) -> None:
        # Autocommit: as transações são abertas explicitamente em _transaction.
        super().__init__(sqlite3.connect(_parent(db_path), isolation_level=None))


class DuckDBMapStore(SqlMapStore):
    def __init__(self, db_path: Path) -> None:
        super().__init__(duckdb.connect(str(_parent(db_path))))


def open_store(settings: Settings) -> SqlMapStore:
    if settings.store is StoreName.DUCKDB:
        return DuckDBMapStore(settings.map_dir / "map.duckdb")
    return SQLiteMapStore(settings.map_dir / "map.sqlite")
