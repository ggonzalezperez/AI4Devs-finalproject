import pytest

from app.security import create_token, decode_token, hash_secret, verify_secret


def test_hash_and_verify_secret():
    hashed = hash_secret("1234")
    assert hashed != "1234"
    assert verify_secret("1234", hashed) is True
    assert verify_secret("0000", hashed) is False


def test_token_roundtrip():
    token = create_token(subject="42", token_type="family")
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["type"] == "family"


def test_decode_invalid_token_raises():
    import jwt

    with pytest.raises(jwt.InvalidTokenError):
        decode_token("not-a-real-token")
