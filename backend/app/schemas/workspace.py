from datetime import datetime

from pydantic import BaseModel


class WorkspaceCreate(BaseModel):
    name: str
    description: str | None = None
    owner_id: str | None = None


class WorkspaceRead(BaseModel):
    id: str
    name: str
    description: str | None
    owner_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkspaceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
