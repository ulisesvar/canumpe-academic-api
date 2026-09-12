import pytest

from app.auth.api_key import (
    MalformedApiKeyError,
    generate_api_key,
    hash_secret,
    parse_api_key,
    verify_secret,
)


def test_generate_api_key_round_trips_through_parse():
    plaintext, key_id, secret = generate_api_key()

    parsed_key_id, parsed_secret = parse_api_key(plaintext)

    assert parsed_key_id == key_id
    assert parsed_secret == secret


def test_generated_keys_are_unique():
    first, _, _ = generate_api_key()
    second, _, _ = generate_api_key()

    assert first != second


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "not-a-key-at-all",
        "cnp_onlyoneseparator",
        "wrongprefix_deadbeefdeadbeef_somesecret",
        "cnp__somesecret",
        "cnp_deadbeefdeadbeef_",
        "cnp_short_somesecret",
    ],
)
def test_parse_api_key_rejects_malformed_input(raw):
    with pytest.raises(MalformedApiKeyError):
        parse_api_key(raw)


def test_verify_secret_accepts_matching_secret():
    assert verify_secret("s3cret", "pepper", hash_secret("s3cret", "pepper"))


def test_verify_secret_rejects_wrong_secret():
    assert not verify_secret("s3cret", "pepper", hash_secret("other", "pepper"))


def test_verify_secret_rejects_wrong_pepper():
    assert not verify_secret("s3cret", "pepper", hash_secret("s3cret", "different-pepper"))


def test_hash_secret_is_deterministic():
    assert hash_secret("s3cret", "pepper") == hash_secret("s3cret", "pepper")
