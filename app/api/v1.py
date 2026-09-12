from fastapi import APIRouter

from app.api.routes import me_attendance, me_courses

router = APIRouter(prefix="/api/v1")
router.include_router(me_attendance.router)
router.include_router(me_courses.router)
