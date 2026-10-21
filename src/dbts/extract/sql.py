"""Lineage de tabelas e colunas em SQL (dialeto Athena/Presto) via sqlglot.

O lineage de colunas usa `sqlglot.lineage`, que atravessa CTEs e subqueries. Quando o sqlglot
não consegue qualificar a query (ex.: coluna sem prefixo com várias tabelas), cai para uma
resolução simples de aliases, em que colunas sem qualificador só resolvem com uma única tabela.
Chaves de junção sobre CTEs ainda não são rastreadas até a tabela física.
"""

import re
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field

import sqlglot
from sqlglot import TokenType, exp
from sqlglot.dialects.dialect import Dialect
from sqlglot.errors import ParseError, SqlglotError, TokenError
from sqlglot.lineage import lineage

from dbts.domain.models import EdgeKind, Fact, FileRef
from dbts.extract.facts import FactBuilder

DIALECT = "athena"
PARAM = "__param__"
_TEMPLATE_EXPR = re.compile(r"\$\{[^}]*\}|\{\{.*?\}\}")
_TEMPLATE_BLOCK = re.compile(r"\{%.*?%\}|\{#.*?#\}", re.DOTALL)


_SQL_HINT = re.compile(r"^\s*(select|insert|create|with|merge|update|delete)\s", re.IGNORECASE)


def looks_like_sql(text: str) -> bool:
    """Heurística para SQL embutido em strings de outras linguagens."""
    return bool(_SQL_HINT.match(text))


def neutralize_templates(sql: str) -> str:
    """Troca parâmetros (${x}, {{ x }}) por um identificador e remove blocos Jinja."""
    return _TEMPLATE_EXPR.sub(PARAM, _TEMPLATE_BLOCK.sub("", sql))


def split_statements(sql: str) -> Iterator[tuple[int, str]]:
    """Devolve (linha inicial, texto) de cada statement."""
    tokens = Dialect.get_or_raise(DIALECT).tokenize(sql)
    start = None
    for token in tokens:
        if token.token_type == TokenType.SEMICOLON:
            if start is not None:
                yield start.line, sql[start.start : token.start]
            start = None
        elif start is None:
            start = token
    if start is not None:
        yield start.line, sql[start.start :]


def _table_name(table: exp.Table) -> str:
    return ".".join(p for p in (table.catalog, table.db, table.name) if p).lower()


def _target_table(tree: exp.Expr) -> exp.Table | None:
    if not isinstance(tree, exp.Create | exp.Insert):
        return None
    node = tree.this
    return node if isinstance(node, exp.Table) else node.find(exp.Table)


@dataclass(frozen=True)
class _Scope:
    aliases: dict[str, str]
    default: str | None
    cte_aliases: dict[str, str] = field(default_factory=dict)
    ctes: dict[str, exp.Expr] = field(default_factory=dict)

    @classmethod
    def of(
        cls, tree: exp.Expr, excluded: set[str], ctes: dict[str, exp.Expr] | None = None
    ) -> "_Scope":
        ctes = _ctes(tree) if ctes is None else ctes
        aliases: dict[str, str] = {}
        cte_aliases: dict[str, str] = {}
        for table in tree.find_all(exp.Table):
            name, alias = _table_name(table), table.alias_or_name.lower()
            if name in ctes:
                cte_aliases[alias] = name
            elif name not in excluded:
                aliases[alias] = name
                aliases[name] = name
        unique = set(aliases.values())
        return cls(aliases, unique.pop() if len(unique) == 1 else None, cte_aliases, ctes)

    def resolve(self, column: exp.Column) -> tuple[str, str] | None:
        alias = column.table.lower()
        if alias in self.cte_aliases:
            return self._through_cte(self.cte_aliases[alias], column.name.lower())
        table = self.aliases.get(alias) if alias else self.default
        return None if table is None else (table, column.name.lower())

    def _through_cte(self, name: str, column: str) -> tuple[str, str] | None:
        """Segue a coluna pela projeção da CTE até a tabela física (só colunas diretas)."""
        query = self.ctes[name]
        select = query if isinstance(query, exp.Select) else query.find(exp.Select)
        projections = select.selects if select else []
        found = next((p for p in projections if p.alias_or_name.lower() == column), None)
        inner = found.unalias() if found is not None else None
        if select is None or not isinstance(inner, exp.Column):
            return None
        others = {key: value for key, value in self.ctes.items() if key != name}
        return _Scope.of(select, set(), others).resolve(inner)


