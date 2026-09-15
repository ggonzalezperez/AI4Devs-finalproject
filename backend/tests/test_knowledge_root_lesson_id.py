"""Tests for root_lesson_id on KnowledgeNode (Task B2c)."""
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


def test_root_lesson_creates_island_with_own_id(client, db_session):
    """After creating a root lesson, /me/knowledge returns a node whose root_lesson_id == lesson id."""
    child_id, token = _child_token(db_session)
    h = {"Authorization": f"Bearer {token}"}

    lesson = client.post("/lessons", headers=h, json={"curiosity": "¿por qué llueve?"}).json()
    assert lesson.get("id"), "lesson should have an id"

    nodes = client.get("/me/knowledge", headers=h).json()
    assert len(nodes) == 1
    assert nodes[0]["root_lesson_id"] == lesson["id"]


def test_followup_different_concept_island_has_root_id(client, db_session):
    """After POST /lessons/{root}/ask with a different concept, new island has root_lesson_id == root id."""
    child_id, token = _child_token(db_session)
    h = {"Authorization": f"Bearer {token}"}

    # Create root lesson
    root = client.post("/lessons", headers=h, json={"curiosity": "¿por qué llueve?"}).json()
    root_id = root["id"]

    # Ask a follow-up with a DIFFERENT curiosity (the stub derives concept from the text)
    followup = client.post(
        f"/lessons/{root_id}/ask",
        headers=h,
        json={"curiosity": "¿qué es una nube de verdad completamente diferente?"},
    ).json()
    followup_concept = followup["concept"]

    # If stub produced a new concept distinct from root, it should have root_lesson_id == root_id
    # If it's the same concept, the existing node is returned (still has root_lesson_id from creation)
    db_session.expire_all()
    nodes = db_session.execute(
        select(KnowledgeNode).where(
            KnowledgeNode.child_id == child_id,
            KnowledgeNode.concept == followup_concept,
        )
    ).scalars().all()
    assert len(nodes) >= 1
    node = nodes[0]
    # root_lesson_id must equal the root lesson id (not the child turn id)
    assert node.root_lesson_id == root_id


def test_root_lesson_id_present_in_me_knowledge_response(client, db_session):
    """GET /me/knowledge serialises root_lesson_id."""
    child_id, token = _child_token(db_session)
    h = {"Authorization": f"Bearer {token}"}

    lesson = client.post("/lessons", headers=h, json={"curiosity": "¿por qué brilla el sol?"}).json()
    nodes = client.get("/me/knowledge", headers=h).json()
    assert len(nodes) >= 1
    assert "root_lesson_id" in nodes[0]
    assert nodes[0]["root_lesson_id"] == lesson["id"]
