from pathlib import Path

import pytest

from dbts.config import ProviderName, resolve_settings


def test_defaults_to_home_dbts(tmp_path: Path) -> None:
    settings = resolve_settings({}, tmp_path)
    assert settings.map_dir == tmp_path / ".dbts"
    assert settings.audit_dir == tmp_path / ".dbts" / "audit"
    assert (settings.llm_provider, settings.llm_model) == (ProviderName.OLLAMA, "qwen3:4b")
    assert settings.queries_dir == tmp_path / ".dbts" / "queries"


def test_env_overrides_default(tmp_path: Path) -> None:
    env = {"DBTS_MAP_DIR": str(tmp_path / "env"), "DBTS_LLM_MODEL": "other"}
    settings = resolve_settings(env, tmp_path)
    assert settings.map_dir == tmp_path / "env"
    assert settings.llm_model == "other"


def test_argument_overrides_env(tmp_path: Path) -> None:
    env = {"DBTS_MAP_DIR": str(tmp_path / "env")}
    assert resolve_settings(env, tmp_path, tmp_path / "arg").map_dir == tmp_path / "arg"


def test_provider_defaults_and_overrides(tmp_path: Path) -> None:
    anthropic = resolve_settings({"DBTS_LLM_PROVIDER": "anthropic"}, tmp_path)
    assert anthropic.llm_model == "claude-sonnet-5-5"
    azure = resolve_settings({"DBTS_LLM_PROVIDER": "azure"}, tmp_path)
    assert azure.llm_model == ""
    env = {"DBTS_LLM_PROVIDER": "azure", "DBTS_LLM_MODEL": "gpt-dep", "DBTS_QUERIES_DIR": "/q"}
    custom = resolve_settings(env, tmp_path)
    assert (custom.llm_model, custom.queries_dir) == ("gpt-dep", Path("/q"))


def test_unknown_provider_fails(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        resolve_settings({"DBTS_LLM_PROVIDER": "outro"}, tmp_path)
