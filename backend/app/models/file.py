from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.session import Session


class File(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "files"

    filename: Mapped[str] = mapped_column(String(255))
    original_name: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    storage_path: Mapped[str] = mapped_column(String(512))
    content_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)
    session_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("sessions.id"))

    session: Mapped[Session] = relationship(back_populates="files")
