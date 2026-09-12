from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_student
from app.db.attendance_db import get_attendance_db
from app.models.student import StudentIdentity
from app.schemas.attendance import AttendanceRecordOut
from app.schemas.errors import ErrorResponse
from app.services import attendance_service

router = APIRouter(tags=["me"])


@router.get(
    "/me/attendance",
    summary="List the authenticated student's attendance history",
    response_model=list[AttendanceRecordOut],
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Missing, malformed, invalid, or revoked API key",
        },
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    },
)
def get_my_attendance(
    student: StudentIdentity = Depends(get_current_student),
    attendance_db: Session = Depends(get_attendance_db),
) -> list[AttendanceRecordOut]:
    """Return every attendance session for the authenticated student.

    The student is derived entirely from the API key -- no account number
    or student id may be supplied by the client.
    """
    records = attendance_service.get_my_attendance(attendance_db, student)
    return [AttendanceRecordOut.from_semantic(record) for record in records]
