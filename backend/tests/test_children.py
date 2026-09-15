def _auth_headers(client):
    r = client.post(
        "/auth/register",
        json={"name": "F", "email": "c@example.com", "password": "secret123"},
    )
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_create_and_list_children(client):
    headers = _auth_headers(client)
    created = client.post(
        "/children",
        headers=headers,
        json={"name": "Lucía", "birthdate": "2018-01-01", "pin": "1234"},
    )
    assert created.status_code == 201
    body = created.json()
    assert body["name"] == "Lucía"
    assert body["age"] >= 6
    assert "pin" not in body and "pin_hash" not in body

    listed = client.get("/children", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_child_pin_login(client):
    headers = _auth_headers(client)
    child = client.post(
        "/children",
        headers=headers,
        json={"name": "Lucía", "birthdate": "2018-01-01", "pin": "1234"},
    ).json()

    ok = client.post(f"/children/{child['id']}/login", headers=headers, json={"pin": "1234"})
    assert ok.status_code == 200
    assert ok.json()["access_token"]

    bad = client.post(f"/children/{child['id']}/login", headers=headers, json={"pin": "0000"})
    assert bad.status_code == 401


def test_list_children_requires_auth(client):
    assert client.get("/children").status_code == 401


def test_child_default_avatar(client):
    headers = _auth_headers(client)
    r = client.post(
        "/children",
        headers=headers,
        json={"name": "Sofía", "birthdate": "2019-03-15", "pin": "5678"},
    )
    assert r.status_code == 201
    assert r.json()["avatar"] == "fox"


def test_child_custom_avatar(client):
    headers = _auth_headers(client)
    r = client.post(
        "/children",
        headers=headers,
        json={"name": "Pedro", "birthdate": "2017-07-20", "pin": "4321", "avatar": "rocket"},
    )
    assert r.status_code == 201
    assert r.json()["avatar"] == "rocket"


def test_create_child_rejects_pin_that_is_not_four_digits(client):
    r"""RF-ONB-03 exige ^\d{4}$. La regla vivía solo en el frontend."""
    headers = _auth_headers(client)
    for bad_pin in ["123", "12345", "abcd", "12a4", ""]:
        r = client.post(
            "/children",
            headers=headers,
            json={"name": "Lucía", "birthdate": "2018-01-01", "pin": bad_pin},
        )
        assert r.status_code == 422, f"PIN {bad_pin!r} debería rechazarse"
