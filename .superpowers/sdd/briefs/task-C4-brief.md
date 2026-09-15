# Task C4: Adaptadores de proveedor (HTTP) + fábrica con fallback

Backend `backend/`, venv `./.venv/Scripts/python.exe`. Rama `feature-entrega4-ai-config`. SIN push. TDD.
Todos los adaptadores implementan la interfaz `LessonGenerator` ya existente (`app/services/lesson_generator.py`: `generate(curiosity, age, subject) -> GeneratedLesson`, con `SUBJECTS`, `StubLessonGenerator`, `GeneratedLesson`).

**Files:**
- Create: `backend/app/services/ai_providers.py`
- Test: `backend/tests/test_ai_providers.py`

## Step 1: Crear `backend/app/services/ai_providers.py`
```python
"""Adaptadores reales de generación (HTTP, sin SDKs). Claude y Ollama activos;
OpenAI/DeepSeek/Kimi/Gemini preparados. La fábrica elige según la config de la familia.
Cualquier fallo lo gestiona el lesson_service (fallback al stub)."""
import json

import httpx

from app.config import get_settings
from app.services import crypto
from app.services.ai_catalog import DEFAULT_LOCAL_MODEL
from app.services.lesson_generator import (
    SUBJECTS,
    GeneratedLesson,
    LessonGenerator,
    StubLessonGenerator,
)

_TIMEOUT = 120.0


def _system_prompt(age: int) -> str:
    return (
        f"Eres un generador de mini-lecciones para un niño de {age} años. "
        "Responde SOLO con JSON válido, sin texto adicional ni markdown. "
        "Contenido apropiado para su edad, en español, breve y positivo. "
        'Forma exacta: {"subject": "ciencia|matematicas|lenguaje|arte|cultura", '
        '"concept": "...", "title": "...", "body": "...", "fun_fact": "...", '
        '"quiz": {"question": "...", "options": ["a","b","c"], "correct_index": 0, "explanation": "..."}}'
    )


def _user_prompt(curiosity: str, subject: str | None) -> str:
    extra = f" Teje la materia '{subject}'." if subject in SUBJECTS else ""
    return f"Curiosidad del niño: «{curiosity}».{extra} Genera la lección en JSON."


def _strip_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t
        t = t.rsplit("```", 1)[0]
    return t.strip()


def _parse_lesson(text: str, curiosity: str, subject: str | None) -> GeneratedLesson:
    data = json.loads(_strip_fences(text))
    quiz = data["quiz"]
    options = list(quiz["options"])[:3]
    if len(options) != 3:
        raise ValueError("el quiz debe tener 3 opciones")
    idx = int(quiz["correct_index"])
    if not 0 <= idx < 3:
        raise ValueError("correct_index fuera de rango")
    chosen = data.get("subject") if data.get("subject") in SUBJECTS else (
        subject if subject in SUBJECTS else SUBJECTS[len(curiosity.strip()) % len(SUBJECTS)]
    )
    return GeneratedLesson(
        subject=chosen,
        concept=str(data["concept"])[:120],
        title=str(data["title"])[:200],
        body=str(data["body"]),
        fun_fact=str(data["fun_fact"]),
        quiz_question=str(quiz["question"])[:300],
        quiz_options=[str(o) for o in options],
        quiz_correct_index=idx,
        quiz_explanation=str(quiz["explanation"]),
    )


class ClaudeGenerator:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def generate(self, curiosity: str, age: int, subject: str | None) -> GeneratedLesson:
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model,
                "max_tokens": 800,
                "system": _system_prompt(age),
                "messages": [{"role": "user", "content": _user_prompt(curiosity, subject)}],
            },
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        text = resp.json()["content"][0]["text"]
        return _parse_lesson(text, curiosity, subject)


class OllamaGenerator:
    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    def generate(self, curiosity: str, age: int, subject: str | None) -> GeneratedLesson:
        resp = httpx.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": _system_prompt(age)},
                    {"role": "user", "content": _user_prompt(curiosity, subject)},
                ],
                "stream": False,
                "format": "json",
            },
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        text = resp.json()["message"]["content"]
        return _parse_lesson(text, curiosity, subject)


class OpenAICompatGenerator:
    """OpenAI / DeepSeek / Kimi (Moonshot) — misma API /chat/completions (preparado)."""

    _BASES = {
        "openai": "https://api.openai.com/v1",
        "deepseek": "https://api.deepseek.com/v1",
        "kimi": "https://api.moonshot.cn/v1",
    }

    def __init__(self, provider: str, api_key: str, model: str) -> None:
        self.base = self._BASES[provider]
        self.api_key = api_key
        self.model = model

    def generate(self, curiosity: str, age: int, subject: str | None) -> GeneratedLesson:
        resp = httpx.post(
            f"{self.base}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": _system_prompt(age)},
                    {"role": "user", "content": _user_prompt(curiosity, subject)},
                ],
                "response_format": {"type": "json_object"},
            },
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"]
        return _parse_lesson(text, curiosity, subject)


