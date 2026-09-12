from app.auth.api_key import generate_api_key, hash_secret
from app.models.api_key import ApiKey
from app.models.student import StudentIdentity
from app.repositories import api_key_repository


def _make_key(api_db, account_number: str = "A0001") -> tuple[str, ApiKey]:
    student = StudentIdentity(account_number=account_number)
    api_db.add(student)
    api_db.flush()

    plaintext, key_id, secret = generate_api_key()
    api_key = ApiKey(
        key_id=key_id, key_hash=hash_secret(secret, "test-pepper"), student_id=student.id
    )
    api_db.add(api_key)
    api_db.commit()
    return plaintext, api_key


def test_get_by_key_id_finds_existing_key(api_db):
    _, created = _make_key(api_db)

    found = api_key_repository.get_by_key_id(api_db, created.key_id)

    assert found is not None
    assert found.id == created.id
    assert found.is_revoked is False


def test_get_by_key_id_returns_none_for_unknown_id(api_db):
    assert api_key_repository.get_by_key_id(api_db, "does-not-exist") is None


def test_touch_last_used_sets_timestamp(api_db):
    _, created = _make_key(api_db)
    assert created.last_used_at is None

    api_key_repository.touch_last_used(api_db, created)

    refreshed = api_key_repository.get_by_key_id(api_db, created.key_id)
    assert refreshed.last_used_at is not None
