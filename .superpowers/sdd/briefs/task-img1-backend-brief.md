# Task IMG-1: Generación de imágenes en lecciones — núcleo backend

Backend `backend/`, venv `./.venv/Scripts/python.exe`. Rama `feature-imagenes`. SIN push. TDD, migración NO destructiva.
Añade la "costura" de imagen detrás de una interfaz `ImageGenerator`, con adaptadores **local (SDXL/Automatic1111) y proveedores (HuggingFace gratis, OpenAI, Gemini)**, configurable por familia y **desactivada por defecto** (sin coste, degrada con elegancia). Cuando está activa, cada lección genera una imagen acorde a la edad, se guarda en disco y se sirve por `/media`.

IMPORTANTE: por defecto `image_enabled=False` y `image_provider="none"` → NINGUNA lección genera imagen (comportamiento actual intacto). Cualquier fallo del generador NO debe romper la creación de la lección (best-effort).

**Files:**
- Create: `app/services/image_generator.py`
- Create: `app/services/image_providers.py`
- Modify: `app/models/ai_config.py` (campos de imagen en FamilyAIConfig)
- Modify: `app/models/lesson.py` (`image_url`)
- Modify: `app/config.py` (`media_dir`, `image_timeout`)
- Modify: `app/main.py` (montar StaticFiles `/media`)
- Modify: `app/services/lesson_service.py` (adjuntar imagen best-effort)
- Modify: `app/schemas/lesson.py` (`LessonRead.image_url`)
- Modify: `app/services/ai_catalog.py` (`IMAGE_PROVIDERS`)
- Modify: `.gitignore` (raíz o backend) → añadir `media/` y `backend/media/`
- Migración Alembic (columnas nuevas, no destructiva)
- Tests

## Step 1: `app/config.py`
En `Settings`, añade:
```python
    media_dir: str = "media"
    image_timeout: float = 60.0
```

## Step 2: `app/models/ai_config.py`
Importa `Boolean` (de sqlalchemy) y añade a `FamilyAIConfig`:
```python
    # Imagen (Fase C). image_provider: none | huggingface | local_sdxl | openai | gemini
    image_provider: Mapped[str] = mapped_column(String(20), default="none")
    image_model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    image_base_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    image_api_key_encrypted: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
```

## Step 3: `app/models/lesson.py`
Añade (String ya importado):
```python
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
```

## Step 4: `app/services/image_generator.py`
```python
from dataclasses import dataclass
from typing import Protocol


@dataclass
class GeneratedImage:
    data: bytes
    mime: str = "image/png"


class ImageGenerator(Protocol):
    def generate(self, prompt: str) -> GeneratedImage | None: ...


class StubImageGenerator:
    """Sin imagen (desactivado). Degradado por defecto."""

    def generate(self, prompt: str) -> GeneratedImage | None:
        return None


def build_image_prompt(concept: str, age: int) -> str:
    if age <= 8:
        style = "ilustración infantil colorida tipo dibujo animado, amable y sencilla, sin texto"
    else:
        style = "ilustración educativa realista y detallada, apropiada para niños, sin texto"
    return f"{concept}. {style}. Contenido seguro y apto para niños."
```

