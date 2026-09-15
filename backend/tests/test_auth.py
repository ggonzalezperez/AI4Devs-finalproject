def test_register_returns_token(client):
    r = client.post(
        "/auth/register",
        json={"name": "Familia García", "email": "p@example.com", "password": "secret123"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_register_duplicate_email_rejected(client):
    payload = {"name": "F", "email": "dup@example.com", "password": "secret123"}
    assert client.post("/auth/register", json=payload).status_code == 201
    assert client.post("/auth/register", json=payload).status_code == 409


def test_login_ok_and_wrong_password(client):
    client.post(
        "/auth/register",
        json={"name": "F", "email": "l@example.com", "password": "secret123"},
    )
    ok = client.post("/auth/login", json={"email": "l@example.com", "password": "secret123"})
    assert ok.status_code == 200
    assert ok.json()["access_token"]

    bad = client.post("/auth/login", json={"email": "l@example.com", "password": "wrong"})
    assert bad.status_code == 401
