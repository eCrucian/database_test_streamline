import pytest
from factories import validation_facts

from dbts.domain.testing import Hypothesis, ProposalStatus, TestPlan
from dbts.mapping.graph import Graph
from dbts.testing import engine
from dbts.testing.engine import load_catalog, merge_plan, propose


def test_catalog_loads_all_hypotheses() -> None:
    ids = [h.id for h in load_catalog()]
    assert ids == [
        "definition-drift",
        "duplicate-keys",
        "join-fanout",
        "null-key-loss",
        "sample-filter-bias",
        "temporal-leakage",
    ]


def test_catalog_rejects_unknown_pattern(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(engine, "MATCHERS", {})
    with pytest.raises(ValueError, match="padrão desconhecido"):
        load_catalog()


def test_propose_fills_params_and_text() -> None:
    proposals = propose(Graph.from_facts(validation_facts()), load_catalog())
    by_hypothesis = {p.hypothesis_id: p for p in proposals}
    assert set(by_hypothesis) == {h.id for h in load_catalog()}
    fanout = by_hypothesis["join-fanout"]
    assert (
        fanout.title
        == "Unicidade das chaves em raw.clientes.id_cliente = raw.pagamentos.id_cliente"
    )
    assert fanout.missing == []
    assert "FROM raw.pagamentos" in fanout.render()
    leakage = by_hypothesis["temporal-leakage"]
    assert leakage.missing == ["event_col", "ref_col"]
    assert "dt_evento, dt_ref" in leakage.description


def test_merge_plan_preserves_user_decisions_and_old_proposals() -> None:
    fresh = propose(Graph.from_facts(validation_facts()), load_catalog())
    first, second = fresh[0], fresh[1]
    decided = first.model_copy(update={"status": ProposalStatus.ACCEPTED, "params": {"k": "v"}})
    gone = second.model_copy(update={"id": "antiga"})
    plan = TestPlan(name="p", proposals=[decided, gone])

    merged = merge_plan(plan, fresh)

    assert merged.get(first.id).status is ProposalStatus.ACCEPTED
    assert merged.get(first.id).params == {"k": "v"}
    assert merged.get("antiga") == gone
    assert len(merged.proposals) == len(fresh) + 1


@pytest.mark.parametrize("hypothesis", load_catalog(), ids=lambda h: h.id)
def test_catalog_sql_is_valid_athena_when_filled(hypothesis: Hypothesis) -> None:
    from string import Template

    import sqlglot

    names = Template(hypothesis.sql).get_identifiers()
    sql = Template(hypothesis.sql).substitute({name: f"x_{name}" for name in names})
    assert sqlglot.parse_one(sql, read="athena") is not None
