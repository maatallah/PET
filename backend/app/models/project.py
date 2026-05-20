from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.session import Session
    from app.models.workspace import Workspace


class Project(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
    workspace_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("workspaces.id"))

    workspace: Mapped[Workspace] = relationship(back_populates="projects")
    sessions: Mapped[list[Session]] = relationship(back_populates="project")
