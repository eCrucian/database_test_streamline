from typing import TypeVar

import openai
from pydantic import BaseModel

from dbts.ports import LLMResponseError

T = TypeVar("T", bound=BaseModel)


class AzureOpenAIProvider:
    """Azure OpenAI com structured outputs (`chat.completions.parse`).

    `model` é o nome do deployment. Sem `client`, usa AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT e OPENAI_API_VERSION do ambiente.
    """

    name = "azure"

    def __init__(self, model: str, client: openai.AzureOpenAI | None = None) -> None:
        self.model = model
        self._client = client or openai.AzureOpenAI()

    def complete(self, prompt: str, schema: type[T]) -> T:
        completion = self._client.chat.completions.parse(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format=schema,
        )
        message = completion.choices[0].message
        if message.parsed is None:
            raise LLMResponseError(f"sem saída estruturada (refusal={message.refusal})")
        return message.parsed
