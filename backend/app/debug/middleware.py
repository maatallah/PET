import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.debug.logger import DebugLog


class DebugMiddleware(BaseHTTPMiddleware):
    """Records every request/response into the circular log buffer."""

    async def dispatch(self, request: Request, call_next):
        start = time.monotonic()
        response: Response = await call_next(request)
        elapsed_ms = (time.monotonic() - start) * 1000

        path = request.url.path[:80]
        query = request.url.query
        full_path = f"{path}?{query}" if query else path

        DebugLog.add(
            method=request.method,
            path=full_path,
            status=response.status_code,
            duration_ms=elapsed_ms,
        )

        response.headers["X-Debug-Duration"] = f"{elapsed_ms:.1f}ms"
        response.headers["X-Debug-Seq"] = str(DebugLog._seq)
        return response
