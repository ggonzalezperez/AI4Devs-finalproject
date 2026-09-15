def _register(client):
    r = client.post(
        "/auth/register",
        json={"name": "F", "email": "me@example.com", "password": "secret123"},
    )
    return r.json()["access_token"]


def test_protected_route_requires_token(client):
    token = _register(client)
    ok = client.get("/children", headers={"Authorization": f"Bearer {token}"})
    assert ok.status_code == 200

    no_auth = client.get("/children")
    assert no_auth.status_code == 401
