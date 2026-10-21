import re

from dbts.extract.registry import EXTRACTORS, extractors_fingerprint


def test_fingerprint_is_stable_short_hex() -> None:
    assert extractors_fingerprint() == extractors_fingerprint()
    assert re.fullmatch(r"[0-9a-f]{16}", extractors_fingerprint())


def test_registry_covers_all_tracked_languages() -> None:
    extensions = set().union(*(e.extensions for e in EXTRACTORS))
    assert extensions == {".sql", ".py", ".tf", ".js", ".ts"}
