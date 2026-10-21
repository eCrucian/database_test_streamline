from pathlib import Path

from factories import pipeline_facts

from dbts.adapters.fake_llm import FakeLLMProvider
from dbts.adapters.sql_store import SQLiteMapStore
from dbts.audit.log import AuditLog
from dbts.domain.enrichment import TableRole
from dbts.enrich.tables import TableEnricher
from dbts.mapping.graph import Graph

ANSWER = '{"resumo": "Base de score.", "papel": "intermediaria", "pontos_de_atencao": ["chave"]}'


def _graph() -> Graph:
    return Graph.from_facts(pipeline_facts()).around({"table:analytics.base"}, 0)


def test_summarize_calls_llm_with_card_and_audits(tmp_path: Path) -> None:
    llm = FakeLLMProvider([ANSWER])
    audit = AuditLog(tmp_path / "audit")
    store = SQLiteMapStore(tmp_path / "m.sqlite")

    summaries = TableEnricher(llm, store, audit, "u").summarize(_graph())

    assert summaries["table:analytics.base"].papel is TableRole.INTERMEDIATE
    assert "### `analytics.base`" in llm.prompts[0]
    (record,) = audit.records()
    assert (record.action, record.llm_provider, record.llm_model) == (
        "enrich",
        "fake",
        "fake-model",
    )
    assert "entity=table:analytics.base" in (record.detail or "")


def test_second_run_uses_cache_without_llm_or_audit(tmp_path: Path) -> None:
    audit = AuditLog(tmp_path / "audit")
    store = SQLiteMapStore(tmp_path / "m.sqlite")
    TableEnricher(FakeLLMProvider([ANSWER]), store, audit, "u").summarize(_graph())

    empty = FakeLLMProvider([])
    summaries = TableEnricher(empty, store, audit, "u").summarize(_graph())

    assert summaries["table:analytics.base"].resumo == "Base de score."
    assert empty.prompts == []
    assert len(list(audit.records())) == 1


def test_different_model_misses_cache(tmp_path: Path) -> None:
    audit = AuditLog(tmp_path / "audit")
    store = SQLiteMapStore(tmp_path / "m.sqlite")
    TableEnricher(FakeLLMProvider([ANSWER]), store, audit, "u").summarize(_graph())
    other = FakeLLMProvider([ANSWER], model="outro")
    TableEnricher(other, store, audit, "u").summarize(_graph())
    assert len(other.prompts) == 1
