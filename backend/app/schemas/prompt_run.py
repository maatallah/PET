from datetime import datetime

from pydantic import BaseModel


class PromptRunCreate(BaseModel):
    resolved_prompt: str | None = None
    model_response: str | None = None
    model_raw: dict | None = None
    tokens_input: int | None = None
    tokens_output: int | None = None
    cost: float | None = None
    latency_ms: int | None = None
    rating: int | None = None
    feedback: str | None = None


class PromptRunRead(BaseModel):
    id: str
    resolved_prompt: str | None
    model_response: str | None
    model_raw: dict | None
    tokens_input: int | None
    tokens_output: int | None
    cost: float | None
    latency_ms: int | None
    rating: int | None
    feedback: str | None
    prompt_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
