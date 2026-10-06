import base64
import os

from cryptography.fernet import Fernet


def _build_key() -> bytes:
    configured = os.getenv("APP_SECRET_KEY") or os.getenv("FERNET_KEY")
    if configured:
        normalized = configured.strip()
        if len(normalized) >= 32:
            return base64.urlsafe_b64encode(normalized.encode()[:32])
        return base64.urlsafe_b64encode((normalized + "=" * 32)[:32].encode())

    fallback = "educollab-local-dev-secret-key-32b"
    return base64.urlsafe_b64encode(fallback.encode()[:32])


_FERNET = Fernet(_build_key())


def encrypt_secret(value: str | None) -> str | None:
    if value is None or not str(value).strip():
        return None
    return _FERNET.encrypt(str(value).strip().encode()).decode()


def decrypt_secret(value: str | None) -> str | None:
    if value is None or not str(value).strip():
        return None
    return _FERNET.decrypt(str(value).strip().encode()).decode()
