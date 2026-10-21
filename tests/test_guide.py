from pathlib import Path

from factories import pipeline_facts

from dbts.adapters.sql_store import SQLiteMapStore
from dbts.audit.log import AuditLog
from dbts.domain.scan import RepoSnapshot, RepoUpdate, ScanPlan
from dbts.mapping.guide import build_guide, slugify


def _store(tmp_path: Path) -> SQLiteMapStore:
    store = SQLiteMapStore(tmp_path / "map.sqlite")
    snap = RepoSnapshot(name="risco", path="/r", commit_sha="c1aaaaaaaa", blobs={"x.sql": "b"})
    plan = ScanPlan(snapshot=snap, changed=("x.sql",), removed=())
    store.apply(RepoUpdate(plan=plan, facts={"x.sql": pipeline_facts()}))
    return store


def test_slugify() -> None:
    assert slugify("Analytics.Base Score") == "analytics-base-score"
    assert slugify("***") == "mapa"


def test_guide_around_term_writes_files_and_audits(tmp_path: Path) -> None:
    audit = AuditLog(tmp_path / "audit")
    result = build_guide(_store(tmp_path), tmp_path / "guides", audit, "u", "analytics.base", 1)
    assert result is not None
    assert result.markdown == tmp_path / "guides" / "analytics-base.md"
    assert "### `analytics.base`" in result.markdown.read_text()
    assert result.json.exists()
    (record,) = audit.records()
    assert record.action == "map"
    assert "term=analytics.base depth=1" in (record.detail or "")
    assert "risco@c1aaaaaa" in (record.detail or "")


def test_full_map(tmp_path: Path) -> None:
    audit = AuditLog(tmp_path / "audit")
    result = build_guide(_store(tmp_path), tmp_path / "guides", audit, "u", None)
    assert result is not None
    assert result.markdown.name == "mapa-completo.md"
    assert "### `models.abt`" in result.markdown.read_text()


def test_unknown_term_returns_none_without_audit(tmp_path: Path) -> None:
    audit = AuditLog(tmp_path / "audit")
    assert build_guide(_store(tmp_path), tmp_path / "g", audit, "u", "inexistente") is None
    assert list(audit.records()) == []


def test_guide_with_enricher_includes_summaries(tmp_path: Path) -> None:
    from dbts.adapters.fake_llm import FakeLLMProvider
    from dbts.enrich.tables import TableEnricher

    store = _store(tmp_path)
    audit = AuditLog(tmp_path / "audit")
    answer = '{"resumo": "R.", "papel": "saida", "pontos_de_atencao": []}'
    enricher = TableEnricher(FakeLLMProvider([answer]), store, audit, "u")
    result = build_guide(store, tmp_path / "g", audit, "u", "models.abt", 0, enricher)
    assert result is not None
    assert "> **Resumo (LLM, hipótese):** R." in result.markdown.read_text()
