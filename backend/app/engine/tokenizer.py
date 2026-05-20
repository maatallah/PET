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
    }
    input_rate, output_rate = rates.get(model, (0.01, 0.03))
    return round((tokens / 1000) * input_rate, 6)
