"""Panel de familia (US5/US6, RF-PLT-01).

La familia lee el perfil y la ficha de conocimiento de SUS hijos. Los endpoints
`/me/*` no sirven: exigen token `child` por diseño (JWT tipado).
"""


def _family_headers(client, email="panel@example.com"):
    r = client.post(
        "/auth/register",
        json={"name": "F", "email": email, "password": "secret123"},
    )
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _create_child(client, headers, name="Nora", pin="1234"):
    r = client.post(
        "/children",
        headers=headers,
        json={"name": name, "birthdate": "2018-01-01", "pin": pin},
    )
    assert r.status_code == 201
    return r.json()


def test_family_reads_child_profile(client):
    headers = _family_headers(client)
    child = _create_child(client, headers)

    r = client.get(f"/children/{child['id']}/profile", headers=headers)

    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Nora"
    assert body["age"] >= 6
    assert body["islands"] == 0
    assert "pin_hash" not in body and "family_id" not in body


def _child_token(client, family_headers, child_id, pin="1234"):
    r = client.post(f"/children/{child_id}/login", headers=family_headers, json={"pin": pin})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_family_reads_child_knowledge(client):
    headers = _family_headers(client)
    child = _create_child(client, headers)
    # El niño explora algo para que exista una isla.
    child_headers = _child_token(client, headers, child["id"])
    assert client.post(
        "/lessons", headers=child_headers, json={"curiosity": "¿por qué llueve?"}
    ).status_code == 201

    r = client.get(f"/children/{child['id']}/knowledge", headers=headers)

    assert r.status_code == 200
    nodos = r.json()
    assert len(nodos) == 1
    assert nodos[0]["concept"]
    assert nodos[0]["mastery"] == 1


def test_child_from_another_family_returns_404(client):
    """Aislamiento entre familias: 404, nunca 403 (no confirmar que existe)."""
    h1 = _family_headers(client, "una@example.com")
    ajeno = _create_child(client, h1)
    h2 = _family_headers(client, "otra@example.com")

    assert client.get(f"/children/{ajeno['id']}/profile", headers=h2).status_code == 404
    assert client.get(f"/children/{ajeno['id']}/knowledge", headers=h2).status_code == 404


def test_child_token_rejected(client):
    """JWT tipado: estos endpoints son de familia; un token `child` da 401."""
    headers = _family_headers(client)
    child = _create_child(client, headers)
    child_headers = _child_token(client, headers, child["id"])

    assert client.get(f"/children/{child['id']}/profile", headers=child_headers).status_code == 401
    assert client.get(f"/children/{child['id']}/knowledge", headers=child_headers).status_code == 401


def test_child_without_activity_is_coherent(client):
    """Caso límite de la HU: niño recién creado, ficha vacía y sin error."""
    headers = _family_headers(client)
    child = _create_child(client, headers, name="Leo", pin="5678")

    perfil = client.get(f"/children/{child['id']}/profile", headers=headers)
    ficha = client.get(f"/children/{child['id']}/knowledge", headers=headers)

    assert perfil.status_code == 200 and perfil.json()["islands"] == 0
    assert ficha.status_code == 200 and ficha.json() == []
