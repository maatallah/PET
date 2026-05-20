from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, Float, ForeignKey, Integer, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.prompt import Prompt


class PromptRun(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "prompt_runs"

    resolved_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_raw: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    tokens_input: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tokens_output: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    prompt_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("prompts.id"))

    prompt: Mapped[Prompt] = relationship(back_populates="runs")
