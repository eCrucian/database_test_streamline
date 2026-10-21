from collections.abc import Sequence
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class FakeLLMProvider:
    """Devolve respostas JSON pré-definidas, em ordem, e registra os prompts recebidos."""

    name = "fake"

    def __init__(self, responses: Sequence[str], model: str = "fake-model") -> None:
        self.model = model
        self._responses = list(responses)
        self.prompts: list[str] = []

    def complete(self, prompt: str, schema: type[T]) -> T:
        if not self._responses:
            raise RuntimeError("FakeLLMProvider sem respostas restantes")
        self.prompts.append(prompt)
        return schema.model_validate_json(self._responses.pop(0))
