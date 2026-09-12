from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AttendanceRecord:
    """A single class session and whether the student attended it.

    This is the API's stable, source-agnostic representation of attendance --
    it must not change shape when the underlying Attendance database schema does.
    """

    session_id: int
    session_opened_at: datetime
    session_closed_at: datetime | None
    session_status: str
    attended: bool
    recorded_at: datetime | None
    distance_meters: float | None
