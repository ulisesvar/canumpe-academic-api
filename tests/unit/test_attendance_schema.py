from datetime import UTC, datetime

from app.schemas.attendance import AttendanceRecordOut
from app.semantic.attendance import AttendanceRecord


def test_from_semantic_preserves_all_fields():
    record = AttendanceRecord(
        session_id=7,
        session_opened_at=datetime(2026, 9, 8, 14, 0, tzinfo=UTC),
        session_closed_at=datetime(2026, 9, 8, 14, 15, tzinfo=UTC),
        session_status="CLOSED",
        attended=True,
        recorded_at=datetime(2026, 9, 8, 14, 3, tzinfo=UTC),
        distance_meters=5.2,
    )

    out = AttendanceRecordOut.from_semantic(record)

    assert out.session_id == 7
    assert out.session_status == "CLOSED"
    assert out.attended is True
    assert out.distance_meters == 5.2


def test_from_semantic_handles_missed_session_with_null_fields():
    record = AttendanceRecord(
        session_id=8,
        session_opened_at=datetime(2026, 9, 8, 14, 0, tzinfo=UTC),
        session_closed_at=None,
        session_status="OPEN",
        attended=False,
        recorded_at=None,
        distance_meters=None,
    )

    out = AttendanceRecordOut.from_semantic(record)

    assert out.attended is False
    assert out.recorded_at is None
    assert out.distance_meters is None
    assert out.session_closed_at is None
