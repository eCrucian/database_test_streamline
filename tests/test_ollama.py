import json

import httpx
import pytest
from pydantic import BaseModel

from dbts.adapters.ollama import OllamaProvider


class Answer(BaseModel):
    text: str


def _client(handler: httpx.MockTransport) -> httpx.Client:
    return httpx.Client(base_url="http://ollama", transport=handler)


def test_ollama_sends_schema_and_parses_response() -> None:
    sent: list[dict[str, object]] = []

    def handle(request: httpx.Request) -> httpx.Response:
        sent.append(json.loads(request.content))
        return httpx.Response(200, json={"message": {"content": '{"text": "oi"}'}})

    provider = OllamaProvider("qwen3:4b", _client(httpx.MockTransport(handle)))
    assert provider.complete("prompt", Answer).text == "oi"
    assert sent[0]["model"] == "qwen3:4b"
    assert sent[0]["format"] == Answer.model_json_schema()
    assert sent[0]["stream"] is False
    assert sent[0]["think"] is False


def test_ollama_raises_on_http_error() -> None:
    transport = httpx.MockTransport(lambda _: httpx.Response(500))
    with pytest.raises(httpx.HTTPStatusError):
        OllamaProvider("m", _client(transport)).complete("p", Answer)


def test_ollama_default_client_points_to_localhost() -> None:
    provider = OllamaProvider("m")
    assert str(provider._client.base_url) == "http://localhost:11434"
