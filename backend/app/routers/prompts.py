from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.prompt import PromptCreate, PromptRead, PromptUpdate
from app.services.prompt import prompt_service

router = APIRouter(prefix="/sessions/{session_id}/prompts", tags=["prompts"])


@router.post("", response_model=PromptRead, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    session_id: str, data: PromptCreate, session: AsyncSession = Depends(get_session)
):
    return await prompt_service.create(session, {**data.model_dump(), "session_id": session_id})


@router.get("", response_model=list[PromptRead])
async def list_prompts(
    session_id: str, skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)
):
    return await prompt_service.list(
        session, parent_field="session_id", parent_id=session_id, skip=skip, limit=limit
    )


@router.get("/{prompt_id}", response_model=PromptRead)
async def get_prompt(prompt_id: str, _=None, session: AsyncSession = Depends(get_session)):
    obj = await prompt_service.get(session, prompt_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    return obj


@router.patch("/{prompt_id}", response_model=PromptRead)
async def update_prompt(
    prompt_id: str, data: PromptUpdate, session: AsyncSession = Depends(get_session)
):
    obj = await prompt_service.update(session, prompt_id, data.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    return obj


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(prompt_id: str, session: AsyncSession = Depends(get_session)):
    deleted = await prompt_service.delete(session, prompt_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
