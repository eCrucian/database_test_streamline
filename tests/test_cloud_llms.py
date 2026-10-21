import json
from typing import Any

import anthropic
import httpx2
import openai
import pytest
from pydantic import BaseModel

from dbts.adapters.anthropic_llm import AnthropicProvider
from dbts.adapters.azure_llm import AzureOpenAIProvider
from dbts.adapters.llm import build_llm
from dbts.config import resolve_settings
from dbts.ports import LLMResponseError


class Answer(BaseModel):
    text: str


def _http(body: dict[str, Any], sent: list[dict[str, Any]]) -> httpx2.Client:
    def handle(request: httpx2.Request) -> httpx2.Response:
        sent.append(json.loads(request.content))
        return httpx2.Response(200, json=body)

    return httpx2.Client(transport=httpx2.MockTransport(handle))


def _message(text: str, stop: str = "end_turn") -> dict[str, Any]:
    return {
        "id": "msg_1",
        "type": "message",
        "role": "assistant",
        "model": "claude-sonnet-5-5",
        "content": [{"type": "text", "text": text}],
        "stop_reason": stop,
        "stop_sequence": None,
        "usage": {"input_tokens": 1, "output_tokens": 1},
    }


def _completion(content: str | None, refusal: str | None = None) -> dict[str, Any]:
    message = {"role": "assistant", "content": content, "refusal": refusal}
    return {
        "id": "c1",
        "object": "chat.completion",
        "created": 0,
        "model": "dep",
        "choices": [{"index": 0, "message": message, "finish_reason": "stop"}],
    }


def _anthropic(body: dict[str, Any], sent: list[dict[str, Any]]) -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key="k", http_client=_http(body, sent), max_retries=0)


def _azure(body: dict[str, Any], sent: list[dict[str, Any]]) -> openai.AzureOpenAI:
    return openai.AzureOpenAI(
        api_key="k",
        api_version="2024-10-21",
        azure_endpoint="https://x.openai.azure.com",
        http_client=_http(body, sent),
        max_retries=0,
    )


def test_anthropic_structured_output() -> None:
    sent: list[dict[str, Any]] = []
    provider = AnthropicProvider("claude-sonnet-5-5", _anthropic(_message('{"text": "oi"}'), sent))
    assert provider.complete("prompt", Answer).text == "oi"
    assert sent[0]["model"] == "claude-sonnet-5-5"
    assert sent[0]["messages"] == [{"role": "user", "content": "prompt"}]


def test_anthropic_without_parsed_output_raises() -> None:
    client = _anthropic({**_message("x", stop="refusal"), "content": []}, [])
    with pytest.raises(LLMResponseError, match="refusal"):
        AnthropicProvider("m", client).complete("p", Answer)


def test_azure_structured_output() -> None:
    sent: list[dict[str, Any]] = []
    provider = AzureOpenAIProvider("dep", _azure(_completion('{"text": "oi"}'), sent))
    assert provider.complete("prompt", Answer).text == "oi"
    assert sent[0]["model"] == "dep"
    assert sent[0]["response_format"]["type"] == "json_schema"


def test_azure_refusal_raises() -> None:
    client = _azure(_completion(None, refusal="não posso"), [])
    with pytest.raises(LLMResponseError, match="não posso"):
        AzureOpenAIProvider("dep", client).complete("p", Answer)


def test_build_llm_per_provider(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "k")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://x.openai.azure.com")
    monkeypatch.setenv("OPENAI_API_VERSION", "2024-10-21")

    def llm(env: dict[str, str]) -> tuple[str, str]:
        provider = build_llm(resolve_settings(env, tmp_path))
        return provider.name, provider.model

    assert llm({}) == ("ollama", "qwen3:4b")
    assert llm({"DBTS_LLM_PROVIDER": "anthropic"}) == ("anthropic", "claude-sonnet-5-5")
    assert llm({"DBTS_LLM_PROVIDER": "azure", "DBTS_LLM_MODEL": "dep"}) == ("azure", "dep")
    with pytest.raises(ValueError, match="deployment"):
        llm({"DBTS_LLM_PROVIDER": "azure"})
