import hashlib
from collections.abc import Callable, Iterator
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from dbts.domain.models import Origin

GENESIS = "0" * 64
LOG_FILE = "audit.jsonl"


class AuditEvent(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    action: str
    user: str
    origin: Origin
    repo: str | None = None
    commit_sha: str | None = None
    query_hash: str | None = None
    llm_provider: str | None = None
    llm_model: str | None = None
    decision: str | None = None
    detail: str | None = None


class AuditRecord(AuditEvent):
    timestamp: datetime
    prev_hash: str
    hash: str


def _digest(event: AuditEvent, timestamp: datetime, prev_hash: str) -> str:
    body = event.model_dump_json() + timestamp.isoformat() + prev_hash
    return hashlib.sha256(body.encode()).hexdigest()


def _now() -> datetime:
    return datetime.now(UTC)


class AuditLog:
    """Log append-only em JSON Lines; cada registro encadeia o hash do anterior."""

    def __init__(self, directory: Path, clock: Callable[[], datetime] = _now) -> None:
        self._path = directory / LOG_FILE
        self._clock = clock

    def records(self) -> Iterator[AuditRecord]:
        if not self._path.exists():
            return
        with self._path.open(encoding="utf-8") as handle:
            for line in handle:
                yield AuditRecord.model_validate_json(line)

    def append(self, event: AuditEvent) -> AuditRecord:
        prev_hash = self._last_hash()
        timestamp = self._clock()
        record = AuditRecord(
            **event.model_dump(),
            timestamp=timestamp,
            prev_hash=prev_hash,
            hash=_digest(event, timestamp, prev_hash),
        )
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(record.model_dump_json() + "\n")
        return record

    def verify(self) -> int | None:
        """Devolve o índice do primeiro registro adulterado, ou None se a cadeia é íntegra."""
        prev_hash = GENESIS
        for index, record in enumerate(self.records()):
            event = AuditEvent(**record.model_dump(include=set(AuditEvent.model_fields)))
            expected = _digest(event, record.timestamp, prev_hash)
            if record.prev_hash != prev_hash or record.hash != expected:
                return index
            prev_hash = record.hash
        return None

    def _last_hash(self) -> str:
        last = GENESIS
        for record in self.records():
            last = record.hash
        return last
