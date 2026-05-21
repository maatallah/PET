from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.engine.builder import build_prompt
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


@router.get("/{prompt_id}/export")
async def export_prompt(
    prompt_id: str,
    format: str = "markdown",
    session: AsyncSession = Depends(get_session),
):
    prompt = await prompt_service.get(session, prompt_id)
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")

    if format == "json":
        return {
            "name": prompt.name,
            "version": prompt.version,
            "system_prompt": prompt.system_prompt,
            "user_prompt": prompt.user_prompt,
            "variables": prompt.variables,
            "prompt_pattern": prompt.prompt_pattern,
            "model_id": prompt.model_id,
        }

    built = build_prompt(
        system_prompt=prompt.system_prompt,
        user_prompt=prompt.user_prompt,
        variables={},
        pattern=prompt.prompt_pattern,
        model=prompt.model_id or "gpt-4",
    )

    lines = [
        f"# {prompt.name}",
        "",
        f"**Version:** {prompt.version}  ",
        f"**Pattern:** {prompt.prompt_pattern or 'None'}  ",
        f"**Model:** {prompt.model_id or 'gpt-4'}  ",
        "",
    ]
    if prompt.variables:
        lines.append("**Variables:**  ")
        for v in prompt.variables:
            lines.append(f"- `{{{v['name']}}}` ({v['type']})")
        lines.append("")

    if prompt.system_prompt:
        lines.extend(["## System Prompt", "", prompt.system_prompt, ""])
    if prompt.user_prompt:
        lines.extend(["## User Prompt", "", prompt.user_prompt, ""])

    return PlainTextResponse(
        "\n".join(lines),
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{prompt.name}.md"'},
    )
