from fastapi import APIRouter

from app.api.routes import me_attendance

router = APIRouter(prefix="/api/v1")
router.include_router(me_attendance.router)
