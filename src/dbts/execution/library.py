"""Biblioteca de queries que executaram com sucesso, identificadas pelo hash do SQL normalizado."""

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from dbts.execution.sql import query_hash

INDEX_FILE = "runs.jsonl"


class RunRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    query_hash: str
    plan: str | None
    proposal_id: str | None
    execution_id: str
    executed_at: datetime
    bytes_scanned: int
    rows: int
    fixes: int
    query_path: str
    results: dict[str, str]


class QueryLibrary:
    def __init__(self, directory: Path) -> None:
        self._dir = directory

    def save_query(self, sql: str, header: list[str]) -> tuple[str, Path]:
        digest = query_hash(sql)
        path = self._dir / f"{digest}.sql"
        rule = "-- " + "=" * 76
        lines = [rule, *(f"-- {line}" for line in [*header, f"Hash: {digest}"]), rule]
        self._dir.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join([*lines, sql.strip(), ""]), encoding="utf-8")
        return digest, path

    def record(self, entry: RunRecord) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)
        with (self._dir / INDEX_FILE).open("a", encoding="utf-8") as handle:
            handle.write(entry.model_dump_json() + "\n")

    def runs(self) -> list[RunRecord]:
        path = self._dir / INDEX_FILE
        if not path.exists():
            return []
        lines = path.read_text(encoding="utf-8").splitlines()
        return [RunRecord.model_validate_json(line) for line in lines]
