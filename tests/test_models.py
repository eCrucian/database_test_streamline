import pytest
from pydantic import ValidationError

from dbts.domain.models import Edge, EdgeKind, Entity, EntityKind, Fact, Origin, SourceLocation

LOCATION = SourceLocation(repo="r", path="a.sql", line=1, commit_sha="abc")


def test_fact_from_llm_is_hypothesis() -> None:
    fact = Fact(
        edge=Edge(source="a", target="b", kind=EdgeKind.READS), location=LOCATION, origin=Origin.LLM
    )
    assert fact.is_hypothesis


def test_fact_from_parser_is_not_hypothesis() -> None:
    entity = Entity(id="t", kind=EntityKind.TABLE, name="t")
    assert not Fact(entity=entity, location=LOCATION, origin=Origin.PARSER).is_hypothesis


def test_models_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        Entity(id="t", kind=EntityKind.TABLE, name="t", extra=1)  # type: ignore[call-arg]
