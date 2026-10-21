"""Renderização determinística do grafo: Markdown (com Mermaid) e JSON legível por IA."""

import json
from collections.abc import Iterable, Mapping

from dbts.domain.enrichment import TableSummary
from dbts.domain.models import EdgeKind, Entity, EntityKind
from dbts.mapping.graph import EdgeInfo, Graph

_MERMAID_ARROWS = {
    EdgeKind.READS: "-->",
    EdgeKind.WRITES: "-->",
    EdgeKind.STORED_AT: "-.->",
    EdgeKind.DEPLOYED_BY: "-.->",
}
_FLOW_KINDS = {EntityKind.JOB, EntityKind.TABLE}


def _short(node_id: str) -> str:
    return node_id.split(":", 1)[1]


def _where(info: EdgeInfo) -> str:
    places = ", ".join(f"`{loc.repo}/{loc.path}:{loc.line}`" for loc in info.locations)
    return f"{places} _(hipótese)_" if info.hypothesis else places


def render_mermaid(graph: Graph) -> str:
    nodes = [e for e in graph.entities.values() if e.kind in _FLOW_KINDS]
    ids = {e.id: f"n{i}" for i, e in enumerate(sorted(nodes, key=lambda e: e.id))}
    lines = ["flowchart LR"]
    for entity in sorted(nodes, key=lambda e: e.id):
        label = _short(entity.id).replace('"', "'")
        shape = f'["{label}"]' if entity.kind is EntityKind.JOB else f'[("{label}")]'
        lines.append(f"  {ids[entity.id]}{shape}")
    for info in graph.edges:
        arrow = _MERMAID_ARROWS.get(info.edge.kind)
        source, target = ids.get(info.edge.source), ids.get(info.edge.target)
        if arrow and source and target:
            ends = (target, source) if info.edge.kind is EdgeKind.READS else (source, target)
            lines.append(f"  {ends[0]} {arrow}|{info.edge.kind}| {ends[1]}")
    return "\n".join(lines)


def _bullets(label: str, infos: Iterable[EdgeInfo], node_of: str) -> list[str]:
    items = [f"`{_short(getattr(i.edge, node_of))}` ({_where(i)})" for i in infos]
    return [f"- **{label}:** " + "; ".join(items)] if items else []


def _column_rows(graph: Graph, table: Entity) -> list[str]:
    prefix = f"column:{_short(table.id)}."
    rows = []
    for column in graph.of_kind(EntityKind.COLUMN):
        if not column.id.startswith(prefix):
            continue
        derived = [i for i in graph.edges_to(column.id) if i.edge.kind is EdgeKind.DERIVES_FROM]
        sources = ", ".join(f"`{_short(i.edge.source)}`" for i in derived) or "—"
        where = "; ".join(_where(i) for i in derived) or "—"
        rows.append(f"| `{column.id.removeprefix(prefix)}` | {sources} | {where} |")
    return ["", "| Coluna | Deriva de | Onde |", "|---|---|---|", *rows] if rows else []


def _join_lines(graph: Graph, table: Entity) -> list[str]:
    prefix = f"column:{_short(table.id)}."
    joins = [
        i
        for i in graph.edges
        if i.edge.kind is EdgeKind.JOINS_ON
        and (i.edge.source.startswith(prefix) or i.edge.target.startswith(prefix))
    ]
    lines = [
        f"- `{_short(i.edge.source)}` = `{_short(i.edge.target)}` ({_where(i)})" for i in joins
    ]
    return ["", "**Chaves de junção**", *lines] if lines else []


def _filter_lines(graph: Graph, table: Entity) -> list[str]:
    prefix = f"column:{_short(table.id)}."
    filters: dict[str, list[EdgeInfo]] = {}
    for info in graph.edges:
        if info.edge.kind is EdgeKind.FILTERS and info.edge.target.startswith(prefix):
            filters.setdefault(info.edge.detail or "", []).append(info)
    lines = [
        f"- `{predicate}` ({_where(infos[0])})" for predicate, infos in sorted(filters.items())
    ]
    return ["", "**Filtros aplicados**", *lines] if lines else []


