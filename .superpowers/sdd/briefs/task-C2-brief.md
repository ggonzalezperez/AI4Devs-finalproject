# Task C2: Catálogo de modelos + recomendador por hardware + endpoints

Backend `backend/`, venv `./.venv/Scripts/python.exe`. Rama `feature-entrega4-ai-config`. SIN push. TDD.

**Files:**
- Create: `backend/app/services/ai_catalog.py`
- Create: `backend/app/schemas/ai_config.py`
- Create: `backend/app/routers/ai_config.py`
- Modify: `backend/app/main.py` (incluir router)
- Test: `backend/tests/test_ai_catalog.py`
- Test: `backend/tests/test_ai_config_api.py`

## Step 1: Crear `backend/app/services/ai_catalog.py`
```python
# Catálogo curado de modelos locales (Ollama) con requisitos de hardware.
OLLAMA_MODELS = [
    {"id": "llama3.2:3b", "label": "Llama 3.2 3B", "min_vram_gb": 4, "min_ram_gb": 8, "speed": "muy rápido"},
    {"id": "qwen3:4b", "label": "Qwen3 4B", "min_vram_gb": 6, "min_ram_gb": 8, "speed": "rápido"},
    {"id": "gemma3:4b", "label": "Gemma 3 4B", "min_vram_gb": 6, "min_ram_gb": 8, "speed": "rápido"},
    {"id": "phi4-mini", "label": "Phi-4 mini", "min_vram_gb": 6, "min_ram_gb": 8, "speed": "rápido"},
    {"id": "qwen3:14b", "label": "Qwen3 14B", "min_vram_gb": 12, "min_ram_gb": 16, "speed": "medio"},
    {"id": "deepseek-r1:32b", "label": "DeepSeek-R1 32B", "min_vram_gb": 24, "min_ram_gb": 32, "speed": "lento"},
]

# Proveedores. enabled=False = preparado pero no activo todavía (D21).
PROVIDERS = [
    {"id": "stub", "label": "Demo (sin IA)", "tier": "free", "needs_key": False, "needs_base_url": False, "enabled": True, "models": []},
    {"id": "ollama", "label": "Local (Ollama)", "tier": "free", "needs_key": False, "needs_base_url": True, "enabled": True, "models": [m["id"] for m in OLLAMA_MODELS]},
    {"id": "claude", "label": "Claude (Anthropic)", "tier": "byok", "needs_key": True, "needs_base_url": False, "enabled": True, "models": ["claude-haiku-4-5", "claude-sonnet-4-6", "claude-opus-4-8"]},
    {"id": "openai", "label": "OpenAI", "tier": "byok", "needs_key": True, "needs_base_url": False, "enabled": False, "models": ["gpt-4o-mini", "gpt-4o"]},
    {"id": "gemini", "label": "Gemini (Google)", "tier": "byok", "needs_key": True, "needs_base_url": False, "enabled": False, "models": ["gemini-1.5-flash", "gemini-1.5-pro"]},
    {"id": "deepseek", "label": "DeepSeek (API)", "tier": "byok", "needs_key": True, "needs_base_url": False, "enabled": False, "models": ["deepseek-chat"]},
    {"id": "kimi", "label": "Kimi (Moonshot)", "tier": "byok", "needs_key": True, "needs_base_url": False, "enabled": False, "models": ["moonshot-v1-8k"]},
]

DEFAULT_LOCAL_MODEL = "qwen3:4b"


def recommend_local(vram_gb: float, ram_gb: float) -> dict:
    fits = [
        m for m in OLLAMA_MODELS
        if vram_gb >= m["min_vram_gb"] and ram_gb >= m["min_ram_gb"]
    ]
    if fits:
        # Recomendar el mayor que quepa (mejor calidad disponible para su equipo).
        recommended = max(fits, key=lambda m: m["min_vram_gb"])["id"]
        note = "Tu equipo puede ejecutar estos modelos en local."
    else:
        recommended = "llama3.2:3b"
        note = (
            "Tu GPU es justa: usa el modelo más pequeño (puede ir lento en CPU), "
            "o elige el nivel gratis con demo, o pon tu propia clave (BYOK)."
        )
    return {
        "can_run_local": bool(fits),
        "fits": [m["id"] for m in fits],
        "recommended": recommended,
        "note": note,
    }
```

