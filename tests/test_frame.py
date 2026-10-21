from dbts.extract.frame import Frame

SINGLE = Frame(frozenset({"db.t"}))


def test_resolve_known_column_wins() -> None:
    frame = SINGLE.with_columns({"Novo": frozenset({("db.x", "a")})})
    assert frame.resolve("novo") == {("db.x", "a")}


def test_resolve_falls_back_to_single_table() -> None:
    assert SINGLE.resolve("Renda") == {("db.t", "renda")}
    assert SINGLE.resolve_one("renda") == ("db.t", "renda")


def test_resolve_ambiguous_with_multiple_tables() -> None:
    frame = Frame(frozenset({"a", "b"}))
    assert frame.resolve("x") == frozenset()
    assert frame.resolve_one("x") is None


def test_only_columns_drops_previous_columns() -> None:
    frame = SINGLE.with_columns({"a": frozenset()}).only_columns({"b": frozenset()})
    assert set(frame.columns) == {"b"}


def test_merge_unions_tables_and_columns() -> None:
    left = SINGLE.with_columns({"a": frozenset({("db.t", "x")})})
    right = Frame(frozenset({"db.u"})).with_columns({"b": frozenset({("db.u", "y")})})
    merged = left.merge(right)
    assert merged.tables == {"db.t", "db.u"}
    assert set(merged.columns) == {"a", "b"}


def test_truthiness() -> None:
    assert not Frame()
    assert SINGLE
    assert Frame().with_columns({"a": frozenset()})
