from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.api_key import ApiKey


def get_by_key_id(db: Session, key_id: str) -> ApiKey | None:
    return db.execute(select(ApiKey).where(ApiKey.key_id == key_id)).scalar_one_or_none()


def touch_last_used(db: Session, api_key: ApiKey) -> None:
    api_key.last_used_at = datetime.now(UTC)
    db.add(api_key)
    db.commit()
