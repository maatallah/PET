from datetime import datetime

from pydantic import BaseModel


class PromptTemplateCreate(BaseModel):
    name: str
    description: str | None = None
    category: str | None = None
    system_prompt: str | None = None
    user_prompt: str | None = None
    variables: list | None = None
    pattern: str | None = None
    is_public: bool = False


class PromptTemplateRead(BaseModel):
    id: str
    name: str
    description: str | None
    category: str | None
    system_prompt: str | None
    user_prompt: str | None
    variables: list | None
    pattern: str | None
    is_public: bool
    usage_count: int
    rating_avg: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PromptTemplateUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    system_prompt: str | None = None
    user_prompt: str | None = None
    variables: list | None = None
    pattern: str | None = None
    is_public: bool | None = None
