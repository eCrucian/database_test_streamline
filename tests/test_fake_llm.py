import pytest
from pydantic import BaseModel

from dbts.adapters.fake_llm import FakeLLMProvider


class Answer(BaseModel):
    text: str


def test_fake_returns_responses_in_order_and_records_prompts() -> None:
    fake = FakeLLMProvider(['{"text": "a"}', '{"text": "b"}'])
    assert fake.complete("p1", Answer).text == "a"
    assert fake.complete("p2", Answer).text == "b"
    assert fake.prompts == ["p1", "p2"]


def test_fake_without_responses_raises() -> None:
    with pytest.raises(RuntimeError):
        FakeLLMProvider([]).complete("p", Answer)
