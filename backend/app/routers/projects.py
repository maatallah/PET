from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services.project import project_service

router = APIRouter(prefix="/workspaces/{workspace_id}/projects", tags=["projects"])


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    workspace_id: str, data: ProjectCreate, session: AsyncSession = Depends(get_session)
):
    return await project_service.create(
        session, {**data.model_dump(), "workspace_id": workspace_id}
    )


@router.get("", response_model=list[ProjectRead])
async def list_projects(
    workspace_id: str, skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)
):
    return await project_service.list(
        session, parent_field="workspace_id", parent_id=workspace_id, skip=skip, limit=limit
    )


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(project_id: str, _=None, session: AsyncSession = Depends(get_session)):
    obj = await project_service.get(session, project_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return obj


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: str, data: ProjectUpdate, session: AsyncSession = Depends(get_session)
):
    obj = await project_service.update(session, project_id, data.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return obj


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str, session: AsyncSession = Depends(get_session)):
    deleted = await project_service.delete(session, project_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