def _warning_lines(graph: Graph) -> list[str]:
    warnings = graph.of_kind(EntityKind.WARNING)
    lines = [f"- `{w.id.removeprefix('warning:')}` — {w.name}" for w in warnings]
    intro = (
        "Trechos que os extratores não conseguiram analisar; o mapa pode estar incompleto neles."
    )
    return ["## Trechos não analisados", "", intro, "", *lines, ""] if lines else []


def _table_card(graph: Graph, table: Entity) -> list[str]:
    def by_kind(infos: list[EdgeInfo], kind: EdgeKind) -> list[EdgeInfo]:
        return [i for i in infos if i.edge.kind is kind]

    incoming, outgoing = graph.edges_to(table.id), graph.edges_from(table.id)
    return [
        f"### `{_short(table.id)}`",
        "",
        *_bullets("Escrita por", by_kind(incoming, EdgeKind.WRITES), "source"),
        *_bullets("Lida por", by_kind(incoming, EdgeKind.READS), "source"),
        *_bullets("Armazenada em", by_kind(outgoing, EdgeKind.STORED_AT), "target"),
        *_bullets("Definida na infra", by_kind(outgoing, EdgeKind.DEPLOYED_BY), "target"),
        *_column_rows(graph, table),
        *_join_lines(graph, table),
        *_filter_lines(graph, table),
        "",
    ]


def table_card(graph: Graph, table: Entity) -> str:
    return "\n".join(_table_card(graph, table))


def _summary_lines(summary: TableSummary | None) -> list[str]:
    if summary is None:
        return []
    lines = [
        f"> **Resumo (LLM, hipótese):** {summary.resumo}",
        f"> **Papel:** {summary.papel}",
        *(f"> - {point}" for point in summary.pontos_de_atencao),
    ]
    return [*lines, ""]


def render_markdown(
    graph: Graph,
    title: str,
    commits: Mapping[str, str],
    summaries: Mapping[str, TableSummary] | None = None,
) -> str:
    summaries = summaries or {}
    repos = ", ".join(f"`{name}@{sha[:8]}`" for name, sha in sorted(commits.items()))
    lines = [
        f"# Mapa: {title}",
        "",
        f"Repos: {repos or '—'}",
        "",
        "Gerado deterministicamente a partir do código. Itens marcados _(hipótese)_ vieram de "
        "inferência por LLM e não foram confirmados por parser.",
        "",
        "## Fluxo",
        "",
        "```mermaid",
        render_mermaid(graph),
        "```",
        "",
        "## Tabelas",
        "",
    ]
    for table in graph.of_kind(EntityKind.TABLE):
        card = _table_card(graph, table)
        lines.extend([*card[:2], *_summary_lines(summaries.get(table.id)), *card[2:]])
    lines.extend(_warning_lines(graph))
    return "\n".join(lines)


def render_json(
    graph: Graph,
    title: str,
    commits: Mapping[str, str],
    summaries: Mapping[str, TableSummary] | None = None,
) -> str:
    document = {
        "title": title,
        "repos": dict(sorted(commits.items())),
        "llm_summaries_hypothesis": {
            eid: summary.model_dump(mode="json") for eid, summary in (summaries or {}).items()
        },
        "entities": [
            e.model_dump(mode="json") for e in sorted(graph.entities.values(), key=lambda e: e.id)
        ],
        "edges": [
            {
                **info.edge.model_dump(mode="json"),
                "hypothesis": info.hypothesis,
                "locations": [loc.model_dump(mode="json") for loc in info.locations],
            }
            for info in graph.edges
        ],
    }
    return json.dumps(document, ensure_ascii=False, indent=2)
