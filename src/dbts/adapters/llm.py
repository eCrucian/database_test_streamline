from dbts.adapters.anthropic_llm import AnthropicProvider
from dbts.adapters.azure_llm import AzureOpenAIProvider
from dbts.adapters.ollama import OllamaProvider
from dbts.config import ProviderName, Settings
from dbts.ports import LLMProvider


def build_llm(settings: Settings) -> LLMProvider:
    model = settings.llm_model
    if settings.llm_provider is ProviderName.ANTHROPIC:
        return AnthropicProvider(model)
    if settings.llm_provider is ProviderName.AZURE:
        if not model:
            raise ValueError("defina DBTS_LLM_MODEL com o nome do deployment Azure")
        return AzureOpenAIProvider(model)
    return OllamaProvider(model)
