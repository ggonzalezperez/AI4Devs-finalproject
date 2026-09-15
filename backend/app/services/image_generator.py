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


def build_avatar_prompt(description: str) -> str:
    return (
        f"Avatar de perfil de {description}. Ilustración infantil colorida y simpática, "
        "primer plano, fondo liso, sin texto. Apto y seguro para niños."
    )


def build_image_prompt(concept: str, age: int) -> str:
    if age <= 8:
        style = "ilustración infantil colorida tipo dibujo animado, amable y sencilla, sin texto"
    else:
        style = "ilustración educativa realista y detallada, apropiada para niños, sin texto"
    return f"{concept}. {style}. Contenido seguro y apto para niños."
