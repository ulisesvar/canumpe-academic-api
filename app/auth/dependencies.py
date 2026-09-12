from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.api.errors import unauthorized
from app.auth.api_key import MalformedApiKeyError, parse_api_key, verify_secret
from app.core.config import Settings, get_settings
from app.db.api_db import get_api_db
from app.models.student import StudentIdentity
from app.repositories import api_key_repository


def get_current_student(
    request: Request,
    db: Session = Depends(get_api_db),
    settings: Settings = Depends(get_settings),
) -> StudentIdentity:
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise unauthorized()

    raw_key = auth_header.removeprefix("Bearer ").strip()
    if not raw_key:
        raise unauthorized()

    try:
        key_id, secret = parse_api_key(raw_key)
    except MalformedApiKeyError:
        raise unauthorized() from None

    api_key = api_key_repository.get_by_key_id(db, key_id)
    if api_key is None or api_key.is_revoked:
        raise unauthorized()

    if not verify_secret(secret, settings.api_key_hash_pepper, api_key.key_hash):
        raise unauthorized()

    api_key_repository.touch_last_used(db, api_key)

    request.state.api_key_id = api_key.key_id
    request.state.student_id = api_key.student_id

    return api_key.student
