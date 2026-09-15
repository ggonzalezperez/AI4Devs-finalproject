from datetime import date

from app.models.child import Child
from app.models.family import Family, User
from app.security import create_token


def _setup(db_session):
    fam = Family(name="F")
    db_session.add(fam)
    db_session.flush()
    user = User(family_id=fam.id, email="p@e.com", password_hash="x")
    child = Child(family_id=fam.id, name="Leo", birthdate=date(2018, 1, 1), pin_hash="x")
    db_session.add_all([user, child])
    db_session.commit()
    child_h = {"Authorization": f"Bearer {create_token(subject=str(child.id), token_type='child')}"}
    fam_h = {"Authorization": f"Bearer {create_token(subject=str(user.id), token_type='family')}"}
    return child, child_h, fam_h


def test_child_creates_pending_story(client, db_session):
    _child, child_h, _fam_h = _setup(db_session)
    r = client.post("/me/stories", headers=child_h)
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "pending"
    assert "Leo" in body["body"]


def test_child_only_sees_approved(client, db_session):
    _child, child_h, fam_h = _setup(db_session)
    sid = client.post("/me/stories", headers=child_h).json()["id"]
    # Pendiente: no aparece en su lista ni en el detalle
    assert client.get("/me/stories", headers=child_h).json() == []
    assert client.get(f"/me/stories/{sid}", headers=child_h).status_code == 404
    # La familia lo aprueba
    client.put(f"/family/stories/{sid}", headers=fam_h, json={"action": "approve"})
    lst = client.get("/me/stories", headers=child_h).json()
    assert len(lst) == 1 and lst[0]["id"] == sid
    assert client.get(f"/me/stories/{sid}", headers=child_h).status_code == 200


def test_family_lists_and_reviews(client, db_session):
    _child, child_h, fam_h = _setup(db_session)
    sid = client.post("/me/stories", headers=child_h).json()["id"]
    # La familia ve el pendiente
    pend = client.get("/family/stories", headers=fam_h, params={"status_filter": "pending"}).json()
    assert len(pend) == 1 and pend[0]["id"] == sid
    # Edita y aprueba en un solo paso
    r = client.put(
        f"/family/stories/{sid}",
        headers=fam_h,
        json={"action": "approve", "title": "Nuevo título"},
    )
    assert r.status_code == 200
    assert r.json()["title"] == "Nuevo título"
    assert r.json()["status"] == "approved"


def test_family_rejects_story(client, db_session):
    _child, child_h, fam_h = _setup(db_session)
    sid = client.post("/me/stories", headers=child_h).json()["id"]
    client.put(f"/family/stories/{sid}", headers=fam_h, json={"action": "reject"})
    # Rechazado: no aparece para el niño
    assert client.get("/me/stories", headers=child_h).json() == []
    rej = client.get("/family/stories", headers=fam_h, params={"status_filter": "rejected"}).json()
    assert len(rej) == 1


def test_auth_guards(client, db_session):
    _child, child_h, fam_h = _setup(db_session)
    # Niño no puede usar endpoints de familia y viceversa (tipo de token inválido → 401)
    assert client.get("/family/stories", headers=child_h).status_code == 401
    assert client.post("/me/stories", headers=fam_h).status_code == 401
    # Sin token → 401
    assert client.get("/me/stories").status_code == 401
    assert client.get("/family/stories").status_code == 401


def test_family_cannot_review_other_familys_story(client, db_session):
    _child, child_h, _fam_h = _setup(db_session)
    sid = client.post("/me/stories", headers=child_h).json()["id"]
    # Otra familia
    other = Family(name="Otra")
    db_session.add(other)
    db_session.flush()
    other_user = User(family_id=other.id, email="o@e.com", password_hash="x")
    db_session.add(other_user)
    db_session.commit()
    other_h = {"Authorization": f"Bearer {create_token(subject=str(other_user.id), token_type='family')}"}
    assert client.put(f"/family/stories/{sid}", headers=other_h, json={"action": "approve"}).status_code == 404
