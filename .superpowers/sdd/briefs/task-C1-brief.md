# Task C1: Cifrado (Fernet) + modelo FamilyAIConfig + migración

Backend `backend/`, venv `./.venv/Scripts/python.exe`. Rama `feature-entrega4-ai-config`. SIN push. TDD.

**Files:**
- Modify: `backend/pyproject.toml` (añadir deps `httpx` y `cryptography`)
- Modify: `backend/app/config.py` (campo `ai_config_key`)
- Create: `backend/app/services/crypto.py`
- Create: `backend/app/models/ai_config.py`
- Modify: `backend/app/models/__init__.py`
- Test: `backend/tests/test_crypto.py`
- Test: `backend/tests/test_ai_config_model.py`
- Migración Alembic (no destructiva).

## Step 1: Añadir dependencias en `backend/pyproject.toml`
En la lista `dependencies` añade (si `httpx` ya está en dev, además déjalo aquí en runtime):
```
    "httpx>=0.27",
    "cryptography>=42",
```
Luego reinstala: desde `backend/`, `./.venv/Scripts/python.exe -m pip install -q -e ".[dev]"`.

## Step 2: Campo en `backend/app/config.py`
Dentro de `Settings`, junto a los demás campos (antes del validador), añade:
```python
    ai_config_key: str | None = None
```

## Step 3: Test `backend/tests/test_crypto.py`
```python
from app.services.crypto import decrypt, encrypt, generate_key


def test_encrypt_decrypt_roundtrip():
    key = generate_key()
    token = encrypt("sk-secret-123", key)
    assert token != "sk-secret-123"
    assert decrypt(token, key) == "sk-secret-123"
```

## Step 4: Crear `backend/app/services/crypto.py`
```python
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
```

## Step 5: Ver pasar el test de crypto
`./.venv/Scripts/python.exe -m pytest tests/test_crypto.py -v` → PASS.

## Step 6: Crear `backend/app/models/ai_config.py`
```python
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class FamilyAIConfig(Base):
    __tablename__ = "family_ai_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"), unique=True, index=True)
    # tier: free | byok | managed
    tier: Mapped[str] = mapped_column(String(20), default="free")
    # provider: stub | ollama | claude | openai | gemini | deepseek | kimi
    provider: Mapped[str] = mapped_column(String(20), default="stub")
    model: Mapped[str | None] = mapped_column(String(80), nullable=True)
    base_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    api_key_encrypted: Mapped[str | None] = mapped_column(String(500), nullable=True)
    monthly_quota: Mapped[int] = mapped_column(Integer, default=0)  # 0 = ilimitado
    used_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
```

## Step 7: Reexportar en `backend/app/models/__init__.py`
Añade al final:
```python
from app.models.ai_config import FamilyAIConfig  # noqa: F401
```

## Step 8: Test `backend/tests/test_ai_config_model.py`
```python
from app.models.ai_config import FamilyAIConfig
from app.models.family import Family


def test_default_config_is_free_stub(db_session):
    fam = Family(name="F")
    db_session.add(fam)
    db_session.flush()
    cfg = FamilyAIConfig(family_id=fam.id)
    db_session.add(cfg)
    db_session.commit()
    assert cfg.tier == "free"
    assert cfg.provider == "stub"
    assert cfg.monthly_quota == 0
    assert cfg.api_key_encrypted is None
```

## Step 9: Tests + migración
- `./.venv/Scripts/python.exe -m pytest tests/test_ai_config_model.py tests/test_crypto.py -v` → PASS.
- Migración:
```bash
./.venv/Scripts/alembic.exe revision --autogenerate -m "ai config: family_ai_config table"
```
Verifica que SOLO contiene `op.create_table("family_ai_config", ...)` (+ índices). Si hay cualquier `drop_table`/`drop_column` sobre tablas existentes, DETENTE y reporta DONE_WITH_CONCERNS sin aplicar. Si limpia:
```bash
./.venv/Scripts/alembic.exe upgrade head
```

## Step 10: Suite completa
`./.venv/Scripts/python.exe -m pytest -q` → todo PASS.

## Step 11: Commit (local, SIN push)
```bash
git add backend/
git commit -m "feat(backend): Fernet crypto + FamilyAIConfig model + migration"
```
