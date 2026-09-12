from datetime import UTC, datetime

from app.schemas.course import CourseOut
from app.semantic.course import Course


def test_from_semantic_preserves_all_fields():
    course = Course(
        course_id=10,
        short_name="MATH101",
        full_name="Mathematics 101",
        start_date=datetime(2026, 8, 1, tzinfo=UTC),
        end_date=datetime(2026, 12, 15, tzinfo=UTC),
        visible=True,
    )

    out = CourseOut.from_semantic(course)

    assert out.course_id == 10
    assert out.short_name == "MATH101"
    assert out.full_name == "Mathematics 101"
    assert out.visible is True


def test_from_semantic_handles_unset_dates():
    course = Course(
        course_id=20,
        short_name="HIST201",
        full_name="History 201",
        start_date=None,
        end_date=None,
        visible=False,
    )

    out = CourseOut.from_semantic(course)

    assert out.start_date is None
    assert out.end_date is None
    assert out.visible is False
