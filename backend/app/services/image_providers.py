"""Adaptadores de generación de imagen (HTTP, sin SDKs). Local (SDXL/Automatic1111)
y proveedores (HuggingFace gratis, OpenAI, Gemini). La fábrica elige según la config
de la familia; cualquier fallo lo absorbe el lesson_service (best-effort)."""
import base64
import ipaddress
import socket
from urllib.parse import quote, urlparse

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


def validate_local_url(url: str) -> str:
    """Mitiga SSRF en el endpoint SDXL local. Apuntar a localhost/LAN es el uso
    PREVISTO (el endpoint privado del propio usuario), así que NO bloqueamos rangos
    privados; pero sí rechazamos esquemas no-HTTP y direcciones link-local
    (169.254.0.0/16, fe80::/10), el principal objetivo de SSRF (metadatos de nube).
    Lanza ValueError si la URL no es válida o no permitida."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("URL de SDXL local inválida")
    try:
        infos = socket.getaddrinfo(parsed.hostname, None)
    except OSError as exc:
        raise ValueError("No se pudo resolver el host de SDXL local") from exc
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_link_local:
            raise ValueError("Dirección no permitida para SDXL local")
    return url


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
            follow_redirects=False,
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
            follow_redirects=False,
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
        self.model = model or "gpt-image-1-mini"

    def generate(self, prompt: str) -> GeneratedImage | None:
        resp = httpx.post(
            "https://api.openai.com/v1/images/generations",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "prompt": prompt, "size": "1024x1024", "n": 1},
            timeout=_timeout(),
            follow_redirects=False,
        )
        resp.raise_for_status()
        b64 = resp.json()["data"][0]["b64_json"]
        return GeneratedImage(data=base64.b64decode(b64), mime="image/png")


class GeminiImageGenerator:
    """Google Imagen vía API de Gemini (`:predict`). De pago."""

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model or "gemini-3.1-flash-image"

    def generate(self, prompt: str) -> GeneratedImage | None:
        resp = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:predict",
            params={"key": self.api_key},
            json={"instances": [{"prompt": prompt}], "parameters": {"sampleCount": 1}},
            timeout=_timeout(),
            follow_redirects=False,
        )
        resp.raise_for_status()
        preds = resp.json().get("predictions") or []
        if not preds:
            return None
        b64 = preds[0]["bytesBase64Encoded"]
        return GeneratedImage(data=base64.b64decode(b64), mime="image/png")


class PollinationsImageGenerator:
    """Pollinations.ai — text-to-image GRATIS y SIN clave. Funciona sin configurar
    nada. Aviso: envía el prompt (el concepto de la lección) a un servicio externo;
    no se le manda ningún dato personal del niño. `safe=true` filtra contenido."""

    def __init__(self, model: str | None = None) -> None:
        self.model = model or "flux"

    def generate(self, prompt: str) -> GeneratedImage | None:
        resp = httpx.get(
            f"https://image.pollinations.ai/prompt/{quote(prompt)}",
            params={
                "width": 768,
                "height": 768,
                "model": self.model,
                "nologo": "true",
                "safe": "true",
            },
            timeout=_timeout(),
            follow_redirects=True,
        )
        resp.raise_for_status()
        mime = resp.headers.get("content-type", "image/jpeg")
        if not mime.startswith("image/"):
            return None
        return GeneratedImage(data=resp.content, mime=mime)


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
        try:
            safe_url = validate_local_url(config.image_base_url)
        except ValueError:
            return StubImageGenerator()
        return LocalSDXLImageGenerator(base_url=safe_url, model=model)
    if provider == "pollinations":
        return PollinationsImageGenerator(model=model)
    key = _decrypt_key(getattr(config, "image_api_key_encrypted", None))
    if provider == "huggingface" and key:
        return HuggingFaceImageGenerator(api_key=key, model=model or "black-forest-labs/FLUX.1-schnell")
    if provider == "openai" and key:
        return OpenAIImageGenerator(api_key=key, model=model or "gpt-image-1-mini")
    if provider == "gemini" and key:
        return GeminiImageGenerator(api_key=key, model=model or "gemini-3.1-flash-image")
    return StubImageGenerator()
