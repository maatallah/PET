from datetime import datetime

from pydantic import BaseModel


class PromptExecuteRequest(BaseModel):
    variables: dict[str, str] = {}
    model: str | None = None
    model_params: dict | None = None
    provider: str = "openai"
    dry_run: bool = True


class PromptExecuteResponse(BaseModel):
    id: str
    resolved_prompt: str
    model_response: str | None = None
    response: str | None = None
    tokens_input: int | None = None
    tokens_output: int | None = None
    cost_estimate: float | None = None
    latency_ms: int | None = None
    finish_reason: str | None = None
    detected_variables: list[str] = []
    unsubstituted_variables: list[str] = []
    prompt_id: str
    created_at: datetime
