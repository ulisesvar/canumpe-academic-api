from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.api_db import Base
from app.models.student import StudentIdentity


class ApiKey(Base):
    """API key metadata. The plaintext key is never stored -- only its hash.

    `key_id` is the public, indexed lookup identifier embedded in the issued
    token (e.g. "cnp_<key_id>_<secret>"); `key_hash` is a SHA-256 digest of
    the secret portion (plus a server-side pepper) and is what gets compared
    on each request.
    """

    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(primary_key=True)
    key_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    key_hash: Mapped[str] = mapped_column(String(128))
    student_id: Mapped[int] = mapped_column(ForeignKey("student_identities.id"), index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    student: Mapped[StudentIdentity] = relationship(back_populates="api_keys")

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None
