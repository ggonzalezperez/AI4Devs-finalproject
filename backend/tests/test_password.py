"""Tests for change-password and recovery-code reset (Task PWD-a)."""
import re

RECOVERY_CODE_RE = re.compile(r"^([0-9A-F]{4}-){7}[0-9A-F]{4}$")  # 128 bits en 8 grupos


def _register(client, email="pwd_user@example.com", password="secret123"):
    r = client.post(
        "/auth/register",
        json={"name": "Familia Test", "email": email, "password": password},
    )
    assert r.status_code == 201
    body = r.json()
    return body["access_token"], body["recovery_code"]


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Register returns recovery_code in correct format
# ---------------------------------------------------------------------------

def test_register_returns_recovery_code(client):
    token, code = _register(client, email="rc_format@example.com")
    assert token
    assert RECOVERY_CODE_RE.match(code), f"Formato inválido: {code!r}"


# ---------------------------------------------------------------------------
# change-password (logged in)
# ---------------------------------------------------------------------------

def test_change_password_wrong_current(client):
    token, _ = _register(client, email="chg_wrong@example.com")
    r = client.post(
        "/auth/change-password",
        json={"current_password": "WRONGPASSWORD", "new_password": "newpass99"},
        headers=_auth_header(token),
    )
    assert r.status_code == 400


def test_change_password_correct(client):
    email = "chg_ok@example.com"
    old_pw = "secret123"
    new_pw = "newpassword99"
    token, _ = _register(client, email=email, password=old_pw)

    r = client.post(
        "/auth/change-password",
        json={"current_password": old_pw, "new_password": new_pw},
        headers=_auth_header(token),
    )
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

    # Login with new password works
    ok = client.post("/auth/login", json={"email": email, "password": new_pw})
    assert ok.status_code == 200
    assert ok.json()["access_token"]

    # Login with old password fails
    bad = client.post("/auth/login", json={"email": email, "password": old_pw})
    assert bad.status_code == 401


def test_change_password_requires_auth(client):
    r = client.post(
        "/auth/change-password",
        json={"current_password": "secret123", "new_password": "newpass99"},
    )
    assert r.status_code == 401


# ---------------------------------------------------------------------------
# reset-password (email-free recovery code)
# ---------------------------------------------------------------------------

def test_reset_password_correct_code(client):
    email = "reset_ok@example.com"
    old_pw = "secret123"
    new_pw = "resetpassword99"
    _, old_code = _register(client, email=email, password=old_pw)

    r = client.post(
        "/auth/reset-password",
        json={"email": email, "recovery_code": old_code, "new_password": new_pw},
    )
    assert r.status_code == 200
    body = r.json()
    new_code = body["recovery_code"]
    assert RECOVERY_CODE_RE.match(new_code), f"Formato inválido: {new_code!r}"
    # New code must differ from old
    assert new_code != old_code


def test_reset_password_old_password_rejected_new_accepted(client):
    email = "reset_login@example.com"
    old_pw = "secret123"
    new_pw = "resetpassword99"
    _, old_code = _register(client, email=email, password=old_pw)

    client.post(
        "/auth/reset-password",
        json={"email": email, "recovery_code": old_code, "new_password": new_pw},
    )

    # Old password no longer works
    bad = client.post("/auth/login", json={"email": email, "password": old_pw})
    assert bad.status_code == 401

    # New password works
    ok = client.post("/auth/login", json={"email": email, "password": new_pw})
    assert ok.status_code == 200


def test_reset_password_code_is_rotated(client):
    """After a reset, the old recovery code must NOT work again."""
    email = "reset_rotate@example.com"
    _, old_code = _register(client, email=email, password="secret123")

    # First reset: should succeed
    r1 = client.post(
        "/auth/reset-password",
        json={"email": email, "recovery_code": old_code, "new_password": "newpass99a"},
    )
    assert r1.status_code == 200

    # Second reset with OLD code: must fail (code was rotated)
    r2 = client.post(
        "/auth/reset-password",
        json={"email": email, "recovery_code": old_code, "new_password": "newpass99b"},
    )
    assert r2.status_code == 400


def test_reset_password_wrong_code(client):
    email = "reset_badcode@example.com"
    _register(client, email=email, password="secret123")

    r = client.post(
        "/auth/reset-password",
        json={"email": email, "recovery_code": "0000-0000", "new_password": "newpass99"},
    )
    assert r.status_code == 400


def test_reset_password_nonexistent_email(client):
    r = client.post(
        "/auth/reset-password",
        json={"email": "nobody@example.com", "recovery_code": "ABCD-1234", "new_password": "newpass99"},
    )
    assert r.status_code == 400


def test_verify_password_confirms_the_adult_is_present(client):
    """Salir de la sesión del niño exige la contraseña de la familia.

    El token de familia sigue en el dispositivo mientras juega el niño, así que
    no basta con tenerlo: hay que demostrar que quien pulsa es el adulto.
    """
    r = client.post(
        "/auth/register",
        json={"name": "F", "email": "salir@example.com", "password": "secret123"},
    )
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}

    ok = client.post("/auth/verify-password", headers=h, json={"password": "secret123"})
    assert ok.status_code == 200 and ok.json()["status"] == "ok"

    mal = client.post("/auth/verify-password", headers=h, json={"password": "loquesea"})
    assert mal.status_code == 401

    sin_token = client.post("/auth/verify-password", json={"password": "secret123"})
    assert sin_token.status_code == 401
