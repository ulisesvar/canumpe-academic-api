from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Course:
    """A course the student is actively enrolled in.

    Source-agnostic: this shape must not change if the underlying Moodle
    schema does.
    """

    course_id: int
    short_name: str
    full_name: str
    start_date: datetime | None
    end_date: datetime | None
    visible: bool
