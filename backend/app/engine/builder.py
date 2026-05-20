from app.engine.patterns import get_pattern
from app.engine.tokenizer import count_tokens, estimate_cost
from app.engine.variables import extract_variables, substitute_all


def build_prompt(
    system_prompt: str | None,
    user_prompt: str | None,
    variables: dict[str, str] | None = None,
    pattern: str | None = None,
    model: str | None = None,
) -> dict:
    variables = variables or {}
    model = model or "gpt-4"

    pattern_obj = get_pattern(pattern)
    sp, up = pattern_obj.apply(system_prompt, user_prompt)
    sp, up = substitute_all(sp, up, variables)

    resolved = ""
    if sp:
        resolved += f"<system>\n{sp}\n</system>\n\n"
    if up:
        resolved += f"<user>\n{up}\n</user>"
    resolved = resolved.strip()

    tokens = count_tokens(resolved, model)
    cost = estimate_cost(tokens, model)
    extracted = extract_variables(system_prompt or "") + extract_variables(user_prompt or "")
    detected_vars = list(set(extracted))

    return {
        "resolved_prompt": resolved,
        "tokens_input": tokens,
        "cost_estimate": cost,
        "detected_variables": detected_vars,
        "unsubstituted_variables": [v for v in detected_vars if v not in variables],
    }
