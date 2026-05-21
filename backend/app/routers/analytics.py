from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.prompt_run import PromptRun

router = APIRouter(tags=["analytics"])


class AnalyticsResponse(BaseModel):
    total_runs: int
    total_tokens_input: int
    total_tokens_output: int
    total_cost: float
    avg_latency_ms: float
    avg_tokens_input: float
    avg_tokens_output: float
    avg_cost: float
    run_count_by_day: list[dict]


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(session: AsyncSession = Depends(get_session)):
    stmt = select(PromptRun)
    result = await session.execute(stmt)
    runs = list(result.scalars().all())

    total_runs = len(runs)
    total_tokens_input = sum(r.tokens_input or 0 for r in runs)
    total_tokens_output = sum(r.tokens_output or 0 for r in runs)
    total_cost = sum(r.cost or 0 for r in runs)
    latencies = [r.latency_ms or 0 for r in runs if r.latency_ms is not None]

    return AnalyticsResponse(
        total_runs=total_runs,
        total_tokens_input=total_tokens_input,
        total_tokens_output=total_tokens_output,
        total_cost=round(total_cost, 6),
        avg_latency_ms=round(sum(latencies) / len(latencies), 1) if latencies else 0,
        avg_tokens_input=round(total_tokens_input / total_runs, 1) if total_runs else 0,
        avg_tokens_output=round(total_tokens_output / total_runs, 1) if total_runs else 0,
        avg_cost=round(total_cost / total_runs, 8) if total_runs else 0,
        run_count_by_day=[],
    )
