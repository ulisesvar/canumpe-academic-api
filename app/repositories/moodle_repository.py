from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.semantic.course import Course

ACCOUNT_NUMBER_FIELD_SHORTNAME = "cuenta"

_FIND_USER_ID = text(
    """
    SELECT u.id
    FROM mdl_user u
    JOIN mdl_user_info_data uid ON uid.userid = u.id
    JOIN mdl_user_info_field uif ON uif.id = uid.fieldid
    WHERE uif.shortname = :field_shortname
      AND uid.data = :account_number
      AND u.deleted = 0
    """
)

_LIST_ACTIVE_COURSES_FOR_USER = text(
    """
    SELECT
        c.id AS course_id,
        c.shortname AS short_name,
        c.fullname AS full_name,
        c.startdate AS start_date,
        c.enddate AS end_date,
        c.visible AS visible
    FROM mdl_user_enrolments ue
    JOIN mdl_enrol e ON e.id = ue.enrolid
    JOIN mdl_course c ON c.id = e.courseid
    WHERE ue.userid = :user_id
      AND ue.status = 0
      AND e.status = 0
    ORDER BY c.startdate DESC NULLS LAST, c.fullname
    """
)


def _unix_seconds_to_datetime(value: int | None) -> datetime | None:
    """Moodle stores 0 to mean "no date set" on course start/end dates."""
    if not value:
        return None
    return datetime.fromtimestamp(value, tz=UTC)


def get_courses_for_account_number(db: Session, account_number: str) -> list[Course]:
    """Read-only lookup of a single student's actively-enrolled courses.

    Resolves the Moodle user via the "cuenta" custom profile field rather
    than any built-in mdl_user column -- that field is where this Moodle
    instance stores the same account number used across CANUMPE.
    """
    user_row = db.execute(
        _FIND_USER_ID,
        {"field_shortname": ACCOUNT_NUMBER_FIELD_SHORTNAME, "account_number": account_number},
    ).first()
    if user_row is None:
        return []

    rows = db.execute(_LIST_ACTIVE_COURSES_FOR_USER, {"user_id": user_row.id}).all()
    return [
        Course(
            course_id=row.course_id,
            short_name=row.short_name,
            full_name=row.full_name,
            start_date=_unix_seconds_to_datetime(row.start_date),
            end_date=_unix_seconds_to_datetime(row.end_date),
            visible=bool(row.visible),
        )
        for row in rows
    ]
