import time

from app.core.config import settings
from app.engine.providers.base import LLMProvider

try:
    from google import genai

    _HAS_GOOGLE = True
except ImportError:
    _HAS_GOOGLE = False


class GoogleProvider(LLMProvider):
    def __init__(self) -> None:
        self._client: genai.Client | None = None

    @property
    def name(self) -> str:
        return "google"

    def _get_client(self) -> genai.Client:
        if self._client is None:
            if not _HAS_GOOGLE:
                raise ImportError("google-genai not installed. Run: pip install google-genai")
            if not settings.GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY not set in .env or environment")
            self._client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        return self._client

    async def execute(
        self,
        prompt: str,
        model: str = "gemini-2.0-flash",
        params: dict | None = None,
    ) -> dict:
        client = self._get_client()
        p = self.validate_params(params)
        start = time.monotonic()

        response = await client.aio.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "temperature": p.get("temperature", 0.7),
                "max_output_tokens": p.get("max_tokens", 2048),
            },
        )

        elapsed_ms = int((time.monotonic() - start) * 1000)
        usage = response.usage_metadata
        tokens_in = usage.prompt_token_count if usage else None
        tokens_out = usage.candidates_token_count if usage else None
        finish = str(response.candidates[0].finish_reason) if response.candidates else None

        return {
            "model_response": response.text or "",
            "model_raw": {},
            "tokens_input": tokens_in,
            "tokens_output": tokens_out,
            "latency_ms": elapsed_ms,
            "finish_reason": finish,
        }
