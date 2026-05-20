from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.file import File
    from app.models.project import Project
    from app.models.prompt import Prompt


class Session(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sessions"

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    project_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("projects.id"))

    project: Mapped[Project] = relationship(back_populates="sessions")
    prompts: Mapped[list[Prompt]] = relationship(back_populates="session")
    files: Mapped[list[File]] = relationship(back_populates="session")
