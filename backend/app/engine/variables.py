import re

_VAR_PATTERN = re.compile(r"\{(\w+)\}")


def extract_variables(text: str) -> list[str]:
    return list(set(_VAR_PATTERN.findall(text)))


def substitute(text: str, variables: dict[str, str]) -> str:
    def _replacer(m: re.Match) -> str:
        return variables.get(m.group(1), m.group(0))

    return _VAR_PATTERN.sub(_replacer, text)


def substitute_all(
    system_prompt: str | None,
    user_prompt: str | None,
    variables: dict[str, str],
) -> tuple[str | None, str | None]:
    sp = substitute(system_prompt, variables) if system_prompt else None
    up = substitute(user_prompt, variables) if user_prompt else None
    return sp, up
