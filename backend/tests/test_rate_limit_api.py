"""Límite de intentos aplicado a los endpoints de credenciales."""

from app.config import get_settings


def _register(client, email="ana@x.com", password="secret123"):
    return client.post(
        "/auth/register", json={"name": "F", "email": email, "password": password}
    )


def test_login_returns_429_after_too_many_attempts_from_the_same_ip(client):
    _register(client)
    for _ in range(10):
        client.post("/auth/login", json={"email": "ana@x.com", "password": "mala"})
    r = client.post("/auth/login", json={"email": "ana@x.com", "password": "mala"})
    assert r.status_code == 429


def test_the_login_limit_also_applies_per_account_across_different_ips(client, monkeypatch):
    # Un atacante que rote IPs esquivaría el cubo por IP; el email no se puede
    # falsificar porque no viaja en una cabecera, sino en el cuerpo.
    monkeypatch.setattr(get_settings(), "client_ip_header", "CF-Connecting-IP")
    _register(client)
    for i in range(5):
        client.post(
            "/auth/login",
            json={"email": "ana@x.com", "password": "mala"},
            headers={"CF-Connecting-IP": f"9.9.9.{i}"},
        )
    r = client.post(
        "/auth/login",
        json={"email": "ana@x.com", "password": "mala"},
        headers={"CF-Connecting-IP": "9.9.9.200"},
    )
    assert r.status_code == 429


def test_the_429_response_includes_a_retry_after_header(client):
    _register(client)
    for _ in range(11):
        r = client.post("/auth/login", json={"email": "ana@x.com", "password": "mala"})
    assert r.status_code == 429
    assert int(r.headers["Retry-After"]) > 0


def test_a_successful_login_clears_the_account_counter(client):
    # Una familia con varios dispositivos no debe autobloquearse: credenciales
    # demostradas válidas no son fuerza bruta.
    _register(client)
    for _ in range(4):
        client.post("/auth/login", json={"email": "ana@x.com", "password": "mala"})
    assert (
        client.post(
            "/auth/login", json={"email": "ana@x.com", "password": "secret123"}
        ).status_code
        == 200
    )
    # El cubo de la cuenta se olvidó: quedan intentos otra vez.
    assert (
        client.post("/auth/login", json={"email": "ana@x.com", "password": "mala"}).status_code
        == 401
    )


def test_a_malformed_json_body_still_returns_422(client):
    # Regresión del punto frágil: el limitador lee el cuerpo antes que Pydantic.
    # Si dejara de estar cacheado, el endpoint vería un cuerpo vacío y todo
    # empezaría a dar 422 aunque la petición fuese correcta.
    r = client.post(
        "/auth/login", content=b"{esto no es json", headers={"content-type": "application/json"}
    )
    assert r.status_code == 422


def test_register_is_limited_per_ip(client):
    for i in range(5):
        _register(client, email=f"a{i}@x.com")
    assert _register(client, email="otro@x.com").status_code == 429


def test_reset_password_is_limited_per_account(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "client_ip_header", "CF-Connecting-IP")
    _register(client)
    cuerpo = {"email": "ana@x.com", "recovery_code": "MAL", "new_password": "otra-larga-1"}
    for i in range(5):
        client.post("/auth/reset-password", json=cuerpo, headers={"CF-Connecting-IP": f"8.8.8.{i}"})
    r = client.post(
        "/auth/reset-password", json=cuerpo, headers={"CF-Connecting-IP": "8.8.8.200"}
    )
    assert r.status_code == 429


def test_verify_password_is_limited_per_authenticated_user(client):
    # Es la puerta que impide que el niño salga solo de su sesión probando
    # contraseñas mientras tiene el dispositivo en la mano.
    token = _register(client).json()["access_token"]
    cabeceras = {"Authorization": f"Bearer {token}"}
    for _ in range(10):
        r = client.post("/auth/verify-password", json={"password": "mala"}, headers=cabeceras)
    r = client.post("/auth/verify-password", json={"password": "mala"}, headers=cabeceras)
    assert r.status_code == 429


def _crear_nino(client, cabeceras, nombre, pin):
    return client.post(
        "/children",
        json={"name": nombre, "birthdate": "2019-05-05", "pin": pin},
        headers=cabeceras,
    ).json()["id"]


def test_child_pin_login_is_limited_per_child(client):
    token = _register(client).json()["access_token"]
    cabeceras = {"Authorization": f"Bearer {token}"}
    child_id = _crear_nino(client, cabeceras, "Leo", "1234")
    for _ in range(20):
        client.post(f"/children/{child_id}/login", json={"pin": "0000"}, headers=cabeceras)
    r = client.post(f"/children/{child_id}/login", json={"pin": "0000"}, headers=cabeceras)
    assert r.status_code == 429


def test_another_child_keeps_its_own_counter(client, monkeypatch):
    # Un hermano que agota sus intentos no puede dejar fuera al otro.
    monkeypatch.setattr(get_settings(), "client_ip_header", "CF-Connecting-IP")
    token = _register(client).json()["access_token"]
    cabeceras = {"Authorization": f"Bearer {token}", "CF-Connecting-IP": "7.7.7.7"}
    uno = _crear_nino(client, cabeceras, "Leo", "1234")
    otro = _crear_nino(client, cabeceras, "Mar", "4321")
    for i in range(10):
        client.post(
            f"/children/{uno}/login",
            json={"pin": "0000"},
            headers={**cabeceras, "CF-Connecting-IP": f"7.7.7.{i}"},
        )
    r = client.post(
        f"/children/{otro}/login",
        json={"pin": "4321"},
        headers={**cabeceras, "CF-Connecting-IP": "7.7.7.99"},
    )
    assert r.status_code == 200


def test_requests_pass_through_when_the_limiter_is_disabled(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "rate_limit_enabled", False)
    _register(client)
    for _ in range(15):
        r = client.post("/auth/login", json={"email": "ana@x.com", "password": "mala"})
    assert r.status_code == 401


def test_the_limit_message_does_not_reveal_whether_the_account_exists(client):
    # Coherente con el hash señuelo de auth_service: nada distingue una cuenta
    # existente de una inventada.
    for _ in range(11):
        r = client.post("/auth/login", json={"email": "nadie@x.com", "password": "mala"})
    assert r.status_code == 429
    detalle = r.json()["detail"].lower()
    assert "nadie@x.com" not in detalle
    assert "existe" not in detalle
