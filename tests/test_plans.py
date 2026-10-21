from pathlib import Path

from factories import validation_facts

from dbts.audit.log import AuditLog
from dbts.domain.models import Origin
from dbts.domain.testing import ProposalStatus
from dbts.mapping.graph import Graph
from dbts.testing.codegen import Language
from dbts.testing.plans import PlanBook


def _book(tmp_path: Path) -> tuple[PlanBook, AuditLog]:
    audit = AuditLog(tmp_path / "audit")
    return PlanBook(tmp_path / "plans", audit, "eduardo"), audit


def _proposed(book: PlanBook) -> str:
    plan = book.propose("Score Base", Graph.from_facts(validation_facts()), "base", {"r": "c" * 10})
    return next(p.id for p in plan.proposals if p.hypothesis_id == "duplicate-keys")


def test_missing_plan_loads_empty(tmp_path: Path) -> None:
    book, _ = _book(tmp_path)
    assert book.load("nada").proposals == []


def test_propose_saves_and_audits(tmp_path: Path) -> None:
    book, audit = _book(tmp_path)
    _proposed(book)
    assert book.path("Score Base") == tmp_path / "plans" / "score-base.json"
    plan = book.load("Score Base")
    assert plan.term == "base" and plan.commits == {"r": "c" * 10}
    (record,) = audit.records()
    assert record.action == "propose"
    assert "proposals=" in (record.detail or "") and "r@cccccccc" in (record.detail or "")


def test_status_and_params_are_persisted_and_audited(tmp_path: Path) -> None:
    book, audit = _book(tmp_path)
    pid = _proposed(book)
    book.set_status("Score Base", [pid], ProposalStatus.ACCEPTED)
    book.set_params("Score Base", pid, {"column": "id"})
    proposal = book.load("Score Base").get(pid)
    assert proposal.status is ProposalStatus.ACCEPTED
    assert proposal.params["column"] == "id"
    records = list(audit.records())[1:]
    assert [(r.origin, r.decision) for r in records] == [
        (Origin.USER, "status=aceito"),
        (Origin.USER, "params column=id"),
    ]


def test_add_custom_is_accepted_user_test(tmp_path: Path) -> None:
    book, _ = _book(tmp_path)
    proposal = book.add_custom("p", "Meu teste", "verifica x", "SELECT 1")
    stored = book.load("p").get(proposal.id)
    assert stored.status is ProposalStatus.ACCEPTED
    assert stored.origin is Origin.USER


def test_generate_writes_files_and_audits(tmp_path: Path) -> None:
    book, audit = _book(tmp_path)
    pid = _proposed(book)
    book.set_status("Score Base", [pid], ProposalStatus.ACCEPTED)

    sql_files = book.generate("Score Base", Language.SQL)
    py_files = book.generate("Score Base", Language.PYTHON)

    assert list(sql_files) == [tmp_path / "plans" / "score-base" / f"{pid}.sql"]
    assert next(iter(py_files)).suffix == ".py"
    assert next(iter(sql_files)).read_text().startswith("-- ")
    assert list(audit.records())[-1].detail == f"plan=Score Base lang=python proposals={pid}"


def test_replace_sql_fixes_template_and_clears_params(tmp_path: Path) -> None:
    book, audit = _book(tmp_path)
    pid = _proposed(book)
    book.replace_sql("Score Base", pid, "SELECT 1")
    proposal = book.load("Score Base").get(pid)
    assert (proposal.template, proposal.params) == ("SELECT 1", {})
    assert list(audit.records())[-1].decision == "sql corrigido"
