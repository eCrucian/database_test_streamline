from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict

from dbts.domain.models import Fact


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class RepoSnapshot(_Frozen):
    """Estado de um repo em um commit: caminho -> hash do blob."""

    name: str
    path: str
    commit_sha: str
    blobs: dict[str, str]


class ScanPlan(_Frozen):
    snapshot: RepoSnapshot
    changed: tuple[str, ...]
    removed: tuple[str, ...]

    @property
    def is_noop(self) -> bool:
        return not self.changed and not self.removed


class RepoUpdate(_Frozen):
    """Mudança atômica a aplicar no MapStore para um repo."""

    plan: ScanPlan
    facts: dict[str, list[Fact]]


def plan_scan(
    snapshot: RepoSnapshot,
    previous_commit: str | None,
    previous_blobs: Mapping[str, str],
    force: bool = False,
) -> ScanPlan:
    """`force` reprocessa todos os arquivos (ex.: a lógica dos extratores mudou)."""
    if previous_commit == snapshot.commit_sha and not force:
        return ScanPlan(snapshot=snapshot, changed=(), removed=())
    changed = sorted(
        p for p, sha in snapshot.blobs.items() if force or previous_blobs.get(p) != sha
    )
    removed = sorted(set(previous_blobs) - set(snapshot.blobs))
    return ScanPlan(snapshot=snapshot, changed=tuple(changed), removed=tuple(removed))
