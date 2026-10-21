"""Fatos de infraestrutura em Terraform (HCL) via python-hcl2.

Cobre `aws_glue_catalog_table` (tabela, colunas, partições e localização S3) e
`aws_athena_named_query` (SQL embutido). Interpolações `${...}` viram `__param__`.
Recursos definidos dentro de módulos de terceiros não são vistos.
"""

import re
from collections.abc import Callable, Iterator
from typing import Any

import hcl2
from hcl2.utils import SerializationOptions
from lark.exceptions import LarkError

from dbts.domain.models import EdgeKind, Fact, FileRef
from dbts.extract.facts import FactBuilder
from dbts.extract.sql import extract_sql_into, neutralize_templates

OPTIONS = SerializationOptions(
    with_comments=False,
    explicit_blocks=False,
    preserve_heredocs=False,
    strip_string_quotes=True,
)

Handler = Callable[[FactBuilder, str, dict[str, Any], int], None]


def _resources(document: dict[str, Any]) -> Iterator[tuple[str, str, dict[str, Any]]]:
    for block in document.get("resource", []):
        for kind, items in block.items():
            for name, attrs in items.items():
                yield kind, name, attrs


def _line(content: str, kind: str, name: str) -> int:
    match = re.search(rf'resource\s+"{re.escape(kind)}"\s+"{re.escape(name)}"', content)
    return content.count("\n", 0, match.start()) + 1 if match else 1


def _block(attrs: dict[str, Any], key: str) -> dict[str, Any]:
    value = attrs.get(key)
    return value[0] if isinstance(value, list) and value else {}


def _names(blocks: Any) -> list[str]:
    items = blocks if isinstance(blocks, list) else []
    return [b["name"] for b in items if isinstance(b, dict) and isinstance(b.get("name"), str)]


def _glue_table(builder: FactBuilder, job: str, attrs: dict[str, Any], line: int) -> None:
    database, name = attrs.get("database_name"), attrs.get("name")
    if not (isinstance(database, str) and isinstance(name, str)):
        return
    table = neutralize_templates(f"{database}.{name}")
    table_node = builder.table(table, line)
    builder.edge(table_node, job, EdgeKind.DEPLOYED_BY, line)
    storage = _block(attrs, "storage_descriptor")
    for column in _names(storage.get("columns")) + _names(attrs.get("partition_keys")):
        builder.column(table, column, line)
    location = storage.get("location")
    if isinstance(location, str):
        storage_node = builder.table(neutralize_templates(location), line)
        builder.edge(table_node, storage_node, EdgeKind.STORED_AT, line)


def _named_query(builder: FactBuilder, job: str, attrs: dict[str, Any], line: int) -> None:
    query = attrs.get("query")
    if isinstance(query, str):
        extract_sql_into(builder, job, query, line)


HANDLERS: dict[str, Handler] = {
    "aws_glue_catalog_table": _glue_table,
    "aws_athena_named_query": _named_query,
}


class TerraformExtractor:
    extensions = frozenset({".tf"})

    def extract(self, content: str, ref: FileRef) -> list[Fact]:
        builder = FactBuilder(ref)
        job = builder.job()
        try:
            document = hcl2.loads(content, serialization_options=OPTIONS)
        except LarkError:
            return builder.build()
        for kind, name, attrs in _resources(document):
            handler = HANDLERS.get(kind)
            if handler:
                handler(builder, job, attrs, _line(content, kind, name))
        return builder.build()
