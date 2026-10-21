from dbts.domain.scan import RepoSnapshot, plan_scan


def _snap(commit: str, blobs: dict[str, str]) -> RepoSnapshot:
    return RepoSnapshot(name="r", path="/r", commit_sha=commit, blobs=blobs)


def test_same_commit_is_noop() -> None:
    plan = plan_scan(_snap("c1", {"a.py": "x"}), "c1", {})
    assert plan.is_noop


def test_first_scan_processes_everything() -> None:
    plan = plan_scan(_snap("c1", {"b.py": "1", "a.py": "2"}), None, {})
    assert plan.changed == ("a.py", "b.py")
    assert plan.removed == ()


def test_new_commit_processes_only_diff() -> None:
    previous = {"same.py": "1", "edited.py": "2", "gone.py": "3"}
    current = {"same.py": "1", "edited.py": "9", "new.py": "4"}
    plan = plan_scan(_snap("c2", current), "c1", previous)
    assert plan.changed == ("edited.py", "new.py")
    assert plan.removed == ("gone.py",)
    assert not plan.is_noop


def test_new_commit_without_relevant_changes_is_noop() -> None:
    assert plan_scan(_snap("c2", {"a.py": "1"}), "c1", {"a.py": "1"}).is_noop


def test_force_reprocesses_everything_even_on_same_commit() -> None:
    plan = plan_scan(
        _snap("c1", {"a.py": "1", "b.py": "2"}), "c1", {"a.py": "1", "old.py": "9"}, force=True
    )
    assert plan.changed == ("a.py", "b.py")
    assert plan.removed == ("old.py",)
