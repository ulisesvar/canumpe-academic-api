import hashlib
import hmac
import secrets

KEY_PREFIX = "cnp"
KEY_ID_BYTES = 8
SECRET_BYTES = 32


class MalformedApiKeyError(ValueError):
    pass


def generate_api_key() -> tuple[str, str, str]:
    """Generate a new API key.

    Returns (plaintext_key, key_id, secret). Only `plaintext_key` should ever
    be shown to the student; the caller must hash `secret` before persisting
    anything.
    """
    key_id = secrets.token_hex(KEY_ID_BYTES)
    secret = secrets.token_urlsafe(SECRET_BYTES)
    plaintext = f"{KEY_PREFIX}_{key_id}_{secret}"
    return plaintext, key_id, secret


def parse_api_key(raw: str) -> tuple[str, str]:
    """Split a presented API key into (key_id, secret).

    Raises MalformedApiKeyError if the key does not match the expected shape.
    """
    parts = raw.split("_", 2)
    if len(parts) != 3 or parts[0] != KEY_PREFIX or not parts[1] or not parts[2]:
        raise MalformedApiKeyError("API key does not match the expected format")
    _, key_id, secret = parts
    if len(key_id) != KEY_ID_BYTES * 2:
        raise MalformedApiKeyError("API key id segment has an invalid length")
    return key_id, secret


def hash_secret(secret: str, pepper: str) -> str:
    return hashlib.sha256(f"{pepper}{secret}".encode()).hexdigest()


def verify_secret(secret: str, pepper: str, expected_hash: str) -> bool:
    return hmac.compare_digest(hash_secret(secret, pepper), expected_hash)
