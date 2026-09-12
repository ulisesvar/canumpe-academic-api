from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.semantic.attendance import AttendanceRecord


class AttendanceRecordOut(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": 42,
                "session_opened_at": "2026-09-08T14:00:00Z",
                "session_closed_at": "2026-09-08T14:15:00Z",
                "session_status": "CLOSED",
                "attended": True,
                "recorded_at": "2026-09-08T14:03:12Z",
                "distance_meters": 8.4,
            }
        }
    )

    session_id: int = Field(
        ..., description="Identifier of the attendance session/class meeting."
    )
    session_opened_at: datetime = Field(..., description="When the session was opened.")
    session_closed_at: datetime | None = Field(
        None, description="When the session was closed, if it has been."
    )
    session_status: str = Field(
        ..., description="Current status of the session, e.g. OPEN or CLOSED."
    )
    attended: bool = Field(
        ..., description="Whether the student has a recorded attendance for this session."
    )
    recorded_at: datetime | None = Field(
        None, description="When the student's attendance was recorded, if attended is true."
    )
    distance_meters: float | None = Field(
        None, description="Distance from the session location at check-in time, in meters."
    )

    @classmethod
    def from_semantic(cls, record: AttendanceRecord) -> "AttendanceRecordOut":
        return cls(
            session_id=record.session_id,
            session_opened_at=record.session_opened_at,
            session_closed_at=record.session_closed_at,
            session_status=record.session_status,
            attended=record.attended,
            recorded_at=record.recorded_at,
            distance_meters=record.distance_meters,
        )
