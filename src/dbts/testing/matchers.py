"""Padrões do grafo que disparam hipóteses. Cada padrão devolve parâmetros + evidência."""

import re
from collections import defaultdict
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from itertools import combinations

from dbts.domain.models import EdgeKind, EntityKind, SourceLocation
from dbts.mapping.graph import Graph

KEY_COLUMN = re.compile(r"^(id|cpf|cnpj|chave|cod|num)(_|$)|_(id|key|cpf|cnpj)$")
DATE_COLUMN = re.compile(r"^(dt|data|date|dat|ref|mes|ano_mes)(_|$)|_(dt|data|date)$")


@dataclass(frozen=True)
class Match:
    params: dict[str, str]
    evidence: tuple[SourceLocation, ...]


def split_column(column_id: str) -> tuple[str, str]:
    table, column = column_id.removeprefix("column:").rsplit(".", 1)
    return table, column


def _written_tables(graph: Graph) -> dict[str, tuple[SourceLocation, ...]]:
    """Tabelas escritas por algum job, com a localização das escritas."""
    written: dict[str, list[SourceLocation]] = defaultdict(list)
    for info in graph.edges:
        if info.edge.kind is EdgeKind.WRITES:
            written[info.edge.target.removeprefix("table:")].extend(info.locations)
    return {table: tuple(locations) for table, locations in written.items()}


def _columns_by_table(graph: Graph) -> dict[str, list[str]]:
    columns: dict[str, list[str]] = defaultdict(list)
    for entity in graph.of_kind(EntityKind.COLUMN):
        table, column = split_column(entity.id)
        columns[table].append(column)
    return columns


def join_keys(graph: Graph) -> Iterator[Match]:
    for info in graph.edges:
        if info.edge.kind is not EdgeKind.JOINS_ON:
            continue
        (lt, lc), (rt, rc) = split_column(info.edge.source), split_column(info.edge.target)
        params = {"left_table": lt, "left_col": lc, "right_table": rt, "right_col": rc}
        yield Match(params, info.locations)


def key_columns(graph: Graph) -> Iterator[Match]:
    columns = _columns_by_table(graph)
    for table, locations in sorted(_written_tables(graph).items()):
        for column in columns.get(table, []):
            if KEY_COLUMN.search(column):
                yield Match({"table": table, "column": column}, locations)


def date_columns(graph: Graph) -> Iterator[Match]:
    columns = _columns_by_table(graph)
    for table, locations in sorted(_written_tables(graph).items()):
        dates = [c for c in columns.get(table, []) if DATE_COLUMN.search(c)]
        if len(dates) >= 2:
            yield Match({"table": table, "date_columns": ", ".join(dates)}, locations)


def _derivations(graph: Graph) -> dict[str, dict[str, set[str]]]:
    """nome da coluna -> tabela -> colunas de origem."""
    derived: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for info in graph.edges:
        if info.edge.kind is EdgeKind.DERIVES_FROM:
            table, column = split_column(info.edge.target)
            derived[column][table].add(info.edge.source.removeprefix("column:"))
    return derived


def divergent_definitions(graph: Graph) -> Iterator[Match]:
    locations = {
        i.edge.target: i.locations for i in graph.edges if i.edge.kind is EdgeKind.DERIVES_FROM
    }
    for column, by_table in sorted(_derivations(graph).items()):
        for (ta, sa), (tb, sb) in combinations(sorted(by_table.items()), 2):
            # Mesma origem, ou uma tabela só herda a coluna da outra: não é divergência.
            if sa == sb or f"{ta}.{column}" in sb or f"{tb}.{column}" in sa:
                continue
            params = {
                "column": column,
                "table_a": ta,
                "table_b": tb,
                "sources_a": ", ".join(sorted(sa)),
                "sources_b": ", ".join(sorted(sb)),
            }
            evidence = locations[f"column:{ta}.{column}"] + locations[f"column:{tb}.{column}"]
            yield Match(params, evidence)


def filters(graph: Graph) -> Iterator[Match]:
    """Um match por (tabela, predicado), mesmo que o predicado use várias colunas."""
    found: dict[tuple[str, str], list[SourceLocation]] = defaultdict(list)
    for info in graph.edges:
        if info.edge.kind is EdgeKind.FILTERS and info.edge.detail:
            table, _ = split_column(info.edge.target)
            found[(table, info.edge.detail)].extend(info.locations)
    for (table, predicate), locations in sorted(found.items()):
        unique = tuple(dict.fromkeys(locations))
        yield Match({"table": table, "predicate": predicate}, unique)


MATCHERS: dict[str, Callable[[Graph], Iterator[Match]]] = {
    "join": join_keys,
    "key_column": key_columns,
    "date_columns": date_columns,
    "divergent_definition": divergent_definitions,
    "filter": filters,
}
