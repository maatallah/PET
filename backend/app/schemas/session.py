from datetime import datetime

from pydantic import BaseModel


class SessionCreate(BaseModel):
    name: str
    description: str | None = None
    tags: list[str] | None = None


class SessionRead(BaseModel):
    id: str
    name: str
    description: str | None
    tags: list | None
    project_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    tags: list[str] | None = None
