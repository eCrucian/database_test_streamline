from collections.abc import Mapping
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict

ENV_MAP_DIR = "DBTS_MAP_DIR"
ENV_PROVIDER = "DBTS_LLM_PROVIDER"
ENV_MODEL = "DBTS_LLM_MODEL"
ENV_QUERIES_DIR = "DBTS_QUERIES_DIR"
ENV_STORE = "DBTS_STORE"


class StoreName(StrEnum):
    SQLITE = "sqlite"
    DUCKDB = "duckdb"


class ProviderName(StrEnum):
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"
    AZURE = "azure"


DEFAULT_MODELS = {
    ProviderName.OLLAMA: "qwen3:4b",
    ProviderName.ANTHROPIC: "claude-sonnet-5-5",
    ProviderName.AZURE: "",  # nome do deployment: obrigatório via DBTS_LLM_MODEL
}


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)

    map_dir: Path
    llm_provider: ProviderName
    llm_model: str
    queries_dir: Path
    store: StoreName = StoreName.SQLITE

    @property
    def audit_dir(self) -> Path:
        return self.map_dir / "audit"

    @property
    def guides_dir(self) -> Path:
        return self.map_dir / "guides"

    @property
    def plans_dir(self) -> Path:
        return self.map_dir / "plans"

    @property
    def reports_dir(self) -> Path:
        return self.map_dir / "reports"


def resolve_settings(env: Mapping[str, str], home: Path, map_dir: Path | None = None) -> Settings:
    """Precedência: argumento explícito > variável de ambiente > padrão em ~/.dbts.

    Queries executadas vão para $DBTS_QUERIES_DIR ou <map_dir>/queries. O LLM vem de
    $DBTS_LLM_PROVIDER (padrão ollama) e $DBTS_LLM_MODEL (padrão por provider). O MapStore vem de
    $DBTS_STORE (sqlite, padrão, ou duckdb).
    """
    chosen = (map_dir or Path(env.get(ENV_MAP_DIR, home / ".dbts"))).expanduser()
    queries = Path(env.get(ENV_QUERIES_DIR, chosen / "queries")).expanduser()
    provider = ProviderName(env.get(ENV_PROVIDER, ProviderName.OLLAMA))
    return Settings(
        map_dir=chosen,
        llm_provider=provider,
        llm_model=env.get(ENV_MODEL, DEFAULT_MODELS[provider]),
        queries_dir=queries,
        store=StoreName(env.get(ENV_STORE, StoreName.SQLITE)),
    )
