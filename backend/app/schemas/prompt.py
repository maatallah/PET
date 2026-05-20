from datetime import datetime

from pydantic import BaseModel


class PromptCreate(BaseModel):
    name: str
    system_prompt: str | None = None
    user_prompt: str | None = None
    variables: list | None = None
    prompt_pattern: str | None = None
    model_id: str | None = None
    model_params: dict | None = None


class PromptRead(BaseModel):
    id: str
    version: int
    name: str
    system_prompt: str | None
    user_prompt: str | None
    variables: list | None
    prompt_pattern: str | None
    model_id: str | None
    model_params: dict | None
    tokens_input: int | None
    tokens_output: int | None
    cost_estimate: float | None
    tags: list | None
    session_id: str
    parent_version_id: str | None
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class PromptUpdate(BaseModel):
    name: str | None = None
    system_prompt: str | None = None
    user_prompt: str | None = None
    variables: list | None = None
    prompt_pattern: str | None = None
    model_id: str | None = None
    model_params: dict | None = None
    tags: list[str] | None = None
