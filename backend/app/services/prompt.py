from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prompt import Prompt
from app.services.crud import CRUDBase


class PromptService(CRUDBase[Prompt]):
    async def create(self, session: AsyncSession, data: dict[str, Any]) -> Prompt:
        latest = await self._latest_version(session, data["session_id"])
        data["version"] = (latest or 0) + 1
        if latest:
            data["parent_version_id"] = data.pop("parent_version_id", None)
        return await super().create(session, data)

    async def update(self, session: AsyncSession, id: str, data: dict[str, Any]) -> Prompt | None:
        existing = await self.get(session, id)
        if not existing:
            return None
        data.pop("version", None)
        data.pop("session_id", None)
        for key, value in data.items():
            if value is not None:
                setattr(existing, key, value)
        await session.commit()
        await session.refresh(existing)
        return existing

    async def list_versions(self, session: AsyncSession, prompt_id: str) -> list[Prompt]:
        root = await self.get(session, prompt_id)
        if not root:
            return []
        stmt = (
            select(self.model)
            .where(
                self.model.session_id == root.session_id,
                self.model.name == root.name,
            )
            .order_by(self.model.version.desc())
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def _latest_version(self, session: AsyncSession, session_id: str) -> int | None:
        stmt = (
            select(self.model.version)
            .where(self.model.session_id == session_id)
            .order_by(self.model.version.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


prompt_service = PromptService(Prompt)
