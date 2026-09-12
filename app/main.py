import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.api.routes import health
from app.api.v1 import router as v1_router
from app.core.config import get_settings
from app.core.logging import RequestLoggingMiddleware, configure_logging
from app.core.rate_limit import RateLimitMiddleware

_STATUS_SLUGS = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    422: "validation_error",
    429: "too_many_requests",
    500: "internal_error",
    503: "service_unavailable",
}

configure_logging(get_settings().log_level)
logger = logging.getLogger("canumpe.app")

app = FastAPI(
    title="CANUMPE Academic API",
    description=(
        "Read-only API that lets an authenticated student retrieve their own "
        "academic information, aggregated from Moodle and the Attendance system."
    ),
    version="0.1.0",
)

app.add_middleware(RateLimitMiddleware, requests_per_minute=get_settings().rate_limit_per_minute)
app.add_middleware(RequestLoggingMiddleware)
app.include_router(health.router)
app.include_router(v1_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict) and "error" in exc.detail and "message" in exc.detail:
        content = exc.detail
    else:
        content = {
            "error": _STATUS_SLUGS.get(exc.status_code, "error"),
            "message": str(exc.detail),
        }
    return JSONResponse(status_code=exc.status_code, content=content, headers=exc.headers)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled exception", extra={"path": request.url.path})
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "message": "An unexpected error occurred"},
    )
