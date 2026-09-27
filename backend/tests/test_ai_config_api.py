from app.config import get_settings
from app.services.crypto import generate_key


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


# ---------------------------------------------------------------------------
# Image config tests (IMG-2a)
# ---------------------------------------------------------------------------

def test_default_config_has_image_defaults(client):
    """GET /family/ai-config returns image defaults: provider=none, enabled=False, no key."""
    body = client.get("/family/ai-config", headers=_auth(client)).json()
    assert body["image_provider"] == "none"
    assert body["image_enabled"] is False
    assert body["has_image_api_key"] is False


def test_put_image_config_round_trip(client):
    """PUT with image fields stores them; GET reflects them; key never returned in plaintext."""
    get_settings().ai_config_key = generate_key()
    h = _auth(client)
    r = client.put(
        "/family/ai-config",
        headers=h,
        json={
            "tier": "free",
            "provider": "stub",
            "image_provider": "huggingface",
            "image_enabled": True,
            "image_api_key": "hf_test",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["image_provider"] == "huggingface"
    assert body["image_enabled"] is True
    assert body["has_image_api_key"] is True
    assert "image_api_key" not in body
    assert "image_api_key_encrypted" not in body

    # Verify GET also reflects the stored values
    get_body = client.get("/family/ai-config", headers=h).json()
    assert get_body["image_provider"] == "huggingface"
    assert get_body["image_enabled"] is True
    assert get_body["has_image_api_key"] is True


def test_put_empty_image_api_key_clears_it(client):
    """Sending image_api_key='' should clear any stored key."""
    get_settings().ai_config_key = generate_key()
    h = _auth(client)
    # First, store a key
    client.put(
        "/family/ai-config",
        headers=h,
        json={"tier": "free", "provider": "stub", "image_provider": "huggingface",
              "image_enabled": True, "image_api_key": "hf_test"},
    )
    # Now clear it
    r = client.put(
        "/family/ai-config",
        headers=h,
        json={"tier": "free", "provider": "stub", "image_provider": "huggingface",
              "image_enabled": True, "image_api_key": ""},
    )
    assert r.status_code == 200
    assert r.json()["has_image_api_key"] is False


def test_catalog_includes_image_providers(client):
    """GET /family/ai-config/catalog exposes image_providers with 'huggingface' entry."""
    body = client.get("/family/ai-config/catalog", headers=_auth(client)).json()
    assert "image_providers" in body
    ids = [p["id"] for p in body["image_providers"]]
    assert len(ids) > 0
    assert "huggingface" in ids


def test_put_rejects_an_unknown_image_provider(client):
    """Un proveedor de imagen inventado se guardaba con 200 y no generaba nada.

    El proveedor de texto sí se valida contra el catálogo; el de imagen no, así que
    `build_image_generator` no lo reconocía y devolvía el stub. Resultado: la familia
    creía tener ilustraciones y las lecciones salían sin imagen, sin ningún aviso.
    RF-IA-06 declara la lista cerrada como regla de negocio.
    """
    h = _auth(client)
    r = client.put(
        "/family/ai-config",
        headers=h,
        json={
            "tier": "free",
            "provider": "stub",
            "image_provider": "midjourney",
            "image_enabled": True,
        },
    )
    assert r.status_code == 422
    assert "imagen" in r.json()["detail"].lower()
    # Y el rechazo no deja escrito a medias: sigue en el valor por defecto.
    assert client.get("/family/ai-config", headers=h).json()["image_provider"] == "none"


def test_put_accepts_every_image_provider_in_the_catalog(client):
    """La validación nueva no puede dejar fuera a ninguno de los del catálogo.

    Si el catálogo y la validación se separan, el panel ofrece en su desplegable
    proveedores que el servidor rechaza con 422: el fallo opuesto, igual de tonto.
    """
    h = _auth(client)
    catalog = client.get("/family/ai-config/catalog", headers=h).json()
    ofrecidos = [p for p in catalog["image_providers"] if p["enabled"]]
    assert ofrecidos, "el catálogo de imagen no ofrece ningún proveedor"
    for provider in ofrecidos:
        r = client.put(
            "/family/ai-config",
            headers=h,
            json={
                "tier": "free",
                "provider": "stub",
                "image_provider": provider["id"],
                "image_enabled": False,
            },
        )
        assert r.status_code == 200, f"el catálogo ofrece {provider['id']} y el servidor lo rechaza"
        assert r.json()["image_provider"] == provider["id"]
