from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    async def execute(
        self,
        prompt: str,
        model: str,
        params: dict | None = None,
    ) -> dict: ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    def validate_params(self, params: dict | None) -> dict:
        return params or {}
