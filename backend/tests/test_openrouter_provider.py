from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.engine.providers.openrouter import OpenRouterProvider


@pytest.fixture
def provider():
    return OpenRouterProvider()


def _make_mock_client(response_text: str = "Hello", finish: str = "stop", prompt_tokens: int = 10, output_tokens: int = 5):
    mock_choice = MagicMock()
    mock_choice.message.content = response_text
    mock_choice.finish_reason = finish

    mock_usage = MagicMock()
    mock_usage.prompt_tokens = prompt_tokens
    mock_usage.completion_tokens = output_tokens

    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    mock_completion.usage = mock_usage
    mock_completion.model_dump.return_value = {"id": "test-123"}

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
    return mock_client


@pytest.mark.anyio
async def test_provider_name(provider):
    assert provider.name == "openrouter"


@pytest.mark.anyio
async def test_execute_success(provider):
    mock_client = _make_mock_client(response_text="Hello from OpenRouter")
    provider._get_client = MagicMock(return_value=mock_client)

    result = await provider.execute("test prompt", model="openai/gpt-4o-mini")

    assert result["model_response"] == "Hello from OpenRouter"
    assert result["tokens_input"] == 10
    assert result["tokens_output"] == 5
    assert result["finish_reason"] == "stop"
    assert result["latency_ms"] >= 0
    assert result["model_raw"] == {"id": "test-123"}


@pytest.mark.anyio
async def test_execute_custom_params(provider):
    mock_client = _make_mock_client()
    provider._get_client = MagicMock(return_value=mock_client)

    await provider.execute("prompt", model="anthropic/claude-3.5", params={"temperature": 0.1, "max_tokens": 500})

    create_call = mock_client.chat.completions.create
    create_call.assert_awaited_once()
    _, kwargs = create_call.call_args
    assert kwargs["model"] == "anthropic/claude-3.5"
    assert kwargs["temperature"] == 0.1
    assert kwargs["max_tokens"] == 500


@pytest.mark.anyio
async def test_execute_import_error():
    with patch("app.engine.providers.openrouter._HAS_OPENAI", False):
        p = OpenRouterProvider()
        with pytest.raises(ImportError, match="openai package not installed"):
            await p.execute("test", model="openai/gpt-4o-mini")
