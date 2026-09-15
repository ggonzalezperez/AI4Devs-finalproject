from datetime import date

from app.models.child import Child
from app.models.family import Family
from app.security import create_token


def _child_token(db_session):
    fam = Family(name="F")
    db_session.add(fam)
    db_session.flush()
    child = Child(family_id=fam.id, name="Nora", birthdate=date(2018, 1, 1), pin_hash="x")
    db_session.add(child)
    db_session.commit()
    return create_token(subject=str(child.id), token_type="child")


def test_profile_returns_name_age_islands(client, db_session):
    token = _child_token(db_session)
    h = {"Authorization": f"Bearer {token}"}
    r = client.get("/me/profile", headers=h)
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Nora"
    assert body["age"] >= 6
    assert body["islands"] == 0
    assert body["avatar"] == "fox"
    # Tras acertar una lección, sube a 1
    lesson = client.post("/lessons", headers=h, json={"curiosity": "¿por qué llueve?"}).json()
    client.post(f"/lessons/{lesson['id']}/answer", headers=h, json={"choice_index": 1})
    assert client.get("/me/profile", headers=h).json()["islands"] == 1


def test_profile_requires_child_auth(client):
    assert client.get("/me/profile").status_code == 401


def test_build_profile_is_shared_by_child_and_family_views(db_session):
    """El perfil se construye en un solo sitio.

    Lo consumen `/me/profile` (token niño) y `/children/{id}/profile` (token
    familia); tenerlo duplicado era la vía rápida a que divergieran.
    """
    from app.repositories import knowledge as knowledge_repo
    from app.services import child_service

    fam = Family(name="F")
    db_session.add(fam)
    db_session.flush()
    child = Child(family_id=fam.id, name="Leo", birthdate=date(2018, 1, 1), pin_hash="x")
    db_session.add(child)
    db_session.commit()

    vacio = child_service.build_profile(db_session, child)
    assert vacio.name == "Leo" and vacio.islands == 0

    knowledge_repo.ensure_node(db_session, child.id, "lluvia", "ciencia")
    assert child_service.build_profile(db_session, child).islands == 1
