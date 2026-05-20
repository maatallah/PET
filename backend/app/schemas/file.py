from datetime import datetime

from pydantic import BaseModel


class FileCreate(BaseModel):
    filename: str
    original_name: str
    mime_type: str | None = None
    size_bytes: int | None = None
    storage_path: str
    content_text: str | None = None
    file_metadata: dict | None = None


class FileRead(BaseModel):
    id: str
    filename: str
    original_name: str
    mime_type: str | None
    size_bytes: int | None
    storage_path: str
    content_text: str | None
    file_metadata: dict | None
    session_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
