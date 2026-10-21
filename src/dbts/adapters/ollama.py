from typing import TypeVar

import httpx
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

DEFAULT_URL = "http://localhost:11434"


class OllamaProvider:
    """Chama /api/chat com saída estruturada pelo JSON schema do modelo Pydantic."""

    name = "ollama"

    def __init__(self, model: str, client: httpx.Client | None = None) -> None:
        self.model = model
        self._client = client or httpx.Client(base_url=DEFAULT_URL, timeout=300)

    def complete(self, prompt: str, schema: type[T]) -> T:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "format": schema.model_json_schema(),
            "stream": False,
            "think": False,
            "options": {"temperature": 0},
        }
        response = self._client.post("/api/chat", json=payload)
        response.raise_for_status()
        return schema.model_validate_json(response.json()["message"]["content"])
