from datetime import date

from sqlalchemy import select

from app.models.child import Child
from app.models.family import Family
from app.models.knowledge import KnowledgeNode
from app.security import create_token


def _child_token(db_session):
    fam = Family(name="F")
    db_session.add(fam)
    db_session.flush()
    child = Child(family_id=fam.id, name="Leo", birthdate=date(2018, 1, 1), pin_hash="x")
    db_session.add(child)
    db_session.commit()
    return child.id, create_token(subject=str(child.id), token_type="child")


def _make_lesson(client, token):
    return client.post(
        "/lessons", headers={"Authorization": f"Bearer {token}"},
        json={"curiosity": "¿por qué llueve?"},
    ).json()


def test_correct_answer_creates_knowledge_node(client, db_session):
    child_id, token = _child_token(db_session)
    lesson = _make_lesson(client, token)
    r = client.post(
        f"/lessons/{lesson['id']}/answer",
        headers={"Authorization": f"Bearer {token}"},
        json={"choice_index": 1},
    )
    assert r.status_code == 200
    assert r.json()["correct"] is True
    nodes = db_session.execute(
        select(KnowledgeNode).where(KnowledgeNode.child_id == child_id)
    ).scalars().all()
    assert len(nodes) == 1
    assert nodes[0].concept == lesson["concept"]


def test_wrong_answer_does_not_increase_mastery(client, db_session):
    child_id, token = _child_token(db_session)
    lesson = _make_lesson(client, token)
    # Node is auto-created when lesson is generated (ensure_node)
    nodes_before = db_session.execute(
        select(KnowledgeNode).where(KnowledgeNode.child_id == child_id)
    ).scalars().all()
    assert len(nodes_before) == 1
    mastery_before = nodes_before[0].mastery
    r = client.post(
        f"/lessons/{lesson['id']}/answer",
        headers={"Authorization": f"Bearer {token}"},
        json={"choice_index": 0},
    )
    assert r.status_code == 200
    assert r.json()["correct"] is False
    db_session.expire_all()
    nodes = db_session.execute(
        select(KnowledgeNode).where(KnowledgeNode.child_id == child_id)
    ).scalars().all()
    assert len(nodes) == 1
    assert nodes[0].mastery == mastery_before
