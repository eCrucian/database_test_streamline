import pytest

from dbts.domain.models import SourceLocation
from dbts.domain.testing import ProposalStatus, Severity, TestPlan, TestProposal
from dbts.testing.codegen import Language, MissingParamsError, generate


def _proposal(pid: str, status: ProposalStatus, params: dict[str, str]) -> TestProposal:
    return TestProposal(
        id=pid,
        hypothesis_id="duplicate-keys",
        title="Duplicidade",
        description="desc",
        severity=Severity.MEDIUM,
        criterio="vazio",
        template='SELECT ${column} FROM ${table} -- """',
        params=params,
        evidence=[SourceLocation(repo="r", path="a.sql", line=3, commit_sha="abcdef123456")],
        status=status,
    )


def _plan() -> TestPlan:
    full = {"table": "db.t", "column": "id"}
    return TestPlan(
        name="plano",
        proposals=[
            _proposal("aaa", ProposalStatus.ACCEPTED, full),
            _proposal("bbb", ProposalStatus.PROPOSED, {}),
            _proposal("ccc", ProposalStatus.REJECTED, {}),
        ],
    )


def test_sql_has_descriptive_header_and_only_accepted() -> None:
    code = generate(_plan(), Language.SQL)
    assert list(code) == ["aaa"]
    sql = code["aaa"]
    assert sql.startswith("-- " + "=" * 76)
    assert "-- Teste: Duplicidade" in sql
    assert "-- Id: aaa | Hipótese: duplicate-keys | Severidade: media" in sql
    assert "-- Parâmetros: column=id, table=db.t" in sql
    assert "--   r/a.sql:3 @ abcdef12" in sql
    assert sql.endswith('SELECT id FROM db.t -- """\n')


def test_python_wraps_sql_with_awswrangler() -> None:
    code = generate(_plan(), Language.PYTHON)["aaa"]
    assert code.startswith('"""Teste: Duplicidade')
    assert "import awswrangler as wr" in code
    assert 'SELECT id FROM db.t -- \\"\\"\\"' in code
    compile(code, "teste.py", "exec")


def test_missing_params_block_generation() -> None:
    plan = _plan()
    plan.proposals[1].status = ProposalStatus.ACCEPTED
    with pytest.raises(MissingParamsError) as error:
        generate(plan, Language.SQL)
    assert error.value.missing == {"bbb": ["column", "table"]}
    assert "bbb: column, table" in str(error.value)


def test_header_without_params_or_evidence() -> None:
    proposal = _proposal("ddd", ProposalStatus.ACCEPTED, {})
    proposal.template, proposal.evidence = "SELECT 1", []
    sql = generate(TestPlan(name="p", proposals=[proposal]), Language.SQL)["ddd"]
    assert "-- Parâmetros: —" in sql and "--   —" in sql
