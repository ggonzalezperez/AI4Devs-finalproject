"""Tests for Avatar-IA (Task AVATAR-IA)."""
from app.services.image_generator import build_avatar_prompt


def _auth_headers(client):
    r = client.post(
        "/auth/register",
        json={"name": "F", "email": "avatar@example.com", "password": "secret123"},
    )
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _create_child(client, headers):
    r = client.post(
        "/children",
        headers=headers,
        json={"name": "Luna", "birthdate": "2018-05-01", "pin": "4321"},
    )
    assert r.status_code == 201
    return r.json()


def test_build_avatar_prompt_contains_description():
    prompt = build_avatar_prompt("un zorro astronauta")
    assert "zorro astronauta" in prompt


def test_generate_avatar_disabled_returns_409(client):
    """With image generation disabled (default), endpoint returns 409."""
    headers = _auth_headers(client)
    child = _create_child(client, headers)
    r = client.post(
        f"/children/{child['id']}/avatar/generate",
        headers=headers,
        json={"description": "un zorro astronauta"},
    )
    assert r.status_code == 409
    assert "imágenes" in r.json()["detail"]


def test_generate_avatar_wrong_family_returns_404(client):
    """Child from another family must return 404."""
    # Create first family with a child
    h1 = _auth_headers(client)
    child = _create_child(client, h1)

    # Create second family
    r2 = client.post(
        "/auth/register",
        json={"name": "F2", "email": "other@example.com", "password": "secret123"},
    )
    h2 = {"Authorization": f"Bearer {r2.json()['access_token']}"}

    r = client.post(
        f"/children/{child['id']}/avatar/generate",
        headers=h2,
        json={"description": "un gato ninja"},
    )
    assert r.status_code == 404


def test_generate_avatar_provider_failure_is_not_reported_as_disabled(client, monkeypatch):
    """Un fallo del proveedor no debe decir «no está activada».

    Antes, cualquier motivo por el que no hubiera imagen (desactivada O el
    proveedor caído) devolvía el mismo 409 con el mismo mensaje, que mandaba al
    usuario a activar algo que ya tenía activado.
    """
    from app.routers import children as children_router

    headers = _auth_headers(client)
    child = _create_child(client, headers)

    # Imagen activada, con un proveedor que no necesita clave.
    cfg = client.put(
        "/family/ai-config",
        headers=headers,
        json={
            "tier": "free", "provider": "stub",
            "image_provider": "pollinations", "image_enabled": True,
        },
    )
    assert cfg.status_code == 200

    class _Roto:
        def generate(self, prompt):
            raise RuntimeError("proveedor caído")

    monkeypatch.setattr(children_router, "build_image_generator", lambda _cfg: _Roto())

    r = client.post(
        f"/children/{child['id']}/avatar/generate",
        headers=headers,
        json={"description": "un zorro astronauta"},
    )
    assert r.status_code == 502
    assert "no está activada" not in r.json()["detail"]
