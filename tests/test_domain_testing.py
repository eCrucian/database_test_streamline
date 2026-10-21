import pytest

from dbts.domain.testing import Severity, TestPlan, TestProposal, proposal_id


def _proposal(**kwargs: object) -> TestProposal:
    base: dict[str, object] = {
        "id": "x",
        "hypothesis_id": "h",
        "title": "t",
        "description": "d",
        "severity": Severity.LOW,
        "criterio": "c",
        "template": "SELECT ${col} FROM ${table} WHERE x = '$$'\n",
    }
    return TestProposal.model_validate(base | kwargs)


def test_missing_and_render() -> None:
    proposal = _proposal(params={"table": "db.t"})
    assert proposal.missing == ["col"]
    assert proposal.render() == "SELECT ${col} FROM db.t WHERE x = '$'"


def test_proposal_id_is_stable_and_order_independent() -> None:
    assert proposal_id("h", {"a": "1", "b": "2"}) == proposal_id("h", {"b": "2", "a": "1"})
    assert proposal_id("h", {"a": "1"}) != proposal_id("g", {"a": "1"})
    assert len(proposal_id("h", {})) == 8


def test_plan_get() -> None:
    plan = TestPlan(name="p", proposals=[_proposal()])
    assert plan.get("x").title == "t"
    with pytest.raises(KeyError):
        plan.get("nada")