def _ctes(tree: exp.Expr) -> dict[str, exp.Expr]:
    return {cte.alias_or_name.lower(): cte.this for cte in tree.find_all(exp.CTE)}


def _column_pair(eq: exp.EQ, scope: _Scope) -> tuple[str, str, str, str] | None:
    if not (isinstance(eq.left, exp.Column) and isinstance(eq.right, exp.Column)):
        return None
    left, right = scope.resolve(eq.left), scope.resolve(eq.right)
    return (*left, *right) if left and right else None


def _join_pairs(tree: exp.Expr, scope: _Scope) -> Iterator[tuple[str, str, str, str]]:
    for join in tree.find_all(exp.Join):
        on = join.args.get("on")
        for eq in on.find_all(exp.EQ) if on else ():
            pair = _column_pair(eq, scope)
            if pair:
                yield pair


def _projections(tree: exp.Expr, scope: _Scope) -> Iterator[tuple[str, str, str]]:
    select = tree.find(exp.Select)
    for projection in select.expressions if select else ():
        out = projection.alias_or_name.lower()
        if out in ("", "*"):
            continue
        for column in projection.find_all(exp.Column):
            source = scope.resolve(column)
            if source:
                yield (*source, out)


def _single_table(select: exp.Select) -> exp.Table | None:
    source = select.args.get("from_")
    table = source.this if source else None
    return table if isinstance(table, exp.Table) and not select.args.get("joins") else None


def _qualify_single_source(query: exp.Query) -> exp.Query:
    """Prefixa colunas soltas em SELECTs de tabela única.

    Contorna o sqlglot, que não qualifica colunas de subqueries quando a query tem CTEs.
    """
    query = query.copy()
    for select in query.find_all(exp.Select):
        table = _single_table(select)
        if table is None:
            continue
        for column in select.find_all(exp.Column):
            if not column.table and column.parent_select is select:
                column.set("table", exp.to_identifier(table.alias_or_name))
    return query


def _lineage_projections(tree: exp.Expr) -> list[tuple[str, str, str]] | None:
    """(tabela, coluna, saída) via sqlglot.lineage; None se a query não puder ser qualificada."""
    query = tree.expression
    if not isinstance(query, exp.Query):
        return []
    try:
        nodes = lineage(None, _qualify_single_source(query), {}, dialect=DIALECT)
    except SqlglotError:
        return None
    return [
        (_table_name(leaf.source), leaf.name.split(".")[-1].lower(), out.lower())
        for out, node in nodes.items()
        for leaf in node.walk()
        if isinstance(leaf.source, exp.Table) and not leaf.downstream
    ]


def _ddl_columns(tree: exp.Expr) -> Iterator[str]:
    schema = tree.this if isinstance(tree, exp.Create) else None
    if isinstance(schema, exp.Schema):
        yield from (col.name for col in schema.expressions if isinstance(col, exp.ColumnDef))


def _scope_and_target(tree: exp.Expr) -> tuple[_Scope, str | None]:
    target_node = _target_table(tree)
    target = _table_name(target_node) if target_node else None
    return _Scope.of(tree, {target} if target else set()), target


def _conjuncts(where: exp.Where) -> list[exp.Expr]:
    condition = where.this
    return list(condition.flatten()) if isinstance(condition, exp.And) else [condition]


