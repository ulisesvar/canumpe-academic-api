from app.repositories import attendance_repository


def test_returns_sessions_newest_first_with_attendance_flag(attendance_db):
    records = attendance_repository.get_attendance_history(attendance_db, "A0001")

    assert [r.session_status for r in records] == ["OPEN", "CLOSED", "CLOSED"]
    opened, missed, attended = records[0], records[1], records[2]

    assert opened.attended is False
    assert opened.recorded_at is None

    assert missed.attended is False
    assert missed.distance_meters is None

    assert attended.attended is True
    assert attended.distance_meters == 5.2
    assert attended.recorded_at is not None


def test_student_with_no_attendance_returns_empty_records_not_missing_sessions(attendance_db):
    records = attendance_repository.get_attendance_history(attendance_db, "A0002")

    assert len(records) == 3
    assert all(r.attended is False for r in records)


def test_unknown_account_number_returns_empty_list(attendance_db):
    records = attendance_repository.get_attendance_history(attendance_db, "NOT-A-REAL-ACCOUNT")

    assert records == []
