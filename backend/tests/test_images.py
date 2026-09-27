"""Tests for image generation seam (Task IMG-1)."""
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from app.models.child import Child
from app.models.family import Family
from app.security import create_token
from app.services.image_generator import (
    GeneratedImage,
    StubImageGenerator,
    build_image_prompt,
)
from app.services.image_providers import build_image_generator
from app.services.lesson_service import _attach_image

# ---------------------------------------------------------------------------
# Unit tests: StubImageGenerator
# ---------------------------------------------------------------------------

def test_stub_returns_none():
    assert StubImageGenerator().generate("any prompt") is None


# ---------------------------------------------------------------------------
# Unit tests: build_image_generator → StubImageGenerator when disabled
# ---------------------------------------------------------------------------

def test_build_image_generator_none_config():
    gen = build_image_generator(None)
    assert isinstance(gen, StubImageGenerator)


def test_build_image_generator_disabled():
    cfg = SimpleNamespace(image_enabled=False, image_provider="huggingface", image_model=None)
    gen = build_image_generator(cfg)
    assert isinstance(gen, StubImageGenerator)


# ---------------------------------------------------------------------------
# Unit tests: build_image_prompt
# ---------------------------------------------------------------------------

def test_build_image_prompt_young_child():
    prompt = build_image_prompt("volcanes", 5)
    assert "dibujo" in prompt


def test_build_image_prompt_older_child():
    prompt = build_image_prompt("volcanes", 11)
    assert "realista" in prompt


# ---------------------------------------------------------------------------
# Integration test: _attach_image writes file when generator returns data
# ---------------------------------------------------------------------------

def test_attach_image_writes_file_and_sets_url(tmp_path, db_session):
    """_attach_image with a fake generator that returns bytes should write the file
    and set lesson.image_url to /media/lessons/{id}.png."""

    class FakeGenerator:
        def generate(self, prompt: str) -> GeneratedImage:
            return GeneratedImage(data=b"PNGBYTES")

    # Create a minimal lesson object in the DB so it has an id.
    fam = Family(name="TestFam")
    db_session.add(fam)
    db_session.flush()
    child = Child(family_id=fam.id, name="Teo", birthdate=date(2017, 6, 1), pin_hash="h")
    db_session.add(child)
    db_session.flush()

    from app.models.lesson import Lesson
    lesson = Lesson(
        child_id=child.id,
        curiosity="¿qué son los volcanes?",
        subject="ciencias",
        concept="volcanes",
        title="Volcanes",
        body="Un volcán es...",
        fun_fact="El Etna...",
        quiz_question="¿Qué es un volcán?",
        quiz_options=["A", "B", "C"],
        quiz_correct_index=1,
        quiz_explanation="Explicación",
        follow_ups=[],
    )
    db_session.add(lesson)
    db_session.commit()

    # Patch both build_image_generator (to return our fake) and get_settings (to use tmp_path)
    fake_cfg = SimpleNamespace(image_enabled=True, image_provider="huggingface",
                               image_model=None, image_api_key_encrypted=None,
                               image_base_url=None)

    with patch("app.services.lesson_service.build_image_generator", return_value=FakeGenerator()):
        with patch("app.services.lesson_service.get_settings") as mock_settings:
            mock_settings.return_value.media_dir = str(tmp_path)
            _attach_image(db_session, fake_cfg, lesson, age=child.age)

    # File should exist
    expected_file = tmp_path / "lessons" / f"{lesson.id}.png"
    assert expected_file.exists(), f"Expected image file at {expected_file}"
    assert expected_file.read_bytes() == b"PNGBYTES"

    # lesson.image_url should be set
    assert lesson.image_url == f"/media/lessons/{lesson.id}.png"


# ---------------------------------------------------------------------------
# Integration test: _attach_image swallows exceptions (best-effort)
# ---------------------------------------------------------------------------

