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
# Los ids de modelo se verifican contra la documentación de cada proveedor, no
# de memoria: caducan, y cuando lo hacen la llamada falla y el niño cae al stub
# sin señal visible. Última verificación: 09-2026.
PROVIDERS = [
    {"id": "stub", "label": "Demo (sin IA)", "tier": "free", "needs_key": False, "needs_base_url": False, "enabled": True, "models": []},
    {"id": "ollama", "label": "Local (Ollama)", "tier": "free", "needs_key": False, "needs_base_url": True, "enabled": True, "models": [m["id"] for m in OLLAMA_MODELS]},
    {"id": "claude", "label": "Claude (Anthropic)", "tier": "byok", "needs_key": True, "needs_base_url": False, "enabled": True, "models": ["claude-haiku-4-5", "claude-sonnet-5", "claude-opus-5"]},
    # Modelos vigentes (verificados en developers.openai.com, 09-2026). Luna es el
    # barato y sobra para lecciones cortas; sol y astra están para quien los quiera.
    {"id": "openai", "label": "OpenAI", "tier": "byok", "needs_key": True, "needs_base_url": False, "enabled": True, "models": ["gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.6-sol", "gpt-6-astra"]},
    {"id": "gemini", "label": "Gemini (Google)", "tier": "byok", "needs_key": True, "needs_base_url": False, "enabled": False, "models": ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-2.5-flash"]},
    {"id": "deepseek", "label": "DeepSeek (API)", "tier": "byok", "needs_key": True, "needs_base_url": False, "enabled": False, "models": ["deepseek-v4-flash", "deepseek-v4-pro"]},
    {"id": "kimi", "label": "Kimi (Moonshot)", "tier": "byok", "needs_key": True, "needs_base_url": False, "enabled": False, "models": ["kimi-k2.6", "kimi-k3"]},
]

DEFAULT_LOCAL_MODEL = "qwen3:4b"

IMAGE_PROVIDERS = [
    {"id": "none", "label": "Sin imágenes", "tier": "free", "needs_key": False, "needs_base_url": False, "enabled": True, "models": []},
    {"id": "pollinations", "label": "Pollinations (gratis, sin clave)", "tier": "free", "needs_key": False, "needs_base_url": False, "enabled": True, "models": ["flux", "turbo"]},
    {"id": "huggingface", "label": "HuggingFace (gratis con token)", "tier": "free", "needs_key": True, "needs_base_url": False, "enabled": True, "models": ["black-forest-labs/FLUX.1-schnell", "stabilityai/stable-diffusion-xl-base-1.0"]},
    {"id": "local_sdxl", "label": "SDXL local (Automatic1111)", "tier": "free", "needs_key": False, "needs_base_url": True, "enabled": True, "models": []},
    {"id": "openai", "label": "OpenAI (imagen)", "tier": "byok", "needs_key": True, "needs_base_url": False, "enabled": True, "models": ["gpt-image-1-mini", "gpt-image-1.5", "gpt-image-2"]},
    {"id": "gemini", "label": "Gemini (imagen)", "tier": "byok", "needs_key": True, "needs_base_url": False, "enabled": True, "models": ["gemini-3.1-flash-image", "gemini-3-pro-image"]},
]


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


# Prefijo con el que empieza la clave de cada proveedor. Sirve para avisar al
# adulto cuando pega algo que no es una clave: sin esto, el proveedor devuelve
# 401, el `except` lo absorbe y el niño recibe lecciones del stub mientras la
# familia cree estar usando la IA que configuró.
#
# Es una comprobación de FORMA, no de validez: no dice si la clave funciona, solo
# descarta lo que no puede funcionar. Un proveedor sin entrada aquí no se valida.
KEY_PREFIXES = {
    "openai": "sk-",
    "claude": "sk-ant-",
    "gemini": "AIza",
    "deepseek": "sk-",
    "kimi": "sk-",
    "huggingface": "hf_",
}


def _label(provider: str) -> str:
    """Nombre legible del proveedor; el id interno no es para enseñárselo a nadie."""
    for grupo in (PROVIDERS, IMAGE_PROVIDERS):
        for p in grupo:
            if p["id"] == provider:
                return p["label"].split(" (")[0]
    return provider


def check_key_shape(provider: str, api_key: str) -> None:
    """Lanza ValueError si la clave no tiene la forma del proveedor."""
    prefijo = KEY_PREFIXES.get(provider)
    if prefijo and not api_key.startswith(prefijo):
        raise ValueError(
            f"Esa no parece una clave de {_label(provider)}: las suyas empiezan por «{prefijo}». "
            "Revisa que la hayas copiado entera y del sitio correcto."
        )
