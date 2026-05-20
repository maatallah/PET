from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.session import SessionCreate, SessionRead, SessionUpdate
from app.services.session import session_service

router = APIRouter(prefix="/projects/{project_id}/sessions", tags=["sessions"])


@router.post("", response_model=SessionRead, status_code=status.HTTP_201_CREATED)
async def create_session(
    project_id: str, data: SessionCreate, session: AsyncSession = Depends(get_session)
):
    return await session_service.create(session, {**data.model_dump(), "project_id": project_id})


@router.get("", response_model=list[SessionRead])
async def list_sessions(
    project_id: str, skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)
):
    return await session_service.list(
        session, parent_field="project_id", parent_id=project_id, skip=skip, limit=limit
    )


@router.get("/{session_id}", response_model=SessionRead)
async def read_session(session_id: str, _=None, session: AsyncSession = Depends(get_session)):
    obj = await session_service.get(session, session_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return obj


@router.patch("/{session_id}", response_model=SessionRead)
async def update_session(
    session_id: str, data: SessionUpdate, session: AsyncSession = Depends(get_session)
):
    obj = await session_service.update(session, session_id, data.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return obj


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str, session: AsyncSession = Depends(get_session)):
    deleted = await session_service.delete(session, session_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
