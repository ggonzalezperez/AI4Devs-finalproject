from datetime import date

from app.models.child import Child
from app.models.family import Family
from app.security import create_token


def _child_token(db_session):
    fam = Family(name="F")
    db_session.add(fam)
    db_session.flush()
    child = Child(family_id=fam.id, name="Leo", birthdate=date(2018, 1, 1), pin_hash="x")
    db_session.add(child)
    db_session.commit()
    return create_token(subject=str(child.id), token_type="child")


def test_knowledge_empty_then_grows(client, db_session):
    token = _child_token(db_session)
    h = {"Authorization": f"Bearer {token}"}
    assert client.get("/me/knowledge", headers=h).json() == []
    lesson = client.post("/lessons", headers=h, json={"curiosity": "¿por qué llueve?"}).json()
    client.post(f"/lessons/{lesson['id']}/answer", headers=h, json={"choice_index": 1})
    nodes = client.get("/me/knowledge", headers=h).json()
    assert len(nodes) == 1
    assert nodes[0]["concept"] == lesson["concept"]


def test_suggestions_returns_list(client, db_session):
    token = _child_token(db_session)
    r = client.get("/me/suggestions", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert len(r.json()) >= 3
    assert "curiosity" in r.json()[0]


def test_me_requires_child_auth(client):
    assert client.get("/me/knowledge").status_code == 401


def test_suggestions_vary_between_visits(client, db_session):
    """Las 5 sugerencias eran fijas: quien volvía a «¿Qué quieres descubrir hoy?»
    veía siempre exactamente las mismas. La pantalla de inicio del niño debe
    sentirse viva."""
    from app.services.me_suggestions import POOL

    token = _child_token(db_session)
    h = {"Authorization": f"Bearer {token}"}

    vistas = set()
    for _ in range(12):
        r = client.get("/me/suggestions", headers=h)
        assert r.status_code == 200
        lote = r.json()
        assert len(lote) == 5, "siempre se ofrecen 5"
        for s in lote:
            assert s["curiosity"] and s["emoji"]
            vistas.add(s["curiosity"])

    assert len(POOL) > 5, "el repertorio debe ser mayor que lo que se muestra"
    assert len(vistas) > 5, "en varias visitas deben aparecer sugerencias distintas"
