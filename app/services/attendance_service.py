from sqlalchemy.orm import Session

from app.models.student import StudentIdentity
from app.repositories import attendance_repository
from app.semantic.attendance import AttendanceRecord


def get_my_attendance(attendance_db: Session, student: StudentIdentity) -> list[AttendanceRecord]:
    return attendance_repository.get_attendance_history(attendance_db, student.account_number)
