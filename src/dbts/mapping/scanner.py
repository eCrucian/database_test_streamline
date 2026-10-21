from collections.abc import Sequence
from pathlib import Path

from dbts.audit.log import AuditEvent, AuditLog
from dbts.domain.models import EntityKind, Fact, FileRef, Origin
from dbts.domain.scan import RepoUpdate, ScanPlan, plan_scan
from dbts.mapping import git
from dbts.ports import Extractor, MapStore

FINGERPRINT_KEY = "extractors_fingerprint"


class Scanner:
    """Reprocessa só o que mudou desde o último commit mapeado de cada repo."""

    def __init__(
        self,
        store: MapStore,
        audit: AuditLog,
        user: str,
        extractors: Sequence[Extractor] = (),
        fingerprint: str = "",
    ) -> None:
        self._store = store
        self._audit = audit
        self._user = user
        self._extractors = extractors
        self._fingerprint = fingerprint

    def scan(self, root: Path) -> list[ScanPlan]:
        """Se a impressão digital dos extratores mudou, reprocessa tudo uma vez."""
        force = self._store.get_meta(FINGERPRINT_KEY) != self._fingerprint
        plans = [self.scan_repo(repo, force) for repo in git.discover_repos(root)]
        self._store.set_meta(FINGERPRINT_KEY, self._fingerprint)
        return [plan for plan in plans if plan is not None]

    def scan_repo(self, repo: Path, force: bool = False) -> ScanPlan | None:
        snap = git.snapshot(repo)
        if snap is None:
            return None
        previous = self._store.repo_commit(snap.name)
        blobs = self._store.repo_blobs(snap.name)
        plan = plan_scan(snap, previous, blobs, force=force and previous is not None)
        if plan.is_noop:
            return plan
        facts = self._extract(repo, plan)
        self._store.apply(RepoUpdate(plan=plan, facts=facts))
        self._record(plan, [fact for items in facts.values() for fact in items])
        return plan

    def _extract(self, repo: Path, plan: ScanPlan) -> dict[str, list[Fact]]:
        snap = plan.snapshot
        facts: dict[str, list[Fact]] = {}
        for path in plan.changed:
            extractors = [e for e in self._extractors if Path(path).suffix in e.extensions]
            if not extractors:
                continue
            content = git.read_blob(repo, snap.blobs[path])
            ref = FileRef(repo=snap.name, path=path, commit_sha=snap.commit_sha)
            facts[path] = [fact for e in extractors for fact in e.extract(content, ref)]
        return facts

    def _record(self, plan: ScanPlan, facts: list[Fact]) -> None:
        warnings = sum(1 for f in facts if f.entity and f.entity.kind is EntityKind.WARNING)
        event = AuditEvent(
            action="scan",
            user=self._user,
            origin=Origin.PARSER,
            repo=plan.snapshot.name,
            commit_sha=plan.snapshot.commit_sha,
            detail=(
                f"changed={len(plan.changed)} removed={len(plan.removed)} "
                f"facts={len(facts)} warnings={warnings}"
            ),
        )
        self._audit.append(event)
