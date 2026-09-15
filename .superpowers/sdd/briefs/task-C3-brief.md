# Task C3: Endpoints GET/PUT de la config de IA por familia (clave cifrada)

Backend `backend/`, venv `./.venv/Scripts/python.exe`. Rama `feature-entrega4-ai-config`. SIN push. TDD.

**Files:**
- Create: `backend/app/repositories/ai_config.py`
- Modify: `backend/app/schemas/ai_config.py` (añadir AIConfigRead, AIConfigUpdate)
- Modify: `backend/app/routers/ai_config.py` (GET/PUT)
- Test: `backend/tests/test_ai_config_crud.py`

**Reglas:**
- Una config por familia (get_or_create). Defecto: `free` / `stub`.
- La clave API se guarda **cifrada** (con `crypto.encrypt(api_key, get_settings().ai_config_key)`). **NUNCA** se devuelve; el read expone solo `has_api_key: bool`.
- Validar: `tier ∈ {free,byok,managed}`; `provider` debe existir en el catálogo y estar `enabled=True`.

## Step 1: Añadir a `backend/app/schemas/ai_config.py`
```python
class AIConfigRead(BaseModel):
    tier: str
    provider: str
    model: str | None
    base_url: str | None
    has_api_key: bool
    monthly_quota: int
    used_count: int


class AIConfigUpdate(BaseModel):
    tier: str
    provider: str
    model: str | None = None
    base_url: str | None = None
    api_key: str | None = None
```
(Mantén `HardwareQuery` y `Recommendation` ya existentes; añade el import `from pydantic import BaseModel, Field` si no está.)

## Step 2: Crear `backend/app/repositories/ai_config.py`
```python
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ai_config import FamilyAIConfig


def get_or_create(db: Session, family_id: int) -> FamilyAIConfig:
    cfg = db.execute(
        select(FamilyAIConfig).where(FamilyAIConfig.family_id == family_id)
    ).scalar_one_or_none()
    if cfg is None:
        cfg = FamilyAIConfig(family_id=family_id)
        db.add(cfg)
        db.commit()
        db.refresh(cfg)
    return cfg
```

## Step 3: Añadir GET/PUT en `backend/app/routers/ai_config.py`
Añade imports al principio:
```python
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.repositories import ai_config as ai_config_repo
from app.schemas.ai_config import AIConfigRead, AIConfigUpdate
from app.services import crypto
```
Y un helper + las rutas:
```python
_VALID_TIERS = {"free", "byok", "managed"}


def _to_read(cfg) -> AIConfigRead:
    return AIConfigRead(
        tier=cfg.tier,
        provider=cfg.provider,
        model=cfg.model,
        base_url=cfg.base_url,
        has_api_key=bool(cfg.api_key_encrypted),
        monthly_quota=cfg.monthly_quota,
        used_count=cfg.used_count,
    )


@router.get("", response_model=AIConfigRead)
def get_config(
    user: User = Depends(get_current_family_user),
    db: Session = Depends(get_db),
) -> AIConfigRead:
    return _to_read(ai_config_repo.get_or_create(db, user.family_id))


@router.put("", response_model=AIConfigRead)
def put_config(
    payload: AIConfigUpdate,
    user: User = Depends(get_current_family_user),
    db: Session = Depends(get_db),
) -> AIConfigRead:
    if payload.tier not in _VALID_TIERS:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Nivel inválido")
    provider = next((p for p in ai_catalog.PROVIDERS if p["id"] == payload.provider), None)
    if provider is None or not provider["enabled"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Proveedor no disponible",
        )
    cfg = ai_config_repo.get_or_create(db, user.family_id)
    cfg.tier = payload.tier
    cfg.provider = payload.provider
    cfg.model = payload.model
    cfg.base_url = payload.base_url
    if payload.api_key is not None:
        if payload.api_key == "":
            cfg.api_key_encrypted = None
        else:
            try:
                cfg.api_key_encrypted = crypto.encrypt(payload.api_key, get_settings().ai_config_key)
            except RuntimeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El servidor no tiene AI_CONFIG_KEY configurada para guardar claves.",
                )
    db.commit()
    db.refresh(cfg)
    return _to_read(cfg)
```
(El módulo ya importa `ai_catalog`, `get_current_family_user`, `User` y `router` de la Task C2 — reutilízalos.)

## Step 4: Test `backend/tests/test_ai_config_crud.py`
```python
from app.config import get_settings
from app.services.crypto import generate_key


def _auth(client):
    r = client.post(
        "/auth/register",
        json={"name": "F", "email": "crud@example.com", "password": "secret123"},
    )
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_default_config_is_free_stub(client):
    body = client.get("/family/ai-config", headers=_auth(client)).json()
    assert body["tier"] == "free"
    assert body["provider"] == "stub"
    assert body["has_api_key"] is False


def test_put_byok_claude_stores_key_without_returning_it(client):
    get_settings().ai_config_key = generate_key()  # clave maestra de prueba
    h = _auth(client)
    r = client.put(
        "/family/ai-config",
        headers=h,
        json={"tier": "byok", "provider": "claude", "model": "claude-haiku-4-5", "api_key": "sk-ant-test"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["provider"] == "claude"
    assert body["has_api_key"] is True
    assert "api_key" not in body and "api_key_encrypted" not in body


def test_put_rejects_disabled_provider(client):
    h = _auth(client)
    r = client.put(
        "/family/ai-config",
        headers=h,
        json={"tier": "byok", "provider": "openai", "model": "gpt-4o-mini"},
    )
    assert r.status_code == 422


def test_get_requires_auth(client):
    assert client.get("/family/ai-config").status_code == 401
```

## Step 5: Tests + suite
`./.venv/Scripts/python.exe -m pytest tests/test_ai_config_crud.py -v` → PASS. Luego `-q` completa → todo PASS.

## Step 6: Commit (local, SIN push)
```bash
git add backend/
git commit -m "feat(backend): family AI config GET/PUT with encrypted key"
```
