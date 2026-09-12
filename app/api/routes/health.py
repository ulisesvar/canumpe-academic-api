from fastapi import APIRouter, Response
from sqlalchemy import text

from app.db.api_db import get_engine as get_api_engine
from app.db.attendance_db import get_engine as get_attendance_engine

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness check")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready", summary="Readiness check")
def ready(response: Response) -> dict[str, str]:
    checks = {}
    for name, get_engine in (("api_db", get_api_engine), ("attendance_db", get_attendance_engine)):
        try:
            with get_engine().connect() as conn:
                conn.execute(text("SELECT 1"))
            checks[name] = "ok"
        except Exception:
            checks[name] = "unavailable"

    if any(status != "ok" for status in checks.values()):
        response.status_code = 503
    return {"status": "ok" if response.status_code != 503 else "unavailable", **checks}
