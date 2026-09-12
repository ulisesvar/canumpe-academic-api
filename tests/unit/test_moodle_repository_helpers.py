from datetime import UTC, datetime

from app.repositories.moodle_repository import _unix_seconds_to_datetime


def test_zero_means_unset_per_moodle_convention():
    assert _unix_seconds_to_datetime(0) is None


def test_none_is_passed_through_as_none():
    assert _unix_seconds_to_datetime(None) is None


def test_nonzero_value_converts_to_utc_datetime():
    result = _unix_seconds_to_datetime(1767225600)

    assert result == datetime(2026, 1, 1, tzinfo=UTC)
