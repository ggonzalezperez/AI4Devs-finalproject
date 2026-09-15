from cryptography.fernet import Fernet

from app.config import get_settings


def generate_key() -> str:
    return Fernet.generate_key().decode()


def _resolve_key(key: str | None) -> bytes:
    k = key or get_settings().ai_config_key
    if not k:
        raise RuntimeError("AI_CONFIG_KEY no configurada")
    return k.encode() if isinstance(k, str) else k


def encrypt(plaintext: str, key: str | None = None) -> str:
    return Fernet(_resolve_key(key)).encrypt(plaintext.encode()).decode()


def decrypt(token: str, key: str | None = None) -> str:
    return Fernet(_resolve_key(key)).decrypt(token.encode()).decode()
