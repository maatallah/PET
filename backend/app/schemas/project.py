from datetime import datetime

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    icon: str | None = None


class ProjectRead(BaseModel):
    id: str
    name: str
    description: str | None
    icon: str | None
    archived: bool
    workspace_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    icon: str | None = None
    archived: bool | None = None
