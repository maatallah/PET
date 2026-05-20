from fastapi import APIRouter, Query

from app.debug.logger import DebugLog

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/logs", response_model=list[dict])
async def get_logs(limit: int = Query(default=200, le=5000)):
    """Fetch recent log entries (most recent last)."""
    entries = DebugLog.get_all()
    result = []
    for e in entries[-limit:]:
        result.append(
            {
                "seq": e.seq,
                "timestamp": e.timestamp,
                "method": e.method,
                "path": e.path,
                "status": e.status,
                "duration_ms": e.duration_ms,
                "error": e.error,
            }
        )
    return result


@router.delete("/logs")
async def clear_logs():
    """Clear the in-memory log buffer."""
    DebugLog.clear()
    return {"cleared": True}
