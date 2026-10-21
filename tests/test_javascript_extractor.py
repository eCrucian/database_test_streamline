from dbts.domain.models import EdgeKind, EntityKind, Fact, FileRef
from dbts.extract.javascript import JavaScriptExtractor

REF = FileRef(repo="front", path="api/score.ts", commit_sha="c")
JOB = "job:front/api/score.ts"


def _extract(code: str) -> list[Fact]:
    return JavaScriptExtractor().extract(code, REF)


def _edges(facts: list[Fact], kind: EdgeKind) -> set[tuple[str, str]]:
    return {(f.edge.source, f.edge.target) for f in facts if f.edge and f.edge.kind is kind}


def test_template_literal_sql_with_interpolation() -> None:
    code = """
const id = req.params.id;
const q = `
  select s.score, s.faixa
  from models.score s
  where s.id_cliente = ${id}
`;
"""
    facts = _extract(code)
    assert _edges(facts, EdgeKind.READS) == {(JOB, "table:models.score")}
    lines = {f.location.line for f in facts if f.edge}
    assert lines == {4}


def test_quoted_strings_and_non_sql_strings() -> None:
    code = """
fetch("/api/clientes");
db.query('insert into logs.acesso select id from raw.sessoes');
const label = "Selecione uma opção";
"""
    facts = _extract(code)
    assert _edges(facts, EdgeKind.WRITES) == {(JOB, "table:logs.acesso")}
    assert _edges(facts, EdgeKind.READS) == {(JOB, "table:raw.sessoes")}


def test_file_without_sql_yields_only_job() -> None:
    assert [f.entity.kind for f in _extract("export const x = 1;") if f.entity] == [EntityKind.JOB]
