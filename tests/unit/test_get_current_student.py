from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.auth import dependencies
from app.auth.api_key import generate_api_key, hash_secret
from app.core.config import Settings
from app.models.api_key import ApiKey
from app.models.student import StudentIdentity

PEPPER = "unit-test-pepper"


def _settings() -> Settings:
    return Settings(
        api_db_url="sqlite://",
        attendance_db_url="sqlite://",
        moodle_db_url="sqlite://",
        moodle_course_id=10,
        api_key_hash_pepper=PEPPER,
    )


def _request(auth_header: str | None) -> MagicMock:
    request = MagicMock()
    request.headers = {"authorization": auth_header} if auth_header else {}
    request.state = SimpleNamespace()
    return request


def _issue_key(*, revoked: bool = False) -> tuple[str, ApiKey]:
    plaintext, key_id, secret = generate_api_key()
    student = StudentIdentity(id=1, account_number="A0001")
    api_key = ApiKey(
        id=1,
        key_id=key_id,
        key_hash=hash_secret(secret, PEPPER),
        student_id=1,
        revoked_at=datetime.now(UTC) if revoked else None,
    )
    api_key.student = student
    return plaintext, api_key


def test_missing_authorization_header_is_401():
    with pytest.raises(HTTPException) as exc:
        dependencies.get_current_student(_request(None), db=MagicMock(), settings=_settings())
    assert exc.value.status_code == 401


def test_non_bearer_scheme_is_401():
    with pytest.raises(HTTPException) as exc:
        dependencies.get_current_student(
            _request("Basic dXNlcjpwYXNz"), db=MagicMock(), settings=_settings()
        )
    assert exc.value.status_code == 401


def test_malformed_key_is_401():
    with pytest.raises(HTTPException) as exc:
        dependencies.get_current_student(
            _request("Bearer garbage"), db=MagicMock(), settings=_settings()
        )
    assert exc.value.status_code == 401


def test_unknown_key_id_is_401(monkeypatch):
    plaintext, _ = _issue_key()
    monkeypatch.setattr(dependencies.api_key_repository, "get_by_key_id", lambda db, kid: None)

    with pytest.raises(HTTPException) as exc:
        dependencies.get_current_student(
            _request(f"Bearer {plaintext}"), db=MagicMock(), settings=_settings()
        )
    assert exc.value.status_code == 401


def test_revoked_key_is_401(monkeypatch):
    plaintext, api_key = _issue_key(revoked=True)
    monkeypatch.setattr(dependencies.api_key_repository, "get_by_key_id", lambda db, kid: api_key)

    with pytest.raises(HTTPException) as exc:
        dependencies.get_current_student(
            _request(f"Bearer {plaintext}"), db=MagicMock(), settings=_settings()
        )
    assert exc.value.status_code == 401


def test_secret_mismatch_is_401(monkeypatch):
    plaintext, api_key = _issue_key()
    api_key.key_hash = hash_secret("a-completely-different-secret", PEPPER)
    monkeypatch.setattr(dependencies.api_key_repository, "get_by_key_id", lambda db, kid: api_key)

    with pytest.raises(HTTPException) as exc:
        dependencies.get_current_student(
            _request(f"Bearer {plaintext}"), db=MagicMock(), settings=_settings()
        )
    assert exc.value.status_code == 401


def test_valid_key_returns_owning_student_and_records_usage(monkeypatch):
    plaintext, api_key = _issue_key()
    monkeypatch.setattr(dependencies.api_key_repository, "get_by_key_id", lambda db, kid: api_key)
    touched = []
    monkeypatch.setattr(
        dependencies.api_key_repository, "touch_last_used", lambda db, k: touched.append(k)
    )

    request = _request(f"Bearer {plaintext}")
    student = dependencies.get_current_student(request, db=MagicMock(), settings=_settings())

    assert student is api_key.student
    assert touched == [api_key]
    assert request.state.student_id == api_key.student_id
    assert request.state.api_key_id == api_key.key_id


def test_a_second_students_key_can_never_resolve_to_the_first_student(monkeypatch):
    """Guards the core authorization invariant: whichever key is presented,
    only its own owning student is ever returned."""
    plaintext_a, key_a = _issue_key()
    key_a.student = StudentIdentity(id=1, account_number="A0001")

    plaintext_b, key_b = _issue_key()
    key_b.id = 2
    key_b.student_id = 2
    key_b.student = StudentIdentity(id=2, account_number="A0002")

    lookup = {key_a.key_id: key_a, key_b.key_id: key_b}
    monkeypatch.setattr(
        dependencies.api_key_repository, "get_by_key_id", lambda db, kid: lookup[kid]
    )
    monkeypatch.setattr(dependencies.api_key_repository, "touch_last_used", lambda db, k: None)

    student_a = dependencies.get_current_student(
        _request(f"Bearer {plaintext_a}"), db=MagicMock(), settings=_settings()
    )
    student_b = dependencies.get_current_student(
        _request(f"Bearer {plaintext_b}"), db=MagicMock(), settings=_settings()
    )

    assert student_a.account_number == "A0001"
    assert student_b.account_number == "A0002"
    assert student_a.account_number != student_b.account_number
