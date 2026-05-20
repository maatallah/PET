from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.prompt_run import PromptRun
    from app.models.session import Session


class Prompt(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "prompts"

    version: Mapped[int] = mapped_column(Integer, default=1)
    name: Mapped[str] = mapped_column(String(255))
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    variables: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=list)
    prompt_pattern: Mapped[str | None] = mapped_column(String(50), nullable=True)
    model_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model_params: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)
    tokens_input: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tokens_output: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_estimate: Mapped[float | None] = mapped_column(Float, nullable=True)
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    session_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("sessions.id"))
    parent_version_id: Mapped[str | None] = mapped_column(
        Uuid(as_uuid=False), ForeignKey("prompts.id"), nullable=True
    )

    session: Mapped[Session] = relationship(back_populates="prompts")
    parent_version: Mapped[Prompt | None] = relationship(
        back_populates="child_versions", remote_side="Prompt.id"
    )
    child_versions: Mapped[list[Prompt]] = relationship(back_populates="parent_version")
    runs: Mapped[list[PromptRun]] = relationship(back_populates="prompt")
