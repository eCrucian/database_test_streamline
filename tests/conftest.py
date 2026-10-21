import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

GitRepo = Callable[[str, dict[str, str | None]], Path]


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
        check=True,
        capture_output=True,
    )


@pytest.fixture
def git_repo(tmp_path: Path) -> GitRepo:
    """Cria (ou atualiza) um repo em tmp_path/repos/<nome> e commita. Valor None apaga o arquivo."""

    def commit(name: str, files: dict[str, str | None]) -> Path:
        repo = tmp_path / "repos" / name
        if not repo.exists():
            repo.mkdir(parents=True)
            _git(repo, "init", "-q")
        for rel, content in files.items():
            target = repo / rel
            if content is None:
                target.unlink()
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "c")
        return repo

    return commit
