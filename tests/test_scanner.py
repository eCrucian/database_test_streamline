import subprocess
from pathlib import Path

from conftest import GitRepo

from dbts.adapters.sql_store import SQLiteMapStore
from dbts.audit.log import AuditLog
from dbts.extract.sql import SQLExtractor
from dbts.mapping.scanner import Scanner


def _scanner(tmp_path: Path) -> tuple[Scanner, AuditLog]:
    audit = AuditLog(tmp_path / "audit")
    return Scanner(SQLiteMapStore(tmp_path / "map.sqlite"), audit, "eduardo"), audit


def test_first_scan_maps_all_repos_and_audits(tmp_path: Path, git_repo: GitRepo) -> None:
    git_repo("a", {"q.sql": "select 1"})
    git_repo("b", {"j.py": "x = 1"})
    scanner, audit = _scanner(tmp_path)

    plans = scanner.scan(tmp_path / "repos")

    assert [(p.snapshot.name, p.changed) for p in plans] == [("a", ("q.sql",)), ("b", ("j.py",))]
    records = list(audit.records())
    assert [(r.repo, r.action, r.user) for r in records] == [
        ("a", "scan", "eduardo"),
        ("b", "scan", "eduardo"),
    ]
    assert records[0].commit_sha == plans[0].snapshot.commit_sha


def test_rescan_without_new_commit_is_noop_and_not_audited(
    tmp_path: Path, git_repo: GitRepo
) -> None:
    git_repo("a", {"q.sql": "select 1"})
    scanner, audit = _scanner(tmp_path)
    scanner.scan(tmp_path / "repos")

    plans = scanner.scan(tmp_path / "repos")

    assert plans[0].is_noop
    assert len(list(audit.records())) == 1


def test_new_commit_reprocesses_only_diff(tmp_path: Path, git_repo: GitRepo) -> None:
    git_repo("a", {"q.sql": "select 1", "keep.py": "x", "old.py": "y"})
    scanner, _ = _scanner(tmp_path)
    scanner.scan(tmp_path / "repos")
    git_repo("a", {"q.sql": "select 2", "old.py": None})

    plan = scanner.scan(tmp_path / "repos")[0]

    assert plan.changed == ("q.sql",)
    assert plan.removed == ("old.py",)


def test_scan_extracts_facts_only_for_matching_extensions(
    tmp_path: Path, git_repo: GitRepo
) -> None:
    git_repo("a", {"q.sql": "insert into t2 select x from t1;\nselec from;", "j.py": "x = 1"})
    store = SQLiteMapStore(tmp_path / "map.sqlite")
    audit = AuditLog(tmp_path / "audit")
    Scanner(store, audit, "u", [SQLExtractor()]).scan(tmp_path / "repos")

    facts = store.facts("a")
    assert {f.location.path for f in facts} == {"q.sql"}
    assert any(f.edge and f.edge.target == "table:t2" for f in facts)
    assert f"facts={len(facts)} warnings=1" in (next(audit.records()).detail or "")


def test_repo_without_commits_is_skipped(tmp_path: Path, git_repo: GitRepo) -> None:
    git_repo("a", {"q.sql": "select 1"})
    subprocess.run(["git", "init", "-q", str(tmp_path / "repos" / "empty")], check=True)
    scanner, _ = _scanner(tmp_path)
    assert [p.snapshot.name for p in scanner.scan(tmp_path / "repos")] == ["a"]


def test_new_extractor_fingerprint_forces_full_rescan_once(
    tmp_path: Path, git_repo: GitRepo
) -> None:
    git_repo("a", {"q.sql": "insert into t2 select x from t1", "j.py": "x = 1"})
    store = SQLiteMapStore(tmp_path / "map.sqlite")
    audit = AuditLog(tmp_path / "audit")
    root = tmp_path / "repos"
    Scanner(store, audit, "u", [SQLExtractor()], "v1").scan(root)

    same = Scanner(store, audit, "u", [SQLExtractor()], "v1").scan(root)
    changed = Scanner(store, audit, "u", [SQLExtractor()], "v2").scan(root)
    after = Scanner(store, audit, "u", [SQLExtractor()], "v2").scan(root)

    assert same[0].is_noop
    assert changed[0].changed == ("j.py", "q.sql")
    assert after[0].is_noop
    assert store.get_meta("extractors_fingerprint") == "v2"
