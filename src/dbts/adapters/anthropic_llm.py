from typing import TypeVar

import anthropic
from pydantic import BaseModel

from dbts.ports import LLMResponseError

T = TypeVar("T", bound=BaseModel)


class AnthropicProvider:
    """Claude via Messages API com saída estruturada (`messages.parse`).

    Sem `client`, usa as credenciais do ambiente (ANTHROPIC_API_KEY).
    """

    name = "anthropic"

    def __init__(
        self, model: str, client: anthropic.Anthropic | None = None, max_tokens: int = 4096
    ) -> None:
        self.model = model
        self._client = client or anthropic.Anthropic()
        self._max_tokens = max_tokens

    def complete(self, prompt: str, schema: type[T]) -> T:
        message = self._client.messages.parse(
            model=self.model,
            max_tokens=self._max_tokens,
            messages=[{"role": "user", "content": prompt}],
            output_format=schema,
        )
        if message.parsed_output is None:
            raise LLMResponseError(f"sem saída estruturada (stop_reason={message.stop_reason})")
        return message.parsed_output
