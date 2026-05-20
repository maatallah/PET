from abc import ABC, abstractmethod

PromptTransform = tuple[str | None, str | None]


class PromptPattern(ABC):
    label: str

    @abstractmethod
    def apply(self, system_prompt: str | None, user_prompt: str | None) -> PromptTransform: ...


class PersonaPattern(PromptPattern):
    label = "persona"

    def apply(self, system_prompt: str | None, user_prompt: str | None) -> PromptTransform:
        if system_prompt and not system_prompt.startswith("You are"):
            system_prompt = f"You are a helpful assistant. {system_prompt}"
        return system_prompt, user_prompt


class ChainOfThoughtPattern(PromptPattern):
    label = "cot"

    def apply(self, system_prompt: str | None, user_prompt: str | None) -> PromptTransform:
        if user_prompt:
            user_prompt = f"{user_prompt}\n\nLet's work through this step by step."
        return system_prompt, user_prompt


class FewShotPattern(PromptPattern):
    label = "few_shot"

    def apply(self, system_prompt: str | None, user_prompt: str | None) -> PromptTransform:
        if system_prompt and "example" not in system_prompt.lower():
            system_prompt = f"{system_prompt}\n\nProvide examples where applicable."
        return system_prompt, user_prompt


class TemplatePattern(PromptPattern):
    label = "template"

    def apply(self, system_prompt: str | None, user_prompt: str | None) -> PromptTransform:
        return system_prompt, user_prompt


_patterns: dict[str, PromptPattern] = {
    p.label: p
    for p in [
        PersonaPattern(),
        ChainOfThoughtPattern(),
        FewShotPattern(),
        TemplatePattern(),
    ]
}


def get_pattern(label: str | None) -> PromptPattern:
    return _patterns.get(label or "template", _patterns["template"])


def list_patterns() -> list[dict[str, str]]:
    return [{"label": p.label} for p in _patterns.values()]