## Step 2: Crear `backend/app/schemas/ai_config.py`
```python
from pydantic import BaseModel, Field


class HardwareQuery(BaseModel):
    vram_gb: float = Field(ge=0)
    ram_gb: float = Field(ge=0)


class Recommendation(BaseModel):
    can_run_local: bool
    fits: list[str]
    recommended: str
    note: str
```

## Step 3: Crear `backend/app/routers/ai_config.py`
```python
from fastapi import APIRouter, Depends

from app.deps import get_current_family_user
from app.models.family import User
from app.schemas.ai_config import HardwareQuery, Recommendation
from app.services import ai_catalog

router = APIRouter(prefix="/family/ai-config", tags=["ai-config"])


@router.get("/catalog")
def catalog(_user: User = Depends(get_current_family_user)) -> dict:
    return {
        "providers": ai_catalog.PROVIDERS,
        "ollama_models": ai_catalog.OLLAMA_MODELS,
        "default_local_model": ai_catalog.DEFAULT_LOCAL_MODEL,
    }


@router.post("/recommend", response_model=Recommendation)
def recommend(
    payload: HardwareQuery,
    _user: User = Depends(get_current_family_user),
) -> Recommendation:
    return Recommendation(**ai_catalog.recommend_local(payload.vram_gb, payload.ram_gb))
```

## Step 4: Incluir el router en `backend/app/main.py`
Añade `ai_config` al import `from app.routers import ...` y `app.include_router(ai_config.router)`. NO toques CORS ni los demás routers.

## Step 5: Test `backend/tests/test_ai_catalog.py`
```python
from app.services.ai_catalog import recommend_local


def test_recommend_high_end_gpu_fits_32b():
    r = recommend_local(vram_gb=24, ram_gb=64)
    assert r["can_run_local"] is True
    assert "deepseek-r1:32b" in r["fits"]
    assert r["recommended"] == "deepseek-r1:32b"


def test_recommend_low_gpu_falls_back():
    r = recommend_local(vram_gb=2, ram_gb=8)
    assert r["can_run_local"] is False
    assert r["recommended"] == "llama3.2:3b"


def test_recommend_midrange_gpu():
    r = recommend_local(vram_gb=8, ram_gb=16)
    assert r["can_run_local"] is True
    assert "qwen3:4b" in r["fits"]
    assert "deepseek-r1:32b" not in r["fits"]
```

## Step 6: Test `backend/tests/test_ai_config_api.py`
```python
def _auth(client):
    r = client.post(
        "/auth/register",
        json={"name": "F", "email": "cfg@example.com", "password": "secret123"},
    )
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_catalog_requires_family_auth(client):
    assert client.get("/family/ai-config/catalog").status_code == 401


def test_catalog_lists_providers(client):
    body = client.get("/family/ai-config/catalog", headers=_auth(client)).json()
    ids = [p["id"] for p in body["providers"]]
    assert {"stub", "ollama", "claude"}.issubset(set(ids))
    assert body["default_local_model"] == "qwen3:4b"


def test_recommend_endpoint(client):
    r = client.post(
        "/family/ai-config/recommend",
        headers=_auth(client),
        json={"vram_gb": 24, "ram_gb": 64},
    )
    assert r.status_code == 200
    assert r.json()["recommended"] == "deepseek-r1:32b"
```

## Step 7: Tests + suite
`./.venv/Scripts/python.exe -m pytest tests/test_ai_catalog.py tests/test_ai_config_api.py -v` → PASS. Luego `-q` completa → todo PASS.

## Step 8: Commit (local, SIN push)
```bash
git add backend/
git commit -m "feat(backend): AI model catalog + hardware recommender + endpoints"
```
