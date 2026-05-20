import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.engine.builder import build_prompt
from app.engine.providers.registry import get_provider
from app.models.prompt_run import PromptRun
from app.schemas.execution import PromptExecuteRequest, PromptExecuteResponse
from app.services.prompt import prompt_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["execution"])


@router.post(
    "/sessions/{session_id}/prompts/{prompt_id}/execute",
    response_model=PromptExecuteResponse,
)
async def execute_prompt(
    session_id: str,
    prompt_id: str,
    body: PromptExecuteRequest,
    session: AsyncSession = Depends(get_session),
):
    prompt = await prompt_service.get(session, prompt_id)
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")

    built = build_prompt(
        system_prompt=prompt.system_prompt,
        user_prompt=prompt.user_prompt,
        variables=body.variables,
        pattern=prompt.prompt_pattern,
        model=body.model or prompt.model_id or "gpt-4",
    )

    model_response: str | None = None
    tokens_output: int | None = None
    latency_ms: int | None = None
    finish_reason: str | None = None
    model_raw: dict | None = None

    if not body.dry_run:
        provider = get_provider(body.provider)
        if not provider:
            raise HTTPException(status_code=501, detail="No LLM provider available")
        try:
            result = await provider.execute(
                prompt=built["resolved_prompt"],
                model=body.model or "gpt-4",
                params=body.model_params,
            )
        except Exception as e:
            logger.exception("Provider execution failed")
            raise HTTPException(status_code=502, detail=str(e))
        model_response = result.get("model_response")
        tokens_output = result.get("tokens_output")
        latency_ms = result.get("latency_ms")
        finish_reason = result.get("finish_reason")
        model_raw = result.get("model_raw")

    run = PromptRun(
        resolved_prompt=built["resolved_prompt"],
        model_response=model_response or "",
        model_raw=model_raw,
        tokens_input=built["tokens_input"],
        tokens_output=tokens_output,
        cost=built["cost_estimate"],
        latency_ms=latency_ms,
        prompt_id=prompt_id,
    )
    session.add(run)
    await session.commit()
    await session.refresh(run)

    return PromptExecuteResponse(
        id=run.id,
        resolved_prompt=built["resolved_prompt"],
        model_response=model_response,
        response=model_response,
        tokens_input=built["tokens_input"],
        tokens_output=tokens_output,
        cost_estimate=built["cost_estimate"],
        latency_ms=latency_ms,
        finish_reason=finish_reason,
        detected_variables=built["detected_variables"],
        unsubstituted_variables=built["unsubstituted_variables"],
        prompt_id=prompt_id,
        created_at=run.created_at,
    )
