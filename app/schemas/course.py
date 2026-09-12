from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.semantic.course import Course


class CourseOut(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "course_id": 10,
                "short_name": "MATH101",
                "full_name": "Mathematics 101",
                "start_date": "2026-08-01T00:00:00Z",
                "end_date": "2026-12-15T00:00:00Z",
                "visible": True,
            }
        }
    )

    course_id: int = Field(..., description="Identifier of the course.")
    short_name: str = Field(..., description="Short/code name of the course.")
    full_name: str = Field(..., description="Full display name of the course.")
    start_date: datetime | None = Field(None, description="When the course starts, if set.")
    end_date: datetime | None = Field(None, description="When the course ends, if set.")
    visible: bool = Field(..., description="Whether the course is currently visible to students.")

    @classmethod
    def from_semantic(cls, course: Course) -> "CourseOut":
        return cls(
            course_id=course.course_id,
            short_name=course.short_name,
            full_name=course.full_name,
            start_date=course.start_date,
            end_date=course.end_date,
            visible=course.visible,
        )
