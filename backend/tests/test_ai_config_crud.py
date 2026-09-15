from app.config import get_settings
from app.services.crypto import generate_key


def _auth(client):
    r = client.post(
        "/auth/register",
        json={"name": "F", "email": "crud@example.com", "password": "secret123"},
    )
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_default_config_is_free_stub(client):
    body = client.get("/family/ai-config", headers=_auth(client)).json()
    assert body["tier"] == "free"
    assert body["provider"] == "stub"
    assert body["has_api_key"] is False


def test_put_byok_claude_stores_key_without_returning_it(client):
    get_settings().ai_config_key = generate_key()  # clave maestra de prueba
    h = _auth(client)
    r = client.put(
        "/family/ai-config",
        headers=h,
        json={"tier": "byok", "provider": "claude", "model": "claude-haiku-4-5", "api_key": "sk-ant-test"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["provider"] == "claude"
    assert body["has_api_key"] is True
    assert "api_key" not in body and "api_key_encrypted" not in body


def test_put_rejects_disabled_provider(client):
    h = _auth(client)
    r = client.put(
        "/family/ai-config",
        headers=h,
        json={"tier": "byok", "provider": "deepseek", "model": "deepseek-chat"},
    )
    assert r.status_code == 422


def test_get_requires_auth(client):
    assert client.get("/family/ai-config").status_code == 401


def test_put_rejects_key_that_is_not_shaped_like_the_providers(client):
    """Guardar una clave con forma imposible no debe quedarse en silencio.

    Caso real (15-09-2026): se guardó una cadena de 156 caracteres como clave de
    OpenAI. La app la aceptó, el proveedor devolvió 401, el `except` lo absorbió
    y el niño recibió lecciones del stub. La familia creía estar usando OpenAI.
    """
    h = _auth(client)
    r = client.put(
        "/family/ai-config",
        headers=h,
        json={"tier": "byok", "provider": "openai", "model": "gpt-5.6-luna", "api_key": "0FrC3cyu" + "x" * 148},
    )
    assert r.status_code == 422
    assert "sk-" in r.json()["detail"]


def test_put_accepts_a_well_shaped_key(client):
    h = _auth(client)
    r = client.put(
        "/family/ai-config",
        headers=h,
        json={"tier": "byok", "provider": "openai", "model": "gpt-5.6-luna", "api_key": "sk-proj-" + "x" * 40},
    )
    assert r.status_code == 200
    assert r.json()["has_api_key"] is True
