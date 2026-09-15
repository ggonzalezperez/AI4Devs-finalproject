import json

import httpx
import pytest

from app.config import get_settings
from app.models.ai_config import FamilyAIConfig
from app.services import crypto
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
    "follow_ups": ["¿De dónde viene el agua?", "¿Por qué hay nubes?", "¿Qué es la niebla?"],
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
    assert isinstance(lesson.follow_ups, list)
    assert len(lesson.follow_ups) == 3


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
    with pytest.raises((ValueError, KeyError)):
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
