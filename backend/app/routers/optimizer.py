import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.engine.providers.registry import get_provider
from app.services.prompt import prompt_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["optimizer"])

OPTIMIZER_PROMPT = """You are a prompt engineering expert. Analyze the following prompt and suggest specific improvements.

Current system prompt: {system_prompt}
Current user prompt: {user_prompt}
Pattern: {pattern}

Provide your response in this exact format:

## Issues
- List specific issues or weaknesses

## Suggestions
- Specific, actionable improvements

## Optimized Prompt
```
system:
<improved system prompt>

user:
<improved user prompt>
```
"""


class OptimizeRequest(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4o-mini"


class OptimizeResponse(BaseModel):
    issues: str
    suggestions: str
    optimized_prompt: str
    raw_response: str


@router.post("/prompts/{prompt_id}/optimize", response_model=OptimizeResponse)
async def optimize_prompt(
    prompt_id: str,
    body: OptimizeRequest,
    session: AsyncSession = Depends(get_session),
):
    prompt = await prompt_service.get(session, prompt_id)
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")

    provider = get_provider(body.provider)
    if not provider:
        raise HTTPException(status_code=501, detail=f"Provider '{body.provider}' not available")

    meta_prompt = OPTIMIZER_PROMPT.format(
        system_prompt=prompt.system_prompt or "(empty)",
        user_prompt=prompt.user_prompt or "(empty)",
        pattern=prompt.prompt_pattern or "none",
    )

    try:
        result = await provider.execute(
            prompt=meta_prompt,
            model=body.model,
            params={"temperature": 0.3, "max_tokens": 2048},
        )
    except Exception as e:
        logger.exception("Optimizer execution failed")
        raise HTTPException(status_code=502, detail=str(e))

    raw = result.get("model_response", "")

    issues = ""
    suggestions = ""
    optimized = ""

    sections = raw.split("## ")
    for section in sections:
        if section.startswith("Issues"):
            issues = section[len("Issues\n"):].strip()
        elif section.startswith("Suggestions"):
            suggestions = section[len("Suggestions\n"):].strip()
        elif section.startswith("Optimized Prompt"):
            optimized = section[len("Optimized Prompt\n"):].strip()

    return OptimizeResponse(
        issues=issues or "Could not parse issues",
        suggestions=suggestions or "Could not parse suggestions",
        optimized_prompt=optimized or "Could not parse optimized prompt",
        raw_response=raw,
    )
