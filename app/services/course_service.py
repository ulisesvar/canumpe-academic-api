from sqlalchemy.orm import Session

from app.models.student import StudentIdentity
from app.repositories import moodle_repository
from app.semantic.course import Course


def get_my_courses(moodle_db: Session, student: StudentIdentity) -> list[Course]:
    return moodle_repository.get_courses_for_account_number(moodle_db, student.account_number)