class GeminiGenerator:
    """Google Gemini (preparado)."""

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def generate(self, curiosity: str, age: int, subject: str | None) -> GeneratedLesson:
        prompt = _system_prompt(age) + "\n\n" + _user_prompt(curiosity, subject)
        resp = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
            params={"key": self.api_key},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"},
            },
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        return _parse_lesson(text, curiosity, subject)


def _decrypt_key(encrypted: str | None) -> str | None:
    if not encrypted:
        return None
    try:
        return crypto.decrypt(encrypted, get_settings().ai_config_key)
    except Exception:
        return None


def build_generator(config) -> LessonGenerator:
    """config: FamilyAIConfig | None → adaptador. Sin clave/desconocido → stub."""
    if config is None or config.provider == "stub":
        return StubLessonGenerator()
    if config.provider == "ollama":
        return OllamaGenerator(
            base_url=config.base_url or "http://localhost:11434",
            model=config.model or DEFAULT_LOCAL_MODEL,
        )
    key = _decrypt_key(config.api_key_encrypted)
    if config.provider == "claude" and key:
        return ClaudeGenerator(api_key=key, model=config.model or "claude-haiku-4-5")
    if config.provider in {"openai", "deepseek", "kimi"} and key:
        return OpenAICompatGenerator(provider=config.provider, api_key=key, model=config.model or "")
    if config.provider == "gemini" and key:
        return GeminiGenerator(api_key=key, model=config.model or "gemini-1.5-flash")
    return StubLessonGenerator()
```

## Step 2: Test `backend/tests/test_ai_providers.py`
```python
import json

import httpx
import pytest

from app.config import get_settings
from app.models.ai_config import FamilyAIConfig
from app.services import ai_providers, crypto
from app.services.ai_providers import (
    ClaudeGenerator,
    OllamaGenerator,
    build_generator,
)
from app.services.lesson_generator import StubLessonGenerator

_LESSON_JSON = json.dumps({
    "subject": "ciencia",
    "concept": "lluvia",
    "title": "¿Por qué llueve?",
    "body": "El agua sube y baja.",
    "fun_fact": "Las nubes pesan mucho.",
    "quiz": {"question": "¿Qué cae?", "options": ["sol", "agua", "viento"], "correct_index": 1, "explanation": "Cae agua."},
})


class _FakeResp:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def test_claude_generator_parses(monkeypatch):
    def fake_post(url, **kwargs):
        assert "api.anthropic.com" in url
        return _FakeResp({"content": [{"text": _LESSON_JSON}]})

    monkeypatch.setattr(httpx, "post", fake_post)
    g = ClaudeGenerator(api_key="k", model="claude-haiku-4-5")
    lesson = g.generate("¿por qué llueve?", age=7, subject=None)
    assert lesson.subject == "ciencia"
    assert lesson.quiz_correct_index == 1
    assert len(lesson.quiz_options) == 3


def test_ollama_generator_parses(monkeypatch):
    def fake_post(url, **kwargs):
        assert url.endswith("/api/chat")
        return _FakeResp({"message": {"content": _LESSON_JSON}})

    monkeypatch.setattr(httpx, "post", fake_post)
    g = OllamaGenerator(base_url="http://ollama:11434", model="qwen3:4b")
    lesson = g.generate("dinosaurios", age=8, subject="arte")
    assert lesson.title


def test_parse_raises_on_bad_json(monkeypatch):
    monkeypatch.setattr(httpx, "post", lambda url, **kw: _FakeResp({"content": [{"text": "no soy json"}]}))
    with pytest.raises(Exception):
        ClaudeGenerator(api_key="k", model="m").generate("x", age=7, subject=None)


def test_factory_stub_for_none_and_stub_provider():
    assert isinstance(build_generator(None), StubLessonGenerator)
    cfg = FamilyAIConfig(family_id=1, provider="stub")
    assert isinstance(build_generator(cfg), StubLessonGenerator)


def test_factory_builds_claude_when_byok_with_key():
    get_settings().ai_config_key = crypto.generate_key()
    cfg = FamilyAIConfig(
        family_id=1, tier="byok", provider="claude", model="claude-haiku-4-5",
        api_key_encrypted=crypto.encrypt("sk-ant", get_settings().ai_config_key),
    )
    assert isinstance(build_generator(cfg), ClaudeGenerator)


def test_factory_falls_back_to_stub_without_key():
    cfg = FamilyAIConfig(family_id=1, tier="byok", provider="claude", model="claude-haiku-4-5")
    assert isinstance(build_generator(cfg), StubLessonGenerator)
```

## Step 3: Tests + suite
`./.venv/Scripts/python.exe -m pytest tests/test_ai_providers.py -v` → PASS. Luego `-q` completa → todo PASS. (`ruff check .` limpio.)

## Step 4: Commit (local, SIN push)
```bash
git add backend/
git commit -m "feat(backend): HTTP provider adapters (Claude/Ollama active, others ready) + factory"
```
