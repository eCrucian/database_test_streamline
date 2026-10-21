"""SQL embutido em JavaScript/TypeScript: strings e template literals que parecem SQL.

Análise léxica simples (regex), sem AST: strings dentro de comentários também são lidas.
"""

import re

from dbts.domain.models import Fact, FileRef
from dbts.extract.facts import FactBuilder
from dbts.extract.sql import extract_sql_into, looks_like_sql

_STRING = re.compile(
    r"`(?:\\.|[^`\\])*`|'(?:\\.|[^'\\\n])*'|\"(?:\\.|[^\"\\\n])*\"",
    re.DOTALL,
)


class JavaScriptExtractor:
    extensions = frozenset({".js", ".ts"})

    def extract(self, content: str, ref: FileRef) -> list[Fact]:
        builder = FactBuilder(ref)
        job = builder.job()
        for match in _STRING.finditer(content):
            body = match.group()[1:-1]
            if looks_like_sql(body):
                line = content.count("\n", 0, match.start()) + 1
                extract_sql_into(builder, job, body, line)
        return builder.build()
