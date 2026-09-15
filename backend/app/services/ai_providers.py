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


def _age_band(age: int) -> str:
    if age <= 5:
        return (
            "Edad 3-5 (aún no lee bien): 2 o 3 frases muy cortas, palabras muy sencillas y "
            "algún sonido divertido (¡pum!, ¡splash!). Compara con cosas que ve cada día "
            "(juguetes, animales, comida). Quiz muy fácil."
        )
    if age <= 8:
        return (
            "Edad 6-8: 4 a 6 frases. Una analogía clara del día a día y un porqué sencillo. "
            "Quiz de dificultad media."
        )
    return (
        "Edad 9-12: 6 a 9 frases. Puedes introducir UNA palabra nueva y explicarla. Muestra "
        "una causa y su efecto, y propón un pequeño reto del mundo real. Quiz algo más exigente."
    )


def _system_prompt(age: int) -> str:
    return (
        f"Eres Chispa, un guía cálido y curioso que ayuda a un niño de {age} años a resolver "
        "su curiosidad CON CONOCIMIENTO. Hablas como alguien mayor que sabe mucho y disfruta "
        "enseñando: cercano, con asombro, nunca por encima del niño.\n"
        "Pedagogía:\n"
        "- Ancla TODO a la pregunta del niño (su curiosidad es la misión).\n"
        "- Enseña UNA sola idea clara (un '¡ajá!'), sin abrumar.\n"
        "- Usa una analogía de su mundo (juguetes, animales, comida, juegos).\n"
        "- Añade un dato sorprendente que despierte más ganas de saber.\n"
        "- Termina invitando a seguir preguntando.\n"
        "- Sé veraz y apropiado a su edad; no inventes.\n"
        f"Estilo para esta edad: {_age_band(age)}\n"
        "El quiz es práctica de recuerdo: 3 opciones de longitud parecida (número de palabras "
        "similar); ninguna debe destacar por formato o longitud; solo una correcta.\n"
        "'follow_ups' son 2 o 3 preguntas cortas y atractivas, en la voz del niño, que podría "
        "hacer a continuación para profundizar.\n"
        "Responde SOLO con JSON válido, sin texto adicional ni markdown. Forma exacta: "
        '{"subject": "ciencia|matematicas|lenguaje|arte|cultura", "concept": "...", '
        '"title": "...", "body": "...", "fun_fact": "...", '
        '"follow_ups": ["...", "...", "..."], '
        '"quiz": {"question": "...", "options": ["a","b","c"], "correct_index": 0, "explanation": "..."}}'
    )


def _user_prompt(curiosity: str, subject: str | None, history: list[tuple[str, str]] | None = None) -> str:
    if history:
        convo = "\n".join(f"Niño: {q}\nChispa: {a}" for q, a in history)
        return (
            "Conversación hasta ahora:\n" + convo + "\n\n"
            f"El niño continúa preguntando: «{curiosity}». Responde SIGUIENDO el hilo, "
            "sin repetir lo ya dicho, profundizando un poco más. Genera la lección en JSON."
        )
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
    raw_fu = data.get("follow_ups")
    follow_ups = [str(x) for x in raw_fu][:3] if isinstance(raw_fu, list) else []
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
        follow_ups=follow_ups,
    )


class ClaudeGenerator:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def generate(self, curiosity: str, age: int, subject: str | None, history: list[tuple[str, str]] | None = None) -> GeneratedLesson:
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model,
                "max_tokens": 1400,
                "system": _system_prompt(age),
                "messages": [{"role": "user", "content": _user_prompt(curiosity, subject, history)}],
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

    def generate(self, curiosity: str, age: int, subject: str | None, history: list[tuple[str, str]] | None = None) -> GeneratedLesson:
        resp = httpx.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": _system_prompt(age)},
                    {"role": "user", "content": _user_prompt(curiosity, subject, history)},
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

    def generate(self, curiosity: str, age: int, subject: str | None, history: list[tuple[str, str]] | None = None) -> GeneratedLesson:
        resp = httpx.post(
            f"{self.base}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": _system_prompt(age)},
                    {"role": "user", "content": _user_prompt(curiosity, subject, history)},
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

    def generate(self, curiosity: str, age: int, subject: str | None, history: list[tuple[str, str]] | None = None) -> GeneratedLesson:
        prompt = _system_prompt(age) + "\n\n" + _user_prompt(curiosity, subject, history)
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
        return GeminiGenerator(api_key=key, model=config.model or "gemini-3.5-flash-lite")
    return StubLessonGenerator()
