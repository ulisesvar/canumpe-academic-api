import time
from collections import deque
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

EXEMPT_PATHS = frozenset({"/health", "/ready"})
WINDOW_SECONDS = 60.0


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory per-client sliding-window rate limit.

    Keyed by client IP rather than API key, so it also protects against
    floods of malformed/invalid keys that never reach authentication.
    In-memory state means limits are per-process -- fine for a single
    instance, but won't be shared across replicas if the app is ever scaled
    horizontally.
    """

    def __init__(self, app, requests_per_minute: int) -> None:
        super().__init__(app)
        self._limit = requests_per_minute
        self._hits: dict[str, deque[float]] = {}

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        client_key = request.client.host if request.client else "unknown"
        now = time.monotonic()
        hits = self._hits.setdefault(client_key, deque())

        cutoff = now - WINDOW_SECONDS
        while hits and hits[0] < cutoff:
            hits.popleft()

        if len(hits) >= self._limit:
            retry_after = max(1, round(WINDOW_SECONDS - (now - hits[0])))
            return JSONResponse(
                status_code=429,
                content={
                    "error": "too_many_requests",
                    "message": "Rate limit exceeded. Try again later.",
                },
                headers={"Retry-After": str(retry_after)},
            )

        hits.append(now)
        return await call_next(request)