def test_attach_image_swallows_generator_exception(tmp_path, db_session):
    """If the generator raises, image_url must remain None (no lesson crash)."""

    class BoomGenerator:
        def generate(self, prompt: str) -> GeneratedImage | None:
            raise RuntimeError("network error")

    fam = Family(name="TestFam2")
    db_session.add(fam)
    db_session.flush()
    child = Child(family_id=fam.id, name="Sol", birthdate=date(2018, 1, 1), pin_hash="h")
    db_session.add(child)
    db_session.flush()

    from app.models.lesson import Lesson
    lesson = Lesson(
        child_id=child.id,
        curiosity="¿por qué brilla el sol?",
        subject="ciencias",
        concept="sol",
        title="El Sol",
        body="El sol es...",
        fun_fact="El sol tiene...",
        quiz_question="¿Qué es el sol?",
        quiz_options=["A", "B", "C"],
        quiz_correct_index=0,
        quiz_explanation="Explicación",
        follow_ups=[],
    )
    db_session.add(lesson)
    db_session.commit()

    fake_cfg = SimpleNamespace(image_enabled=True, image_provider="huggingface",
                               image_model=None, image_api_key_encrypted=None,
                               image_base_url=None)

    # Should not raise
    with patch("app.services.lesson_service.build_image_generator", return_value=BoomGenerator()):
        with patch("app.services.lesson_service.get_settings") as mock_settings:
            mock_settings.return_value.media_dir = str(tmp_path)
            _attach_image(db_session, fake_cfg, lesson, age=child.age)

    assert lesson.image_url is None


# ---------------------------------------------------------------------------
# API test: default lesson has image_url == None
# ---------------------------------------------------------------------------

def _child_token(db_session):
    fam = Family(name="FamImg")
    db_session.add(fam)
    db_session.flush()
    child = Child(family_id=fam.id, name="Leo", birthdate=date(2018, 1, 1), pin_hash="x")
    db_session.add(child)
    db_session.commit()
    return create_token(subject=str(child.id), token_type="child")


def test_default_lesson_has_no_image(client, db_session):
    """With default config (image_enabled=False), lesson.image_url must be None."""
    token = _child_token(db_session)
    r = client.post(
        "/lessons",
        headers={"Authorization": f"Bearer {token}"},
        json={"curiosity": "¿por qué el cielo es azul?"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body.get("image_url") is None


# --- Seguridad: mitigación SSRF en el endpoint SDXL local ---
from app.services.image_providers import validate_local_url  # noqa: E402


def test_validate_local_url_allows_localhost_and_lan():
    assert validate_local_url("http://localhost:7860") == "http://localhost:7860"
    assert validate_local_url("http://192.168.1.50:7860").startswith("http://192.168")


def test_validate_local_url_blocks_metadata_and_non_http():
    with pytest.raises(ValueError):
        validate_local_url("http://169.254.169.254/latest/meta-data")
    with pytest.raises(ValueError):
        validate_local_url("file:///etc/passwd")


class _Cfg:
    image_enabled = True
    image_provider = "local_sdxl"
    image_model = None
    image_api_key_encrypted = None

    def __init__(self, base_url):
        self.image_base_url = base_url


def test_build_image_generator_rejects_metadata_url_falls_back_to_stub():
    gen = build_image_generator(_Cfg("http://169.254.169.254"))
    assert isinstance(gen, StubImageGenerator)


def test_build_image_generator_pollinations_needs_no_key():
    from app.services.image_providers import (
        PollinationsImageGenerator,
        build_image_generator,
    )

    class Cfg:
        image_enabled = True
        image_provider = "pollinations"
        image_model = None
        image_base_url = None
        image_api_key_encrypted = None

    assert isinstance(build_image_generator(Cfg()), PollinationsImageGenerator)


def test_openai_asks_for_a_compressed_webp_instead_of_a_full_png():
    """Una ilustración en PNG a máxima calidad ocupa 2-3 MB.

    Eso son megas por lección viajando al móvil del niño, y el modelo devuelve
    PNG si no se le pide otra cosa. WebP comprimido baja a cientos de kilobytes
    sin diferencia visible en pantalla.
    """
    import base64 as _b64

    from app.services.image_providers import OpenAIImageGenerator

    capturado = {}

    class _Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"data": [{"b64_json": _b64.b64encode(b"datos").decode()}]}

    def _post(url, **kwargs):
        capturado.update(kwargs.get("json", {}))
        return _Resp()

    with patch("app.services.image_providers.httpx.post", _post):
        img = OpenAIImageGenerator(api_key="sk-x", model="gpt-image-1-mini").generate("un pulpo")

    assert capturado["output_format"] == "webp"
    assert 60 <= capturado["output_compression"] <= 90
    assert capturado["quality"] == "medium"
    assert img.mime == "image/webp"


def test_openai_without_b64_json_returns_none_instead_of_exploding():
    """Era la única lectura del módulo que indexaba a ciegas.

    `resp.json()["data"][0]["b64_json"]` lanza KeyError o IndexError si el proveedor
    responde 200 con otra forma —una `url`, o `data` vacío—. El best-effort del
    lesson_service lo absorbería, pero absorbiendo también el motivo: devolver None
    es el contrato de ImageGenerator y es lo que ya hacen los adaptadores de Gemini
    y de SDXL local.
    """
    from app.services.image_providers import OpenAIImageGenerator

    class _Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"data": [{"url": "https://example.invalid/imagen.png"}]}

    with patch("app.services.image_providers.httpx.post", lambda url, **kw: _Resp()):
        assert OpenAIImageGenerator(api_key="sk-x", model="gpt-image-1-mini").generate("x") is None


