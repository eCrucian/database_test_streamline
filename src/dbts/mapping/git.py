# Só executa o binário git, com argumentos em lista e sem shell.
import subprocess  # nosec B404
from collections.abc import Collection
from pathlib import Path

from dbts.domain.scan import RepoSnapshot

TRACKED_EXTENSIONS = frozenset({".py", ".sql", ".tf", ".js", ".ts", ".ipynb"})


def _git(repo: Path, *args: str) -> str:
    # Argumentos em lista, sem shell; repo e args vêm do próprio código.
    result = subprocess.run(  # nosec B603 B607
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    )
    return result.stdout


def discover_repos(root: Path) -> list[Path]:
    return sorted(p for p in root.iterdir() if (p / ".git").exists())


def head_sha(repo: Path) -> str | None:
    """None quando o repo ainda não tem commits."""
    try:
        return _git(repo, "rev-parse", "HEAD").strip()
    except subprocess.CalledProcessError:
        return None


def _parse_ls_tree(output: str, extensions: Collection[str]) -> dict[str, str]:
    blobs: dict[str, str] = {}
    for line in output.splitlines():
        meta, path = line.split("\t", 1)
        _, kind, sha = meta.split()
        if kind == "blob" and Path(path).suffix in extensions:
            blobs[path] = sha
    return blobs


def snapshot(repo: Path, extensions: Collection[str] = TRACKED_EXTENSIONS) -> RepoSnapshot | None:
    commit = head_sha(repo)
    if commit is None:
        return None
    blobs = _parse_ls_tree(_git(repo, "ls-tree", "-r", commit), extensions)
    return RepoSnapshot(name=repo.name, path=str(repo), commit_sha=commit, blobs=blobs)


def read_blob(repo: Path, blob_sha: str) -> str:
    return _git(repo, "cat-file", "-p", blob_sha)
