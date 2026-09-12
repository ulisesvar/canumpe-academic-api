from app.repositories import moodle_repository


def test_returns_active_courses_ordered_newest_start_date_first(moodle_db):
    courses = moodle_repository.get_courses_for_account_number(moodle_db, "A0001")

    assert [c.course_id for c in courses] == [10, 40]
    math101, chem101 = courses

    assert math101.short_name == "MATH101"
    assert math101.full_name == "Mathematics 101"
    assert math101.visible is True
    assert math101.end_date is None  # enddate = 0 in the fixture

    assert chem101.short_name == "CHEM101"


def test_excludes_suspended_enrolment_and_disabled_enrol_instance(moodle_db):
    """Alice is also linked to History201 (suspended enrolment) and
    Physics301 (enrolment method disabled) in the fixture -- neither
    should surface, only Math101 and Chemistry101."""
    courses = moodle_repository.get_courses_for_account_number(moodle_db, "A0001")

    course_ids = {c.course_id for c in courses}
    assert 20 not in course_ids
    assert 30 not in course_ids


def test_hidden_course_is_still_returned_with_visible_false(moodle_db):
    courses = moodle_repository.get_courses_for_account_number(moodle_db, "A0002")

    assert len(courses) == 1
    assert courses[0].course_id == 20
    assert courses[0].visible is False


def test_deleted_moodle_account_does_not_resolve(moodle_db):
    courses = moodle_repository.get_courses_for_account_number(moodle_db, "A0003")

    assert courses == []


def test_unknown_account_number_returns_empty_list(moodle_db):
    courses = moodle_repository.get_courses_for_account_number(moodle_db, "NOT-A-REAL-ACCOUNT")

    assert courses == []
