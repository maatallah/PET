import time

from app.core.config import settings
from app.engine.providers.base import LLMProvider

try:
    from openai import AsyncOpenAI

    _HAS_OPENAI = True
except ImportError:
    _HAS_OPENAI = False


class OpenRouterProvider(LLMProvider):
    def __init__(self) -> None:
        self._client: AsyncOpenAI | None = None

    @property
    def name(self) -> str:
        return "openrouter"

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            if not _HAS_OPENAI:
                raise ImportError("openai package not installed. Run: pip install openai")
            self._client = AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=settings.OPENROUTER_API_KEY,
            )
        return self._client

    async def execute(
        self,
        prompt: str,
        model: str = "openai/gpt-4o-mini",
        params: dict | None = None,
    ) -> dict:
        client = self._get_client()
        p = self.validate_params(params)
        start = time.monotonic()

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=p.get("temperature", 0.7),
            max_tokens=p.get("max_tokens", 2048),
        )

        elapsed_ms = int((time.monotonic() - start) * 1000)
        choice = response.choices[0]

        return {
            "model_response": choice.message.content or "",
            "model_raw": response.model_dump() if hasattr(response, "model_dump") else {},
            "tokens_input": response.usage.prompt_tokens if response.usage else None,
            "tokens_output": response.usage.completion_tokens if response.usage else None,
            "latency_ms": elapsed_ms,
            "finish_reason": choice.finish_reason,
        }