## Step 5: `app/services/image_providers.py`
```python
"""Adaptadores de generación de imagen (HTTP, sin SDKs). Local (SDXL/Automatic1111)
y proveedores (HuggingFace gratis, OpenAI, Gemini). La fábrica elige según la config
de la familia; cualquier fallo lo absorbe el lesson_service (best-effort)."""
import base64

import httpx

from app.config import get_settings
from app.services import crypto
from app.services.image_generator import (
    GeneratedImage,
    ImageGenerator,
    StubImageGenerator,
)


def _timeout() -> float:
    return get_settings().image_timeout


class HuggingFaceImageGenerator:
    """HuggingFace Inference API (gratis con token hf_***, con límite de uso)."""

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model or "black-forest-labs/FLUX.1-schnell"

    def generate(self, prompt: str) -> GeneratedImage | None:
        resp = httpx.post(
            f"https://api-inference.huggingface.co/models/{self.model}",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"inputs": prompt},
            timeout=_timeout(),
        )
        resp.raise_for_status()
        mime = resp.headers.get("content-type", "image/png")
        return GeneratedImage(data=resp.content, mime=mime)


class LocalSDXLImageGenerator:
    """Endpoint local tipo Automatic1111 (`/sdapi/v1/txt2img`). Sin clave."""

    def __init__(self, base_url: str, model: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str) -> GeneratedImage | None:
        resp = httpx.post(
            f"{self.base_url}/sdapi/v1/txt2img",
            json={"prompt": prompt, "steps": 20, "width": 768, "height": 768},
            timeout=_timeout(),
        )
        resp.raise_for_status()
        images = resp.json().get("images") or []
        if not images:
            return None
        return GeneratedImage(data=base64.b64decode(images[0]), mime="image/png")


class OpenAIImageGenerator:
    """OpenAI Images API (gpt-image-1). De pago."""

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model or "gpt-image-1"

    def generate(self, prompt: str) -> GeneratedImage | None:
        resp = httpx.post(
            "https://api.openai.com/v1/images/generations",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "prompt": prompt, "size": "1024x1024", "n": 1},
            timeout=_timeout(),
        )
        resp.raise_for_status()
        b64 = resp.json()["data"][0]["b64_json"]
        return GeneratedImage(data=base64.b64decode(b64), mime="image/png")


class GeminiImageGenerator:
    """Google Imagen vía API de Gemini (`:predict`). De pago."""

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model or "imagen-3.0-generate-002"

    def generate(self, prompt: str) -> GeneratedImage | None:
        resp = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:predict",
            params={"key": self.api_key},
            json={"instances": [{"prompt": prompt}], "parameters": {"sampleCount": 1}},
            timeout=_timeout(),
        )
        resp.raise_for_status()
        preds = resp.json().get("predictions") or []
        if not preds:
            return None
        b64 = preds[0]["bytesBase64Encoded"]
        return GeneratedImage(data=base64.b64decode(b64), mime="image/png")


def _decrypt_key(encrypted: str | None) -> str | None:
    if not encrypted:
        return None
    try:
        return crypto.decrypt(encrypted, get_settings().ai_config_key)
    except Exception:
        return None


def build_image_generator(config) -> ImageGenerator:
    """config: FamilyAIConfig | None → adaptador de imagen. Desactivado → Stub (sin imagen)."""
    if config is None or not getattr(config, "image_enabled", False):
        return StubImageGenerator()
    provider = getattr(config, "image_provider", "none")
    model = getattr(config, "image_model", None)
    if provider == "local_sdxl" and config.image_base_url:
        return LocalSDXLImageGenerator(base_url=config.image_base_url, model=model)
    key = _decrypt_key(getattr(config, "image_api_key_encrypted", None))
    if provider == "huggingface" and key:
        return HuggingFaceImageGenerator(api_key=key, model=model or "black-forest-labs/FLUX.1-schnell")
    if provider == "openai" and key:
        return OpenAIImageGenerator(api_key=key, model=model or "gpt-image-1")
    if provider == "gemini" and key:
        return GeminiImageGenerator(api_key=key, model=model or "imagen-3.0-generate-002")
    return StubImageGenerator()
```

## Step 6: `app/main.py` — servir `/media`
Tras crear `app` (y antes o después de los routers), monta los estáticos:
```python
from pathlib import Path
from fastapi.staticfiles import StaticFiles
# ...
_media_root = Path(get_settings().media_dir)
(_media_root / "lessons").mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(_media_root)), name="media")
```
(Colócalo después de `app = FastAPI(...)` y del middleware CORS.)

