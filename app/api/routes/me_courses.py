from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_student
from app.db.moodle_db import get_moodle_db
from app.models.student import StudentIdentity
from app.schemas.course import CourseOut
from app.schemas.errors import ErrorResponse
from app.services import course_service

router = APIRouter(tags=["me"])


@router.get(
    "/me/courses",
    summary="List the authenticated student's actively enrolled courses",
    response_model=list[CourseOut],
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Missing, malformed, invalid, or revoked API key",
        },
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    },
)
def get_my_courses(
    student: StudentIdentity = Depends(get_current_student),
    moodle_db: Session = Depends(get_moodle_db),
) -> list[CourseOut]:
    """Return every course the authenticated student is actively enrolled in.

    The student is derived entirely from the API key -- no account number
    or student id may be supplied by the client.
    """
    courses = course_service.get_my_courses(moodle_db, student)
    return [CourseOut.from_semantic(course) for course in courses]
