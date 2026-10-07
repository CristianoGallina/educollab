from app.security import encrypt_secret, decrypt_secret


def test_encrypt_and_decrypt_round_trip():
    original = "sk-test-123456"
    encrypted = encrypt_secret(original)

    assert encrypted != original
    assert decrypt_secret(encrypted) == original
    assert decrypt_secret(None) is None