def _filter(condition: exp.Expr, scope: _Scope) -> tuple[str, list[str], str] | None:
    """(tabela, colunas, predicado sem alias) de um termo do WHERE sobre uma única tabela.

    Predicados com subquery ou parâmetro de template não são avaliáveis isoladamente.
    """
    if condition.find(exp.Select) or PARAM in condition.sql(dialect=DIALECT):
        return None
    columns = list(condition.find_all(exp.Column))
    resolved = [scope.resolve(column) for column in columns]
    # Coluna renomeada numa CTE tornaria o predicado inválido na tabela física.
    direct = [r for c, r in zip(columns, resolved, strict=True) if r and r[1] == c.name.lower()]
    tables = {table for table, _ in direct}
    if not columns or len(direct) != len(columns) or len(tables) != 1:
        return None
    bare = condition.transform(
        lambda node: exp.column(node.name) if isinstance(node, exp.Column) else node
    )
    return tables.pop(), sorted({name for _, name in direct}), bare.sql(dialect=DIALECT)


def parse_predicate(text: str) -> tuple[list[str], str] | None:
    """(colunas, predicado normalizado) de uma condição SQL solta, como em `df.filter("x > 1")`."""
    if PARAM in text:
        return None
    try:
        condition = sqlglot.parse_one(text, read=DIALECT)
    except SqlglotError:
        return None
    columns = sorted({column.name.lower() for column in condition.find_all(exp.Column)})
    if not columns or condition.find(exp.Select):
        return None
    return columns, condition.sql(dialect=DIALECT)


def _emit_filters(tree: exp.Expr, scope: _Scope, builder: FactBuilder, job: str, line: int) -> None:
    for where in tree.find_all(exp.Where):
        for found in filter(None, (_filter(c, scope) for c in _conjuncts(where))):
            table, columns, predicate = found
            for column in columns:
                target = builder.column(table, column, line)
                builder.edge(job, target, EdgeKind.FILTERS, line, detail=predicate)


def extract_statement(tree: exp.Expr, builder: FactBuilder, job: str, line: int) -> None:
    scope, target = _scope_and_target(tree)
    _emit_filters(tree, scope, builder, job, line)

    for source in sorted(set(scope.aliases.values())):
        builder.edge(job, builder.table(source, line), EdgeKind.READS, line)
    for lt, lc, rt, rc in _join_pairs(tree, scope):
        left, right = builder.column(lt, lc, line), builder.column(rt, rc, line)
        builder.edge(left, right, EdgeKind.JOINS_ON, line)
    if target is None:
        return
    builder.edge(job, builder.table(target, line), EdgeKind.WRITES, line)
    for column in _ddl_columns(tree):
        builder.column(target, column, line)
    projections = _lineage_projections(tree)
    if projections is None:
        projections = list(_projections(tree, scope))
    for st, sc, out in projections:
        source, dest = builder.column(st, sc, line), builder.column(target, out, line)
        builder.edge(source, dest, EdgeKind.DERIVES_FROM, line)


OnError = Callable[[int, str], None]


def _ignore(line: int, message: str) -> None:
    """Padrão de `parse_statements`: descarta erros silenciosamente."""


def parse_statements(sql: str, on_error: OnError = _ignore) -> Iterator[tuple[int, exp.Expr]]:
    """Devolve (linha, árvore) dos statements válidos; inválidos vão para `on_error`."""
    try:
        statements = list(split_statements(neutralize_templates(sql)))
    except TokenError as error:
        on_error(1, f"SQL não tokenizável: {error}")
        return
    for line, text in statements:
        try:
            yield line, sqlglot.parse_one(text, read=DIALECT)
        except ParseError as error:
            on_error(line, f"SQL não analisado: {str(error).splitlines()[0]}")


def read_tables(sql: str) -> set[str]:
    """Tabelas físicas lidas por `sql` (sem CTEs nem a tabela de destino)."""
    tables: set[str] = set()
    for _, tree in parse_statements(sql):
        tables |= set(_scope_and_target(tree)[0].aliases.values())
    return tables


def extract_sql_into(builder: FactBuilder, job: str, sql: str, base_line: int = 1) -> None:
    def warn(line: int, message: str) -> None:
        builder.warning(base_line + line - 1, message)

    for line, tree in parse_statements(sql, warn):
        extract_statement(tree, builder, job, base_line + line - 1)


class SQLExtractor:
    extensions = frozenset({".sql"})

    def extract(self, content: str, ref: FileRef) -> list[Fact]:
        builder = FactBuilder(ref)
        extract_sql_into(builder, builder.job(), content)
        return builder.build()
