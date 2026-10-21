import subprocess
from pathlib import Path

from conftest import GitRepo

from dbts.mapping import git


def test_discover_repos_only_returns_git_dirs(tmp_path: Path, git_repo: GitRepo) -> None:
    git_repo("b", {"x.py": "1"})
    git_repo("a", {"x.py": "1"})
    (tmp_path / "repos" / "not_a_repo").mkdir()
    (tmp_path / "repos" / "file.txt").write_text("")
    assert [p.name for p in git.discover_repos(tmp_path / "repos")] == ["a", "b"]


def test_snapshot_lists_tracked_blobs_with_relevant_extensions(git_repo: GitRepo) -> None:
    repo = git_repo("r", {"etl/job.py": "print(1)", "q.sql": "select 1", "README.md": "x"})
    snap = git.snapshot(repo)
    assert snap is not None
    assert snap.name == "r"
    assert sorted(snap.blobs) == ["etl/job.py", "q.sql"]
    assert snap.commit_sha == git.head_sha(repo)


def test_snapshot_ignores_uncommitted_changes(git_repo: GitRepo) -> None:
    repo = git_repo("r", {"q.sql": "select 1"})
    (repo / "q.sql").write_text("select 2")
    snap = git.snapshot(repo)
    assert snap is not None
    assert git.read_blob(repo, snap.blobs["q.sql"]) == "select 1"


def test_snapshot_of_repo_without_commits_is_none(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    assert git.snapshot(tmp_path) is None


def test_parse_ls_tree_skips_submodules() -> None:
    output = "160000 commit abc\tvendor/lib.py\n100644 blob def\tmain.py\n"
    assert git._parse_ls_tree(output, {".py"}) == {"main.py": "def"}
