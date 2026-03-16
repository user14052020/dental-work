import pytest

from app.core.exceptions import AuthenticationError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_password,
    hash_token,
    verify_password,
    verify_token_hash,
)


def test_password_hash_and_verify_roundtrip():
    password = "admin123"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_access_token_roundtrip_contains_expected_claims():
    token = create_access_token("user-123", expires_minutes=5)

    payload = decode_access_token(token)

    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"


def test_refresh_token_roundtrip_contains_expected_claims():
    token = create_refresh_token("user-456", expires_days=2)

    payload = decode_refresh_token(token)

    assert payload["sub"] == "user-456"
    assert payload["type"] == "refresh"
    assert payload["jti"]


def test_access_decoder_rejects_refresh_token():
    token = create_refresh_token("user-789")

    with pytest.raises(AuthenticationError):
        decode_access_token(token)


def test_token_hash_verification():
    token = create_refresh_token("user-hash")

    token_hash = hash_token(token)

    assert verify_token_hash(token, token_hash) is True
    assert verify_token_hash("invalid-token", token_hash) is False
