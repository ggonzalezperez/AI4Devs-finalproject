"""Código de invitación en el alta de familia.

La demo pública vive en internet: sin esto, cualquiera que llegue a la URL puede
crear una familia. La regla vive en el servidor, no en el esquema, porque el
campo debe seguir siendo opcional para quien despliega Chispa en su casa.
"""

import pytest

from app.config import Settings, get_settings
from app.models.family import User


@pytest.fixture
def invite_code(monkeypatch):
    """Configura el código de invitación en los ajustes vivos de la app."""

    def _set(code: str | None) -> None:
        monkeypatch.setattr(get_settings(), "invite_code", code)

    return _set


def _payload(**extra) -> dict:
    return {"name": "Familia García", "email": "p@example.com", "password": "secret123", **extra}


def test_settings_invite_code_defaults_to_none():
    assert Settings().invite_code is None


def test_register_rejects_a_wrong_invite_code(client, invite_code):
    invite_code("palabra-secreta")
    assert client.post("/auth/register", json=_payload(invite_code="otra-cosa")).status_code == 403


def test_register_is_open_when_no_invite_code_is_configured(client, invite_code):
    # Contrato que mantiene verde la suite existente y el despliegue casero.
    invite_code(None)
    assert client.post("/auth/register", json=_payload()).status_code == 201


def test_register_accepts_the_correct_invite_code(client, invite_code):
    invite_code("palabra-secreta")
    r = client.post("/auth/register", json=_payload(invite_code="palabra-secreta"))
    assert r.status_code == 201
    assert r.json()["recovery_code"]


def test_register_rejects_a_missing_invite_code(client, invite_code):
    invite_code("palabra-secreta")
    # 403 y no 422: el campo es opcional en el esquema, la regla es del servidor.
    assert client.post("/auth/register", json=_payload()).status_code == 403


def test_a_rejected_invite_code_creates_no_user(client, invite_code, db_session):
    invite_code("palabra-secreta")
    client.post("/auth/register", json=_payload(invite_code="otra-cosa"))
    # La comprobación va antes de tocar la base de datos.
    assert db_session.query(User).count() == 0


def test_register_ignores_surrounding_whitespace_in_the_invite_code(client, invite_code):
    # El código se copia y pega desde un email: arrastra espacios.
    invite_code("palabra-secreta")
    r = client.post("/auth/register", json=_payload(invite_code="  palabra-secreta  "))
    assert r.status_code == 201


def test_invite_code_error_does_not_reveal_the_expected_value(client, invite_code):
    # La pantalla de alta pinta el detalle del servidor tal cual.
    invite_code("palabra-secreta")
    r = client.post("/auth/register", json=_payload(invite_code="otra-cosa"))
    assert "palabra-secreta" not in r.text
