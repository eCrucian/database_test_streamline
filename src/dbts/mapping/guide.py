import re
from dataclasses import dataclass
from pathlib import Path

from dbts.audit.log import AuditEvent, AuditLog
from dbts.domain.models import Origin
from dbts.enrich.tables import TableEnricher
from dbts.mapping.graph import Graph
from dbts.mapping.render import render_json, render_markdown
from dbts.ports import MapStore

FULL_MAP = "mapa-completo"


@dataclass(frozen=True)
class GuideResult:
    markdown: Path
    json: Path
    entities: int


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "mapa"


def load_subgraph(store: MapStore, term: str | None, depth: int) -> Graph | None:
    """Grafo inteiro (term None) ou em torno de `term`; None se o termo não casa com nada."""
    graph = Graph.from_facts(store.all_facts())
    if term is None:
        return graph
    seeds = graph.find(term)
    return graph.around(seeds, depth) if seeds else None


def build_guide(
    store: MapStore,
    out_dir: Path,
    audit: AuditLog,
    user: str,
    term: str | None,
    depth: int = 2,
    enricher: TableEnricher | None = None,
) -> GuideResult | None:
    """Gera o guia do subgrafo em torno de `term` (ou do grafo inteiro se `term` é None).

    Com `enricher`, inclui resumos das tabelas gerados por LLM (marcados como hipótese).
    Devolve None quando o termo não casa com nenhuma entidade.
    """
    graph = load_subgraph(store, term, depth)
    if graph is None:
        return None
    summaries = enricher.summarize(graph) if enricher else {}
    title = term or FULL_MAP
    commits = store.repo_commits()
    out_dir.mkdir(parents=True, exist_ok=True)
    markdown, document = out_dir / f"{slugify(title)}.md", out_dir / f"{slugify(title)}.json"
    markdown.write_text(render_markdown(graph, title, commits, summaries), encoding="utf-8")
    document.write_text(render_json(graph, title, commits, summaries), encoding="utf-8")
    repos = " ".join(f"{name}@{sha[:8]}" for name, sha in sorted(commits.items()))
    audit.append(
        AuditEvent(
            action="map",
            user=user,
            origin=Origin.PARSER,
            detail=f"term={title} depth={depth} entities={len(graph.entities)} repos={repos}",
        )
    )
    return GuideResult(markdown, document, len(graph.entities))
