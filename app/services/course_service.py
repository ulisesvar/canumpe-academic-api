from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.student import StudentIdentity
from app.repositories import moodle_repository
from app.semantic.course import Course


def get_my_courses(moodle_db: Session, student: StudentIdentity) -> list[Course]:
    course_id = get_settings().moodle_course_id
    return moodle_repository.get_courses_for_account_number(
        moodle_db, student.account_number, course_id
    )
