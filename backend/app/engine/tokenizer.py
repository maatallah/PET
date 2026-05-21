import math

try:
    import tiktoken

    def count_tokens(text: str, model: str = "gpt-4") -> int:
        try:
            enc = tiktoken.encoding_for_model(model)
        except KeyError:
            enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))

except ImportError:
    _HAS_TIKTOKEN = False

    def count_tokens(text: str, model: str = "gpt-4") -> int:
        return math.ceil(len(text) / 4)


def estimate_cost(tokens: int, model: str = "gpt-4") -> float:
    rates = {
        "gpt-4": (0.03, 0.06),
        "gpt-4-turbo": (0.01, 0.03),
        "gpt-3.5-turbo": (0.001, 0.002),
        "gpt-4o": (0.0025, 0.01),
        "gpt-4o-mini": (0.00015, 0.0006),
    }
    input_rate, output_rate = rates.get(model, (0.01, 0.03))
    return round((tokens / 1000) * input_rate, 6)


MODEL_CONTEXT_WINDOWS: dict[str, int] = {
    "gpt-4": 8192,
    "gpt-4-turbo": 128000,
    "gpt-4o": 128000,
    "gpt-4o-mini": 128000,
    "gpt-3.5-turbo": 16385,
    "claude-3-opus": 200000,
    "claude-3-sonnet": 200000,
    "claude-3.5-sonnet": 200000,
    "claude-3-haiku": 200000,
    "gemini-pro": 32768,
    "gemini-1.5-pro": 1048576,
    "llama3.2": 131072,
    "llama3.1": 131072,
    "mixtral": 32768,
    "command-r": 131072,
}


def get_context_window(model: str) -> int:
    for key, size in MODEL_CONTEXT_WINDOWS.items():
        if key in model:
            return size
    return 128000
