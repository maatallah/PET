from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.file import File

router = APIRouter(tags=["rag"])


class ChunkResult(BaseModel):
    file_id: str
    file_name: str
    snippet: str
    score: float


class RagSearchResponse(BaseModel):
    results: list[ChunkResult]


@router.get("/rag/search", response_model=RagSearchResponse)
async def rag_search(
    q: str = "",
    session_id: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    if not q.strip():
        return RagSearchResponse(results=[])

    keyword = q.lower()
    stmt = select(File).where(File.content_text.isnot(None))
    if session_id:
        stmt = stmt.where(File.session_id == session_id)

    result = await session.execute(stmt)
    files = list(result.scalars().all())

    results: list[ChunkResult] = []
    for f in files:
        text = f.content_text or ""
        if keyword in text.lower():
            idx = text.lower().index(keyword)
            start = max(0, idx - 100)
            end = min(len(text), idx + len(keyword) + 100)
            snippet = text[start:end]
            results.append(ChunkResult(
                file_id=f.id,
                file_name=f.original_name,
                snippet=snippet,
                score=1.0,
            ))

    return RagSearchResponse(results=results[:20])
