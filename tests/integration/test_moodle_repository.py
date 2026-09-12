import pytest

from app.repositories import moodle_repository
from app.repositories.moodle_repository import DuplicateAccountNumberError

# Matches tests/fixtures/moodle_seed.sql and the MOODLE_COURSE_ID test env var.
IN_SCOPE_COURSE_ID = 10


def test_returns_the_students_active_enrolment_in_the_configured_course(moodle_db):
    courses = moodle_repository.get_courses_for_account_number(
        moodle_db, "A0001", IN_SCOPE_COURSE_ID
    )

    assert len(courses) == 1
    course = courses[0]
    assert course.course_id == IN_SCOPE_COURSE_ID
    assert course.short_name == "MATH101"
    assert course.full_name == "Mathematics 101"
    assert course.visible is True
    assert course.end_date is None  # enddate = 0 in the fixture


def test_active_enrolment_outside_configured_scope_is_not_returned(moodle_db):
    """Bob is actively enrolled in History201 (course 20), but CANUMPE's
    scope is course 10 -- an active enrolment elsewhere must never leak
    through."""
    courses = moodle_repository.get_courses_for_account_number(
        moodle_db, "A0002", IN_SCOPE_COURSE_ID
    )

    assert courses == []


def test_disabled_enrolment_method_is_excluded_even_within_scope(moodle_db):
    courses = moodle_repository.get_courses_for_account_number(
        moodle_db, "A0004", IN_SCOPE_COURSE_ID
    )

    assert courses == []


def test_suspended_own_enrolment_is_excluded_even_within_scope(moodle_db):
    courses = moodle_repository.get_courses_for_account_number(
        moodle_db, "A0005", IN_SCOPE_COURSE_ID
    )

    assert courses == []


def test_deleted_moodle_account_does_not_resolve(moodle_db):
    courses = moodle_repository.get_courses_for_account_number(
        moodle_db, "A0003", IN_SCOPE_COURSE_ID
    )

    assert courses == []


def test_unknown_account_number_returns_empty_list(moodle_db):
    courses = moodle_repository.get_courses_for_account_number(
        moodle_db, "NOT-A-REAL-ACCOUNT", IN_SCOPE_COURSE_ID
    )

    assert courses == []


def test_duplicate_account_number_raises_instead_of_picking_one_student(moodle_db):
    """Two non-deleted Moodle users (ids 6 and 7) share account number
    A0009 in the fixture. Even though one of them (id 6) has a real active
    enrolment in the configured course, the lookup must refuse to guess
    which student that data belongs to."""
    with pytest.raises(DuplicateAccountNumberError):
        moodle_repository.get_courses_for_account_number(moodle_db, "A0009", IN_SCOPE_COURSE_ID)
