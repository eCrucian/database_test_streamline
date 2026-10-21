from datetime import UTC, datetime
from pathlib import Path

from dbts.audit.log import GENESIS, LOG_FILE, AuditEvent, AuditLog
from dbts.domain.models import Origin

FIXED = datetime(2026, 10, 20, tzinfo=UTC)


def _log(tmp_path: Path) -> AuditLog:
    return AuditLog(tmp_path / "audit", clock=lambda: FIXED)


def _event(action: str = "scan") -> AuditEvent:
    return AuditEvent(action=action, user="eduardo", origin=Origin.USER, repo="r", commit_sha="abc")


def test_empty_log_has_no_records_and_is_valid(tmp_path: Path) -> None:
    log = _log(tmp_path)
    assert list(log.records()) == []
    assert log.verify() is None


def test_append_chains_hashes(tmp_path: Path) -> None:
    log = _log(tmp_path)
    first = log.append(_event("scan"))
    second = log.append(_event("execute"))
    assert first.prev_hash == GENESIS
    assert second.prev_hash == first.hash
    assert first.timestamp == FIXED
    assert [r.action for r in log.records()] == ["scan", "execute"]
    assert log.verify() is None


def test_verify_detects_edited_record(tmp_path: Path) -> None:
    log = _log(tmp_path)
    log.append(_event("scan"))
    log.append(_event("execute"))
    path = tmp_path / "audit" / LOG_FILE
    path.write_text(path.read_text().replace('"execute"', '"tampered"'))
    assert log.verify() == 1


def test_verify_detects_removed_record(tmp_path: Path) -> None:
    log = _log(tmp_path)
    for action in ("a", "b", "c"):
        log.append(_event(action))
    path = tmp_path / "audit" / LOG_FILE
    lines = path.read_text().splitlines(keepends=True)
    path.write_text(lines[0] + lines[2])
    assert log.verify() == 1


def test_default_clock_is_utc(tmp_path: Path) -> None:
    record = AuditLog(tmp_path).append(_event())
    assert record.timestamp.tzinfo is UTC