## Step 7: `app/services/lesson_service.py` — adjuntar imagen best-effort
Importa arriba:
```python
from pathlib import Path
from app.config import get_settings
from app.services.image_generator import build_image_prompt
from app.services.image_providers import build_image_generator
```
Añade el helper:
```python
def _attach_image(db: Session, cfg, lesson: Lesson, age: int) -> None:
    gen = build_image_generator(cfg)
    try:
        img = gen.generate(build_image_prompt(lesson.concept, age))
    except Exception:
        img = None
    if img is None:
        return
    try:
        media = Path(get_settings().media_dir) / "lessons"
        media.mkdir(parents=True, exist_ok=True)
        (media / f"{lesson.id}.png").write_bytes(img.data)
        lesson.image_url = f"/media/lessons/{lesson.id}.png"
        db.commit()
    except Exception:
        db.rollback()
```
Llama a `_attach_image(db, cfg, lesson, child.age)` justo antes del `return` final TANTO en `create_lesson` como en `continue_conversation` (después de que la lección ya tiene id y se ha asegurado la isla). En `create_lesson` la variable de config se llama `cfg`; reutilízala. (Si `create_lesson` no conserva `cfg` hasta el final, guárdalo en una variable y pásalo.)

## Step 8: `app/schemas/lesson.py`
En `LessonRead` añade: `image_url: str | None = None`

## Step 9: `app/services/lesson_service.py` — `to_read_dict`
Añade al dict: `"image_url": lesson.image_url,`

## Step 10: `app/services/ai_catalog.py` — catálogo de imagen
Añade al final (antes de `recommend_local` o tras `PROVIDERS`):
```python
IMAGE_PROVIDERS = [
    {"id": "none", "label": "Sin imágenes", "tier": "free", "needs_key": False, "needs_base_url": False, "enabled": True, "models": []},
    {"id": "huggingface", "label": "HuggingFace (gratis con token)", "tier": "free", "needs_key": True, "needs_base_url": False, "enabled": True, "models": ["black-forest-labs/FLUX.1-schnell", "stabilityai/stable-diffusion-xl-base-1.0"]},
    {"id": "local_sdxl", "label": "SDXL local (Automatic1111)", "tier": "free", "needs_key": False, "needs_base_url": True, "enabled": True, "models": []},
    {"id": "openai", "label": "OpenAI (gpt-image-1)", "tier": "byok", "needs_key": True, "needs_base_url": False, "enabled": True, "models": ["gpt-image-1"]},
    {"id": "gemini", "label": "Gemini Imagen", "tier": "byok", "needs_key": True, "needs_base_url": False, "enabled": True, "models": ["imagen-3.0-generate-002"]},
]
```

## Step 11: `.gitignore`
Añade (para no commitear imágenes generadas):
```
media/
backend/media/
```

## Step 12: Migración
- `./.venv/Scripts/alembic.exe revision --autogenerate -m "image generation config + lesson image_url"`
- Verifica que SOLO añade columnas a `family_ai_config` (image_*) y `lessons.image_url`. Si hay drops/alters sobre otras tablas, DETENTE y reporta DONE_WITH_CONCERNS sin aplicar.
- Aplica: `./.venv/Scripts/alembic.exe upgrade head`.

## Step 13: Tests (`tests/test_images.py`)
- `StubImageGenerator().generate("x") is None`.
- `build_image_generator(None)` y un config con `image_enabled=False` → `StubImageGenerator`.
- `build_image_prompt("volcanes", 5)` contiene "dibujo" y `build_image_prompt("volcanes", 11)` contiene "realista".
- `_attach_image` con un generador stub-falso que devuelve `GeneratedImage(b"PNGBYTES")`: inyecta monkeypatch de `build_image_generator` (o crea un cfg con un provider mockeado) para que escriba el archivo y fije `lesson.image_url` a `/media/lessons/{id}.png`. Verifica que el archivo existe. (Usa `tmp_path` para `media_dir` vía monkeypatch de settings si es posible; si no, escribe en `media/lessons` y limpia.)
- Lección por defecto: `image_url is None` (el flujo normal con config free no genera imagen). Comprueba vía API que una lección creada con la familia por defecto tiene `image_url == None`.
- Mantén verdes los tests existentes. `./.venv/Scripts/python.exe -m pytest -q` → todo PASS.

## Step 14: Commit (local, SIN push)
```bash
git add backend/ .gitignore
git commit -m "feat(backend): image generation seam (HF/local-SDXL/OpenAI/Gemini), default off"
```
