from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.api_db import Base

if TYPE_CHECKING:
    from app.models.api_key import ApiKey


class StudentIdentity(Base):
    """Maps an internal student identity to the account numbers used by source systems.

    This table never stores academic data itself -- only the identity mapping
    needed to know which Moodle / Attendance records belong to this student.
    """

    __tablename__ = "student_identities"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_number: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    role: Mapped[str] = mapped_column(String(16), default="student", server_default="student")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    api_keys: Mapped[list["ApiKey"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
