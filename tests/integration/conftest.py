import os

import pytest
from alembic.config import Config

from alembic import command
from tests.conftest import db_reachable

API_DB_URL = os.environ["API_DB_URL"]
ATTENDANCE_DB_URL = os.environ["ATTENDANCE_DB_URL"]
MOODLE_DB_URL = os.environ["MOODLE_DB_URL"]


@pytest.fixture(scope="session", autouse=True)
def _test_databases():
    dbs_reachable = (
        db_reachable(API_DB_URL) and db_reachable(ATTENDANCE_DB_URL) and db_reachable(MOODLE_DB_URL)
    )
    if not dbs_reachable:
        pytest.skip(
            "test databases not running - start with: docker compose -f compose.test.yml up -d"
        )
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")
    yield
    command.downgrade(cfg, "base")


@pytest.fixture
def api_db():
    from app.db.api_db import get_sessionmaker
    from app.models import ApiKey, StudentIdentity

    session = get_sessionmaker()()
    try:
        yield session
    finally:
        session.rollback()
        session.query(ApiKey).delete()
        session.query(StudentIdentity).delete()
        session.commit()
        session.close()


@pytest.fixture
def attendance_db():
    from app.db.attendance_db import get_sessionmaker

    session = get_sessionmaker()()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def moodle_db():
    from app.db.moodle_db import get_sessionmaker

    session = get_sessionmaker()()
    try:
        yield session
    finally:
        session.close()
