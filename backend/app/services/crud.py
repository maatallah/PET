from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base


class CRUDBase[ModelT: Base]:
    def __init__(self, model: type[ModelT]):
        self.model = model

    async def create(self, session: AsyncSession, data: dict[str, Any]) -> ModelT:
        obj = self.model(**data)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def get(self, session: AsyncSession, id: str) -> ModelT | None:
        try:
            uuid.UUID(id)
        except ValueError:
            return None
        stmt = select(self.model).where(self.model.id == id)  # type: ignore[attr-defined]
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        session: AsyncSession,
        parent_field: str | None = None,
        parent_id: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelT]:
        stmt = select(self.model)
        if parent_field and parent_id:
            stmt = stmt.where(getattr(self.model, parent_field) == parent_id)
        stmt = stmt.offset(skip).limit(limit).order_by(self.model.created_at.desc())  # type: ignore[attr-defined]
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, session: AsyncSession, id: str, data: dict[str, Any]) -> ModelT | None:
        obj = await self.get(session, id)
        if not obj:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(obj, key, value)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def delete(self, session: AsyncSession, id: str) -> bool:
        obj = await self.get(session, id)
        if not obj:
            return False
        await session.delete(obj)
        await session.commit()
        return True

    async def count(
        self, session: AsyncSession, parent_field: str | None = None, parent_id: str | None = None
    ) -> int:
        stmt = select(func.count()).select_from(self.model)
        if parent_field and parent_id:
            stmt = stmt.where(getattr(self.model, parent_field) == parent_id)
        result = await session.execute(stmt)
        return result.scalar_one()
