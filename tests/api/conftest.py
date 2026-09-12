import os

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient

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
def client():
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def issue_api_key(api_db):
    from app.auth.api_key import generate_api_key, hash_secret
    from app.core.config import get_settings
    from app.models.api_key import ApiKey
    from app.models.student import StudentIdentity

    def _issue(account_number: str = "A0001", revoked: bool = False) -> str:
        student = StudentIdentity(account_number=account_number)
        api_db.add(student)
        api_db.flush()

        plaintext, key_id, secret = generate_api_key()
        pepper = get_settings().api_key_hash_pepper
        api_key = ApiKey(
            key_id=key_id,
            key_hash=hash_secret(secret, pepper),
            student_id=student.id,
        )
        if revoked:
            from datetime import UTC, datetime

            api_key.revoked_at = datetime.now(UTC)
        api_db.add(api_key)
        api_db.commit()
        return plaintext

    return _issue
