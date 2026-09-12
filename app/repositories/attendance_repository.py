from sqlalchemy import text
from sqlalchemy.orm import Session

from app.semantic.attendance import AttendanceRecord

_FIND_STUDENT_ID = text(
    "SELECT id FROM students WHERE account_number = :account_number"
)

_LIST_SESSIONS_FOR_STUDENT = text(
    """
    SELECT
        s.id AS session_id,
        s.opened_at AS session_opened_at,
        s.closed_at AS session_closed_at,
        s.status AS session_status,
        a.created_at AS recorded_at,
        a.distance_meters AS distance_meters
    FROM attendance_sessions s
    LEFT JOIN attendances a
        ON a.session_id = s.id AND a.student_id = :student_id
    ORDER BY s.opened_at DESC
    """
)


def get_attendance_history(db: Session, account_number: str) -> list[AttendanceRecord]:
    """Read-only lookup of a single student's attendance history.

    Looks the student up by account_number within the Attendance source
    database itself -- the caller is never allowed to pass an internal id
    that didn't originate from the authenticated identity.
    """
    student_row = db.execute(_FIND_STUDENT_ID, {"account_number": account_number}).first()
    if student_row is None:
        return []

    rows = db.execute(_LIST_SESSIONS_FOR_STUDENT, {"student_id": student_row.id}).all()
    return [
        AttendanceRecord(
            session_id=row.session_id,
            session_opened_at=row.session_opened_at,
            session_closed_at=row.session_closed_at,
            session_status=row.session_status,
            attended=row.recorded_at is not None,
            recorded_at=row.recorded_at,
            distance_meters=row.distance_meters,
        )
        for row in rows
    ]
