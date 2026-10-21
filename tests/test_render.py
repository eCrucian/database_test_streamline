import json

from factories import pipeline_facts

from dbts.domain.models import EdgeKind, FileRef
from dbts.extract.facts import FactBuilder
from dbts.mapping.graph import Graph
from dbts.mapping.render import render_json, render_markdown, render_mermaid

COMMITS = {"risco": "c1aaaaaaaaaa", "modelos": "c2bbbbbbbbbb"}


def _graph() -> Graph:
    return Graph.from_facts(pipeline_facts())


def test_mermaid_has_jobs_tables_and_directed_flow() -> None:
    mermaid = render_mermaid(_graph())
    assert mermaid.startswith("flowchart LR")
    assert '["risco/score.sql"]' in mermaid
    assert '[("analytics.base")]' in mermaid
    assert "-->|reads|" in mermaid and "-->|writes|" in mermaid
    assert "-.->|stored_at|" in mermaid and "-.->|deployed_by|" in mermaid
    assert "column" not in mermaid


def test_mermaid_reads_point_from_table_to_job() -> None:
    builder = FactBuilder(FileRef(repo="r", path="j.py", commit_sha="c"))
    builder.edge(builder.job(), builder.table("t", 1), EdgeKind.READS, 1)
    lines = render_mermaid(Graph.from_facts(builder.build())).splitlines()
    assert lines[-1] == "  n1 -->|reads| n0"


def test_mermaid_skips_edges_outside_flow() -> None:
    builder = FactBuilder(FileRef(repo="r", path="j.py", commit_sha="c"))
    builder.edge("job:fora", builder.table("t", 1), EdgeKind.READS, 1)
    assert "-->" not in render_mermaid(Graph.from_facts(builder.build()))


def test_markdown_table_card() -> None:
    md = render_markdown(_graph(), "base", COMMITS)
    assert md.startswith("# Mapa: base")
    assert "`modelos@c2bbbbbb`, `risco@c1aaaaaa`" in md
    assert "```mermaid" in md
    assert "### `analytics.base`" in md
    assert "- **Escrita por:** `risco/score.sql` (`risco/score.sql:2`)" in md
    assert "- **Lida por:** `modelos/modelo.py` (`modelos/modelo.py:3`)" in md
    assert "| `limite` | `raw.clientes.renda` | `risco/score.sql:3` |" in md


def test_markdown_infra_joins_and_hypotheses() -> None:
    md = render_markdown(_graph(), "x", COMMITS)
    assert "- **Armazenada em:** `s3://b/raw/clientes`" in md
    assert "- **Definida na infra:** `infra/glue.tf`" in md
    assert "- `raw.clientes.id` = `raw.pagamentos.id` (`risco/score.sql:5`)" in md
    assert "| `lim` | `analytics.base.limite` | `risco/score.sql:9` _(hipótese)_ |" in md


def test_markdown_column_without_lineage_and_no_repos() -> None:
    builder = FactBuilder(FileRef(repo="r", path="ddl.sql", commit_sha="c"))
    builder.column("t", "id", 1)
    md = render_markdown(Graph.from_facts(builder.build()), "t", {})
    assert "Repos: —" in md
    assert "| `id` | — | — |" in md


def test_json_is_machine_readable() -> None:
    document = json.loads(render_json(_graph(), "base", COMMITS))
    assert document["title"] == "base"
    assert list(document["repos"]) == ["modelos", "risco"]
    edge = next(e for e in document["edges"] if e["target"] == "column:models.abt.lim")
    assert edge["hypothesis"] is True
    assert edge["locations"][0] == {
        "repo": "risco",
        "path": "score.sql",
        "line": 9,
        "commit_sha": "c1",
    }


def test_summaries_render_as_hypotheses_in_markdown_and_json() -> None:
    from dbts.domain.enrichment import TableRole, TableSummary

    summary = TableSummary(resumo="Base.", papel=TableRole.FEATURE, pontos_de_atencao=["dup"])
    summaries = {"table:analytics.base": summary}
    md = render_markdown(_graph(), "x", COMMITS, summaries)
    assert (
        "### `analytics.base`\n\n> **Resumo (LLM, hipótese):** Base.\n> **Papel:** feature\n> - dup"
        in md
    )
    document = json.loads(render_json(_graph(), "x", COMMITS, summaries))
    assert document["llm_summaries_hypothesis"]["table:analytics.base"]["papel"] == "feature"


def test_filters_and_warnings_sections() -> None:
    from dbts.domain.models import EdgeKind as Kind

    builder = FactBuilder(FileRef(repo="r", path="q.sql", commit_sha="c"))
    job = builder.job()
    for column in ("a", "b"):
        builder.edge(job, builder.column("t", column, 2), Kind.FILTERS, 2, detail="a > b")
    builder.warning(7, "SQL não analisado: x")
    md = render_markdown(Graph.from_facts(builder.build()), "t", {})
    assert md.count("- `a > b` (`r/q.sql:2`)") == 1
    assert "## Trechos não analisados" in md
    assert "- `r/q.sql:7` — SQL não analisado: x" in md


def test_no_warnings_section_when_clean() -> None:
    assert "Trechos não analisados" not in render_markdown(_graph(), "x", COMMITS)
