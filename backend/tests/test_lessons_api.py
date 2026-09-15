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


def test_create_lesson_returns_quiz_without_answer(client, db_session):
    token = _child_token(db_session)
    r = client.post(
        "/lessons",
        headers={"Authorization": f"Bearer {token}"},
        json={"curiosity": "¿por qué llueve?"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["quiz"]["question"]
    assert len(body["quiz"]["options"]) == 3
    assert "correct_index" not in body["quiz"]
    assert body["answered"] is False
    assert "follow_ups" in body
    assert isinstance(body["follow_ups"], list)


def test_create_lesson_blocked_by_moderation(client, db_session):
    token = _child_token(db_session)
    r = client.post(
        "/lessons",
        headers={"Authorization": f"Bearer {token}"},
        json={"curiosity": "quiero ver armas"},
    )
    assert r.status_code == 422


def test_get_lesson_requires_child_auth(client):
    assert client.get("/lessons/1").status_code == 401
