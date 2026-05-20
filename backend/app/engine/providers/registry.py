from app.engine.providers.base import LLMProvider
from app.engine.providers.google import GoogleProvider
from app.engine.providers.ollama import OllamaProvider
from app.engine.providers.openai import OpenAIProvider
from app.engine.providers.openrouter import OpenRouterProvider

_providers: dict[str, LLMProvider] = {}


def register(provider: LLMProvider) -> None:
    _providers[provider.name] = provider


def get_provider(name: str) -> LLMProvider | None:
    return _providers.get(name)


def list_providers() -> list[str]:
    return list(_providers.keys())


register(OpenAIProvider())
register(GoogleProvider())
register(OllamaProvider())
register(OpenRouterProvider())
