from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.engine.scanner import scan_prompt
from app.services.prompt import prompt_service

router = APIRouter(tags=["scanner"])


class ScanResult(BaseModel):
    findings: list[dict]
    safe: bool
    total_issues: int


@router.post("/prompts/{prompt_id}/scan", response_model=ScanResult)
async def scan_prompt_endpoint(
    prompt_id: str,
    session: AsyncSession = Depends(get_session),
):
    prompt = await prompt_service.get(session, prompt_id)
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")

    text = f"{prompt.system_prompt or ''}\n{prompt.user_prompt or ''}"
    findings = scan_prompt(text)

    return ScanResult(
        findings=findings,
        safe=len(findings) == 0,
        total_issues=len(findings),
    )
