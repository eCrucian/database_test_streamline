"""Lineage em Python/PySpark via `ast`: leituras, escritas, junções, colunas e SQL embutido.

Análise por arquivo, sem fluxo entre funções: variáveis são rastreadas em ordem de linha.
Cobre `spark.table`, `spark.read.*`, `.join`, `withColumn`, `withColumnRenamed`, `select`,
`groupBy`/`agg`, `saveAsTable`/`insertInto`, `.write.*` e SQL em chamadas como `spark.sql`,
`read_sql_query` (awswrangler/pandas) e `start_query_execution` (boto3).
Colunas de DataFrames vindos de `spark.sql` não são rastreadas (só as tabelas).
"""

import ast
from collections.abc import Callable, Iterator

from dbts.domain.models import EdgeKind, Fact, FileRef
from dbts.extract.facts import FactBuilder
from dbts.extract.frame import Column, Frame
from dbts.extract.sql import extract_sql_into, looks_like_sql, parse_predicate, read_tables

SQL_METHODS = frozenset({"sql", "read_sql", "read_sql_query", "start_query_execution", "execute"})
SQL_KEYWORDS = frozenset({"sql", "query", "QueryString"})
TABLE_METHODS = frozenset({"table"})
FILE_METHODS = frozenset({"parquet", "csv", "json", "orc", "load", "save"})
WRITE_METHODS = frozenset({"saveAsTable", "insertInto"})
PATH_KEYWORDS = frozenset({"path", "name", "tableName"})
COLUMN_FUNCS = frozenset({"col", "column"})
AGG_FUNCS = frozenset(
    {"sum", "avg", "mean", "max", "min", "count", "countDistinct", "first", "last", "stddev"}
    | {"variance", "collect_list", "collect_set", "approx_count_distinct", "lag", "lead"}
)
ALIAS_METHODS = frozenset({"alias", "name"})
PARAM = "__param__"

ColumnPair = tuple[Column, Column]


def _method(node: ast.Call) -> str | None:
    return node.func.attr if isinstance(node.func, ast.Attribute) else None


def _func_name(node: ast.Call) -> str | None:
    """Nome da função chamada, seja `F.col(...)` ou `col(...)`."""
    return node.func.id if isinstance(node.func, ast.Name) else _method(node)


def _in_chain(node: ast.expr, attr: str) -> bool:
    while isinstance(node, ast.Attribute | ast.Call):
        if isinstance(node, ast.Call):
            node = node.func
        elif node.attr == attr:
            return True
        else:
            node = node.value
    return False


def _argument(node: ast.Call, keywords: frozenset[str], position: int = 0) -> ast.expr | None:
    if len(node.args) > position:
        return node.args[position]
    return next((k.value for k in node.keywords if k.arg in keywords), None)


def _string_nodes(tree: ast.AST) -> Iterator[ast.Constant | ast.JoinedStr]:
    """Strings e f-strings, sem os pedaços internos de f-strings."""
    parts = {id(v) for n in ast.walk(tree) if isinstance(n, ast.JoinedStr) for v in n.values}
    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr) or (
            isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in parts
        ):
            yield node


def _is_physical(frame: Frame, table: str, name: str) -> bool:
    """A coluna não é derivada no frame (ou é a própria coluna física da tabela)."""
    return frame.columns.get(name.lower(), frozenset({(table, name)})) == {(table, name)}


def _relevant_nodes(tree: ast.AST) -> Iterator[ast.Assign | ast.Call]:
    watched = SQL_METHODS | WRITE_METHODS | FILE_METHODS | TABLE_METHODS | {"join"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) or (
            isinstance(node, ast.Call) and _method(node) in watched
        ):
            yield node


