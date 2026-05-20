import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.workspace import WorkspaceCreate, WorkspaceRead, WorkspaceUpdate
from app.services.workspace import workspace_service

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
async def create_workspace(data: WorkspaceCreate, session: AsyncSession = Depends(get_session)):
    payload = data.model_dump()
    if not payload.get("owner_id"):
        payload["owner_id"] = str(uuid.uuid4())
    return await workspace_service.create(session, payload)


@router.get("", response_model=list[WorkspaceRead])
async def list_workspaces(
    skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)
):
    return await workspace_service.list(session, skip=skip, limit=limit)


@router.get("/{workspace_id}", response_model=WorkspaceRead)
async def get_workspace(workspace_id: str, session: AsyncSession = Depends(get_session)):
    obj = await workspace_service.get(session, workspace_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return obj


@router.patch("/{workspace_id}", response_model=WorkspaceRead)
async def update_workspace(
    workspace_id: str, data: WorkspaceUpdate, session: AsyncSession = Depends(get_session)
):
    obj = await workspace_service.update(session, workspace_id, data.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return obj


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(workspace_id: str, session: AsyncSession = Depends(get_session)):
    deleted = await workspace_service.delete(session, workspace_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