def test_openai_does_not_send_response_format():
    """Centinela de una corrección que sería un error.

    El libro mayor arrastraba «falta response_format=b64_json» como deuda menor.
    Es al contrario: el parámetro existe solo para dall-e-2 y dall-e-3; la familia
    gpt-image-* lo rechaza con «Unknown parameter» y ya devuelve b64_json de serie.
    Añadirlo rompería un adaptador que funciona, y el 400 lo absorbería el
    best-effort sin que nadie viese la causa. Este test se pone rojo si reaparece.
    """
    import base64 as _b64

    from app.services.image_providers import OpenAIImageGenerator

    capturado = {}

    class _Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"data": [{"b64_json": _b64.b64encode(b"datos").decode()}]}

    def _post(url, **kwargs):
        capturado.update(kwargs.get("json", {}))
        return _Resp()

    with patch("app.services.image_providers.httpx.post", _post):
        OpenAIImageGenerator(api_key="sk-x", model="gpt-image-1-mini").generate("un pulpo")

    assert "response_format" not in capturado, (
        "response_format solo vale para dall-e-*; gpt-image-* lo rechaza. "
        "Si el catálogo incorpora un dall-e-*, revisa también output_format, "
        "output_compression y quality, que dejan de estar soportados."
    )


def test_attach_image_saves_with_the_extension_of_its_real_format(tmp_path, db_session):
    """El fichero se guardaba siempre como .png, viniera lo que viniera.

    Con WebP eso deja un .png que no es un PNG: el navegador lo resuelve por el
    contenido, pero cualquier herramienta que mire la extensión se equivoca, y
    la caché de un año hace muy caro descubrirlo tarde.
    """
    from app.models.lesson import Lesson

    class WebpGenerator:
        def generate(self, prompt: str) -> GeneratedImage:
            return GeneratedImage(data=b"WEBPBYTES", mime="image/webp")

    fam = Family(name="F")
    db_session.add(fam)
    db_session.flush()
    child = Child(family_id=fam.id, name="Teo", birthdate=date(2017, 6, 1), pin_hash="h")
    db_session.add(child)
    db_session.flush()
    lesson = Lesson(
        child_id=child.id, curiosity="c", subject="ciencias", concept="c", title="t",
        body="b", fun_fact="f", quiz_question="q", quiz_options=["A"],
        quiz_correct_index=0, quiz_explanation="e", follow_ups=[],
    )
    db_session.add(lesson)
    db_session.commit()

    cfg = SimpleNamespace(image_enabled=True, image_provider="openai", image_model=None,
                          image_api_key_encrypted=None, image_base_url=None)
    with patch("app.services.lesson_service.build_image_generator", return_value=WebpGenerator()):
        with patch("app.services.lesson_service.get_settings") as ajustes:
            ajustes.return_value.media_dir = str(tmp_path)
            _attach_image(db_session, cfg, lesson, age=child.age)

    assert (tmp_path / "lessons" / f"{lesson.id}.webp").exists()
    assert lesson.image_url == f"/media/lessons/{lesson.id}.webp"


def test_the_app_registers_the_webp_mime_type():
    """El contenedor del backend no trae .webp en su tabla de tipos.

    Sin registrarlo, las ilustraciones se sirven como application/octet-stream:
    el navegador las deduce igual, pero un cliente estricto o una descarga
    guardarían un fichero sin tipo.
    """
    import mimetypes

    import app.main  # noqa: F401  (registrar el tipo es efecto de importar la app)

    assert mimetypes.guess_type("leccion.webp")[0] == "image/webp"