class _Analyzer:
    def __init__(self, builder: FactBuilder) -> None:
        self._builder = builder
        self._job = builder.job()
        self._frames: dict[str, Frame] = {}
        self._strings: dict[str, str] = {}
        self._handlers: dict[str, Callable[[ast.Call], Frame]] = {
            **dict.fromkeys(TABLE_METHODS, self._table_call),
            **dict.fromkeys(FILE_METHODS, self._file_call),
            **dict.fromkeys(SQL_METHODS, self._sql_call),
            "join": self._join,
            "withColumn": self._with_column,
            "withColumnRenamed": self._renamed,
            "select": self._select,
            "groupBy": self._select,
            "agg": self._agg,
            "filter": self._filter,
            "where": self._filter,
        }

    def run(self, tree: ast.AST) -> None:
        for node in sorted(_relevant_nodes(tree), key=lambda n: (n.lineno, n.col_offset)):
            if isinstance(node, ast.Assign):
                self._assign(node)
            else:
                self._call(node)
        self._embedded_sql(tree)

    def _embedded_sql(self, tree: ast.AST) -> None:
        """SQL em strings soltas (constantes, dicts de config), fora das chamadas conhecidas."""
        for node in _string_nodes(tree):
            text = self._literal(node)
            if text and looks_like_sql(text):
                extract_sql_into(self._builder, self._job, text, node.lineno)

    def _assign(self, node: ast.Assign) -> None:
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            return
        name = node.targets[0].id
        text = self._literal(node.value)
        if text is not None:
            self._strings[name] = text
        else:
            self._frames[name] = self._frame(node.value)

    def _call(self, node: ast.Call) -> None:
        method = _method(node)
        is_file_write = method in FILE_METHODS and _in_chain(node.func, "write")
        if method in WRITE_METHODS or is_file_write:
            self._write(node)
        else:
            self._frame(node)

    def _literal(self, node: ast.expr | None) -> str | None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.JoinedStr):
            return "".join(self._literal(v) or PARAM for v in node.values)
        if isinstance(node, ast.Name):
            return self._strings.get(node.id)
        return None

    # --- DataFrames -------------------------------------------------------------------------

    def _frame(self, node: ast.expr) -> Frame:
        if isinstance(node, ast.Name):
            return self._frames.get(node.id, Frame())
        if isinstance(node, ast.Attribute | ast.Subscript):
            return self._frame(node.value)
        return self._call_frame(node) if isinstance(node, ast.Call) else Frame()

    def _call_frame(self, node: ast.Call) -> Frame:
        handler = self._handlers.get(_method(node) or "")
        return handler(node) if handler else self._passthrough(node)

    def _receiver(self, node: ast.Call) -> Frame:
        return self._frame(node.func.value) if isinstance(node.func, ast.Attribute) else Frame()

    def _passthrough(self, node: ast.Call) -> Frame:
        receiver = self._receiver(node)
        if receiver:
            return receiver
        frames = [self._frame(arg) for arg in node.args]
        return next((frame for frame in frames if frame), Frame())

    def _table_call(self, node: ast.Call) -> Frame:
        return self._read(_argument(node, PATH_KEYWORDS), node.lineno)

    def _file_call(self, node: ast.Call) -> Frame:
        if _in_chain(node.func, "read"):
            return self._table_call(node)
        return self._passthrough(node)

    def _read(self, arg: ast.expr | None, line: int) -> Frame:
        name = self._literal(arg)
        if name is None:
            return Frame()
        self._builder.edge(self._job, self._builder.table(name, line), EdgeKind.READS, line)
        return Frame(frozenset({name.lower()}))

    def _sql_call(self, node: ast.Call) -> Frame:
        arg = _argument(node, SQL_KEYWORDS)
        text = self._literal(arg)
        if arg is None or text is None:
            return Frame()
        extract_sql_into(self._builder, self._job, text, arg.lineno)
        return Frame(frozenset(read_tables(text)))

    def _write(self, node: ast.Call) -> None:
        frame = self._receiver(node)
        name = self._literal(_argument(node, PATH_KEYWORDS))
        if name is None:
            return
        line = node.lineno
        self._builder.edge(self._job, self._builder.table(name, line), EdgeKind.WRITES, line)
        for column, sources in frame.columns.items():
            target = self._builder.column(name, column, line)
            for table, source in sorted(sources):
                origin = self._builder.column(table, source, line)
                self._builder.edge(origin, target, EdgeKind.DERIVES_FROM, line)

    # --- Colunas ----------------------------------------------------------------------------

    def _filter(self, node: ast.Call) -> Frame:
        """Filtro em string sobre colunas físicas de uma única tabela vira aresta `filters`.

        O frame devolvido "aprende" que essas colunas pertencem à tabela, o que permite
        resolvê-las depois de um join, quando o frame passa a ter várias tabelas.
        """
        base = self._receiver(node)
        text = self._literal(_argument(node, frozenset({"condition"})))
        parsed = parse_predicate(text) if text else None
        if parsed is None or len(base.tables) != 1:
            return base
        columns, predicate = parsed
        table = next(iter(base.tables))
        if not all(_is_physical(base, table, name) for name in columns):
            return base
        for name in columns:
            target = self._builder.column(table, name, node.lineno)
            self._builder.edge(self._job, target, EdgeKind.FILTERS, node.lineno, detail=predicate)
        return base.with_columns({name: frozenset({(table, name)}) for name in columns})

    def _with_column(self, node: ast.Call) -> Frame:
        base = self._receiver(node)
        name = self._literal(_argument(node, frozenset({"colName"})))
        expr = _argument(node, frozenset({"col"}), position=1)
        if name is None or expr is None:
            return base
        return base.with_columns({name: self._refs(expr, base)})

    def _renamed(self, node: ast.Call) -> Frame:
        base = self._receiver(node)
        old = self._literal(_argument(node, frozenset({"existing"})))
        new = self._literal(_argument(node, frozenset({"new"}), position=1))
        if old is None or new is None:
            return base
        return base.with_columns({new: base.resolve(old)})

    def _select(self, node: ast.Call) -> Frame:
        base = self._receiver(node)
        return base.only_columns(self._projections(node, base))

    def _agg(self, node: ast.Call) -> Frame:
        base = self._receiver(node)
        return base.with_columns(self._projections(node, base))

    def _projections(self, node: ast.Call, base: Frame) -> dict[str, frozenset[Column]]:
        projections = (self._projection(arg, base) for arg in node.args)
        return dict(p for p in projections if p is not None)

    def _projection(self, arg: ast.expr, base: Frame) -> tuple[str, frozenset[Column]] | None:
        if (
            isinstance(arg, ast.Call)
            and isinstance(arg.func, ast.Attribute)
            and arg.func.attr in ALIAS_METHODS
        ):
            alias = self._literal(_argument(arg, frozenset({"alias"})))
            return (alias, self._refs(arg.func.value, base)) if alias else None
        name = self._column_name(arg)
        return (name, self._refs(arg, base)) if name else None

    def _column_name(self, node: ast.expr) -> str | None:
        """Nome da coluna em `"x"`, `F.col("x")`, `df.x` ou `df["x"]`."""
        if isinstance(node, ast.Call) and _func_name(node) in COLUMN_FUNCS:
            return self._literal(_argument(node, frozenset({"col"})))
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            return node.attr if node.value.id in self._frames else None
        if isinstance(node, ast.Subscript):
            return self._literal(node.slice)
        return self._literal(node)

    def _refs(self, expr: ast.expr, base: Frame) -> frozenset[Column]:
        """Colunas físicas referenciadas em uma expressão de coluna."""
        if self._literal(expr) is not None:
            return base.resolve(self._literal(expr) or "")
        sources: set[Column] = set()
        for node in ast.walk(expr):
            sources |= self._node_refs(node, base)
        return frozenset(sources)

    def _node_refs(self, node: ast.AST, base: Frame) -> frozenset[Column]:
        if isinstance(node, ast.Call) and _func_name(node) in COLUMN_FUNCS:
            return base.resolve(self._literal(_argument(node, frozenset({"col"}))) or "")
        if isinstance(node, ast.Call) and _func_name(node) in AGG_FUNCS:
            names = (self._literal(arg) for arg in node.args)
            return frozenset().union(*(base.resolve(n) for n in names if n))
        if isinstance(node, ast.Attribute | ast.Subscript) and isinstance(node.value, ast.Name):
            return self._frame_ref(node.value, node)
        return frozenset()

    def _frame_ref(self, owner: ast.Name, node: ast.Attribute | ast.Subscript) -> frozenset[Column]:
        """`owner.col` ou `owner["col"]`, resolvido no frame da variável `owner`."""
        frame = self._frames.get(owner.id)
        name = node.attr if isinstance(node, ast.Attribute) else self._literal(node.slice)
        return frame.resolve(name) if frame and name else frozenset()

    # --- Junções ----------------------------------------------------------------------------

    def _join(self, node: ast.Call) -> Frame:
        left = self._receiver(node)
        right = self._frame(node.args[0]) if node.args else Frame()
        on = _argument(node, frozenset({"on"}), position=1)
        keys: dict[str, set[Column]] = {}
        for lcol, rcol in self._join_keys(on, left, right):
            columns = (
                self._builder.column(*lcol, node.lineno),
                self._builder.column(*rcol, node.lineno),
            )
            self._builder.edge(*columns, EdgeKind.JOINS_ON, node.lineno)
            for table, name in (lcol, rcol):
                keys.setdefault(name, set()).add((table, name))
        # Chaves de junção são evidência de qual tabela tem cada coluna.
        return left.merge(right).with_columns({k: frozenset(v) for k, v in keys.items()})

    def _join_keys(self, on: ast.expr | None, left: Frame, right: Frame) -> Iterator[ColumnPair]:
        for key in self._same_name_keys(on):
            lcol, rcol = left.resolve_one(key), right.resolve_one(key)
            if lcol and rcol:
                yield lcol, rcol
        for compare in ast.walk(on) if on else ():
            pair = self._compare_pair(compare)
            if pair:
                yield pair

    def _same_name_keys(self, on: ast.expr | None) -> list[str]:
        items = on.elts if isinstance(on, ast.List | ast.Tuple) else [on]
        return [key for key in map(self._literal, items) if key]

    def _compare_pair(self, node: ast.AST) -> ColumnPair | None:
        if not (isinstance(node, ast.Compare) and isinstance(node.ops[0], ast.Eq)):
            return None
        left, right = self._column_ref(node.left), self._column_ref(node.comparators[0])
        return (left, right) if left and right else None

    def _column_ref(self, node: ast.expr) -> Column | None:
        """`df.col` ou `df["col"]` que resolve para uma única coluna física."""
        if not (
            isinstance(node, ast.Attribute | ast.Subscript) and isinstance(node.value, ast.Name)
        ):
            return None
        sources = self._frame_ref(node.value, node)
        return next(iter(sources)) if len(sources) == 1 else None


class PySparkExtractor:
    extensions = frozenset({".py"})

    def extract(self, content: str, ref: FileRef) -> list[Fact]:
        builder = FactBuilder(ref)
        try:
            tree = ast.parse(content)
        except SyntaxError:
            builder.job()
            return builder.build()
        _Analyzer(builder).run(tree)
        return builder.build()
