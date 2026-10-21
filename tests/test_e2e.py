"""Fluxo completo pela CLI, sem AWS: scan → map → propose → refinar → generate → run → report."""

import json
from pathlib import Path
from typing import TypeVar

import duckdb
import pytest
from conftest import GitRepo
from pydantic import BaseModel
from typer.testing import CliRunner

from dbts.cli import app as cli_module
from dbts.cli.app import app

pytestmark = pytest.mark.integration

runner = CliRunner()

SCORE_SQL = """
create table analytics.base as
with pag as (select p.id_cliente, sum(p.valor) as total from raw.pagamentos p group by 1)
select c.id_cliente, c.renda * 0.3 as limite, x.total
from raw.clientes c
left join pag x on c.id_cliente = x.id_cliente
where c.status <> 'INADIMPLENTE'
"""

T = TypeVar("T", bound=BaseModel)

ANSWERS = {
    "TableSummary": '{"resumo": "R.", "papel": "feature", "pontos_de_atencao": []}',
    "SqlFix": '{"sql": "SELECT COUNT(*) AS n FROM raw.clientes", "explicacao": "tabela errada"}',
    "ReportAnalysis": '{"status": "reprovado", "analise": "Órfãos.", "conclusao": "Ver."}',
}


class SchemaLLM:
    """LLM falso que responde conforme o tipo de saída pedido."""

    name, model = "fake", "fake-model"

    def __init__(self) -> None:
        self.calls: list[str] = []

    def complete(self, prompt: str, schema: type[T]) -> T:
        self.calls.append(schema.__name__)
        return schema.model_validate_json(ANSWERS[schema.__name__])


def _seed(path: Path) -> None:
    connection = duckdb.connect(str(path))
    for schema in ("raw", "analytics", "sandbox"):
        connection.execute(f"CREATE SCHEMA {schema}")
    connection.execute(
        "CREATE TABLE raw.clientes AS SELECT i AS id_cliente, 1000 * i AS renda, "
        "CASE WHEN i % 5 = 0 THEN 'INADIMPLENTE' ELSE 'ATIVO' END AS status FROM range(1, 21) t(i)"
    )
    connection.execute(
        "CREATE TABLE raw.pagamentos AS SELECT 1 + i % 15 AS id_cliente, 10 AS valor "
        "FROM range(1, 61) t(i)"
    )
    connection.close()


def _ids(output: str, marker: str) -> list[str]:
    return [line.split()[0] for line in output.splitlines() if marker in line]


def test_end_to_end_offline(
    tmp_path: Path, git_repo: GitRepo, monkeypatch: pytest.MonkeyPatch
) -> None:
    git_repo("risco", {"score.sql": SCORE_SQL})
    database = tmp_path / "local.duckdb"
    _seed(database)
    llm = SchemaLLM()
    monkeypatch.setattr(cli_module, "_llm", lambda _: llm)
    monkeypatch.setenv("DBTS_MAP_DIR", str(tmp_path / "map"))

    assert runner.invoke(app, ["scan", str(tmp_path / "repos")]).exit_code == 0
    mapped = runner.invoke(app, ["map", "analytics.base", "--enrich"])
    assert mapped.exit_code == 0, mapped.output

    proposed = runner.invoke(app, ["propose", "analytics.base", "--plan", "e2e"]).output
    orphans = _ids(proposed, "órfãs em raw.clientes.id_cliente -> raw.pagamentos")
    assert len(orphans) == 1
    sql_file = tmp_path / "custom.sql"
    sql_file.write_text("SELECT COUNT(*) AS n FROM raw.inexistente")
    custom = runner.invoke(app, ["plan", "add", "e2e", "--title", "C", "--sql-file", str(sql_file)])
    assert runner.invoke(app, ["plan", "accept", "e2e", *orphans]).exit_code == 0
    assert runner.invoke(app, ["generate", "e2e", "--lang", "python"]).exit_code == 0

    args = ["run", "e2e", "--yes", "--local-db", str(database), "--sandbox", "sandbox"]
    ran = runner.invoke(app, args, input="a\ny\n")
    assert ran.exit_code == 0, ran.output

    reports = sorted((tmp_path / "map" / "reports" / "e2e").glob("*.md"))
    orphan_report = next(r.read_text() for r in reports if r.name.startswith(orphans[0]))
    assert "| 20 | 0 | 5 |" in orphan_report  # 20 clientes, nenhum nulo, 5 sem pagamento
    assert "| Status | reprovado |" in orphan_report
    shown = runner.invoke(app, ["plan", "show", "e2e", "--sql"]).output
    assert "FROM raw.clientes" in shown and custom.output.strip() in shown

    assert runner.invoke(app, ["audit", "verify"]).exit_code == 0
    actions = [
        json.loads(line)["action"]
        for line in (tmp_path / "map" / "audit" / "audit.jsonl").read_text().splitlines()
    ]
    for action in ("scan", "enrich", "map", "propose", "plan", "generate", "fix", "execute"):
        assert action in actions
    assert actions.count("report") == 2
    assert llm.calls.count("SqlFix") == 1 and llm.calls.count("ReportAnalysis") == 2
