from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

_engine = None
_SessionLocal: sessionmaker[Session] | None = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(get_settings().moodle_db_url, pool_pre_ping=True)
    return _engine


def get_sessionmaker() -> sessionmaker[Session]:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)
    return _SessionLocal


def get_moodle_db() -> Generator[Session, None, None]:
    """Read-only session against the Moodle source database.

    The credentials configured here must belong to a PostgreSQL role with
    SELECT-only privileges; the API must never write to this database.
    """
    session = get_sessionmaker()()
    try:
        yield session
    finally:
        session.close()
