from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.prompt_template import (
    PromptTemplateCreate,
    PromptTemplateRead,
    PromptTemplateUpdate,
)
from app.services.prompt_template import prompt_template_service

router = APIRouter(prefix="/templates", tags=["templates"])


@router.post("", response_model=PromptTemplateRead, status_code=status.HTTP_201_CREATED)
async def create_template(data: PromptTemplateCreate, session: AsyncSession = Depends(get_session)):
    return await prompt_template_service.create(session, data.model_dump())


@router.get("", response_model=list[PromptTemplateRead])
async def list_templates(
    skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)
):
    return await prompt_template_service.list(session, skip=skip, limit=limit)


@router.get("/{template_id}", response_model=PromptTemplateRead)
async def get_template(template_id: str, session: AsyncSession = Depends(get_session)):
    obj = await prompt_template_service.get(session, template_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    return obj


@router.patch("/{template_id}", response_model=PromptTemplateRead)
async def update_template(
    template_id: str, data: PromptTemplateUpdate, session: AsyncSession = Depends(get_session)
):
    obj = await prompt_template_service.update(
        session, template_id, data.model_dump(exclude_unset=True)
    )
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    return obj


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(template_id: str, session: AsyncSession = Depends(get_session)):
    deleted = await prompt_template_service.delete(session, template_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
