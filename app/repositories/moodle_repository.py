import logging
from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.semantic.course import Course

logger = logging.getLogger("canumpe.moodle")

ACCOUNT_NUMBER_FIELD_SHORTNAME = "cuenta"

_FIND_USER_IDS = text(
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
      AND c.id = :course_id
    ORDER BY c.startdate DESC NULLS LAST, c.fullname
    """
)


class DuplicateAccountNumberError(RuntimeError):
    """More than one non-deleted Moodle user shares the same account-number
    custom profile field value.

    This is a Moodle data-integrity problem, not a normal "student not
    found" case -- the account number is used as an identity boundary, so
    silently picking one of the matching users could leak one student's
    courses to another. Callers must let this propagate as a failure.
    """


def _unix_seconds_to_datetime(value: int | None) -> datetime | None:
    """Moodle stores 0 to mean "no date set" on course start/end dates."""
    if not value:
        return None
    return datetime.fromtimestamp(value, tz=UTC)


def _find_user_id(db: Session, account_number: str) -> int | None:
    rows = db.execute(
        _FIND_USER_IDS,
        {"field_shortname": ACCOUNT_NUMBER_FIELD_SHORTNAME, "account_number": account_number},
    ).all()

    if not rows:
        return None

    if len(rows) > 1:
        logger.critical(
            "duplicate Moodle account number detected -- refusing to resolve identity",
            extra={"account_number": account_number, "match_count": len(rows)},
        )
        raise DuplicateAccountNumberError(
            f"{len(rows)} non-deleted Moodle users share account number {account_number!r}"
        )

    return rows[0].id


def get_courses_for_account_number(
    db: Session, account_number: str, course_id: int
) -> list[Course]:
    """Read-only lookup of a single student's active enrolment in the
    configured CANUMPE course.

    Resolves the Moodle user via the "cuenta" custom profile field rather
    than any built-in mdl_user column -- that field is where this Moodle
    instance stores the same account number used across CANUMPE.
    """
    user_id = _find_user_id(db, account_number)
    if user_id is None:
        return []

    rows = db.execute(
        _LIST_ACTIVE_COURSES_FOR_USER, {"user_id": user_id, "course_id": course_id}
    ).all()
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
