from app.services.crypto import decrypt, encrypt, generate_key


def test_encrypt_decrypt_roundtrip():
    key = generate_key()
    token = encrypt("sk-secret-123", key)
    assert token != "sk-secret-123"
    assert decrypt(token, key) == "sk-secret-123"
