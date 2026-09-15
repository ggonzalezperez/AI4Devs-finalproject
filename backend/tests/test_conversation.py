"""Tests for conversational lesson threads (Task B2a)."""
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


def _make_lesson(client, token, curiosity="¿por qué llueve?"):
    r = client.post(
        "/lessons",
        headers={"Authorization": f"Bearer {token}"},
        json={"curiosity": curiosity},
    )
    assert r.status_code == 201
    return r.json()


def test_create_root_lesson_auto_creates_island(client, db_session):
    """Creating a root lesson creates a knowledge node without answering the quiz."""
    child_id, token = _child_token(db_session)
    h = {"Authorization": f"Bearer {token}"}

    # No knowledge before lesson
    assert client.get("/me/knowledge", headers=h).json() == []

    # Create root lesson
    lesson = _make_lesson(client, token)

    # Island should exist automatically (without quiz answer)
    nodes = client.get("/me/knowledge", headers=h).json()
    assert len(nodes) == 1
    assert nodes[0]["concept"] == lesson["concept"]


def test_ask_followup_creates_new_turn(client, db_session):
    """POST /lessons/{root}/ask returns 201 and a new turn."""
    child_id, token = _child_token(db_session)
    h = {"Authorization": f"Bearer {token}"}

    root = _make_lesson(client, token, "¿por qué llueve?")

    r = client.post(
        f"/lessons/{root['id']}/ask",
        headers=h,
        json={"curiosity": "¿y por qué a veces nieva?"},
    )
    assert r.status_code == 201
    child_turn = r.json()
    assert child_turn["id"] != root["id"]
    assert child_turn["curiosity"] == "¿y por qué a veces nieva?"


def test_thread_returns_both_turns_in_order(client, db_session):
    """GET /lessons/{root}/thread returns root + child turn in order."""
    child_id, token = _child_token(db_session)
    h = {"Authorization": f"Bearer {token}"}

    root = _make_lesson(client, token, "¿por qué llueve?")

    r = client.post(
        f"/lessons/{root['id']}/ask",
        headers=h,
        json={"curiosity": "¿y por qué a veces nieva?"},
    )
    assert r.status_code == 201
    child_turn = r.json()

    # Thread from root
    thread_r = client.get(f"/lessons/{root['id']}/thread", headers=h)
    assert thread_r.status_code == 200
    thread = thread_r.json()
    assert len(thread) == 2
    assert thread[0]["id"] == root["id"]
    assert thread[1]["id"] == child_turn["id"]


def test_thread_of_child_equals_thread_of_root(client, db_session):
    """Thread accessed via child turn ID == thread accessed via root ID."""
    child_id, token = _child_token(db_session)
    h = {"Authorization": f"Bearer {token}"}

    root = _make_lesson(client, token, "¿por qué llueve?")
    r = client.post(
        f"/lessons/{root['id']}/ask",
        headers=h,
        json={"curiosity": "¿y por qué a veces nieva?"},
    )
    child_turn = r.json()

    thread_via_root = client.get(f"/lessons/{root['id']}/thread", headers=h).json()
    thread_via_child = client.get(f"/lessons/{child_turn['id']}/thread", headers=h).json()

    assert [t["id"] for t in thread_via_root] == [t["id"] for t in thread_via_child]


def test_ensure_node_does_not_increase_mastery(client, db_session):
    """Creating multiple turns with the same concept leaves mastery unchanged (no quiz answered)."""
    child_id, token = _child_token(db_session)
    h = {"Authorization": f"Bearer {token}"}

    # The stub generates a concept from the curiosity text.
    root = _make_lesson(client, token, "¿por qué llueve?")

    nodes_after_root = db_session.execute(
        select(KnowledgeNode).where(KnowledgeNode.child_id == child_id)
    ).scalars().all()
    assert len(nodes_after_root) >= 1
    mastery_after_root = {n.concept: n.mastery for n in nodes_after_root}

    # Create a second turn (ensure_node is called again — should NOT change mastery)
    client.post(
        f"/lessons/{root['id']}/ask",
        headers=h,
        json={"curiosity": "¿y por qué a veces hay tormenta?"},
    )

    db_session.expire_all()
    nodes_after_turn = db_session.execute(
        select(KnowledgeNode).where(KnowledgeNode.child_id == child_id)
    ).scalars().all()
    mastery_after_turn = {n.concept: n.mastery for n in nodes_after_turn}

    # For any concept that existed after root lesson, mastery must not have increased
    for concept, mastery_before in mastery_after_root.items():
        assert mastery_after_turn.get(concept, mastery_before) == mastery_before


def test_correct_quiz_answer_increases_mastery(client, db_session):
    """A correct quiz answer increases mastery (upsert_node behavior preserved)."""
    child_id, token = _child_token(db_session)
    h = {"Authorization": f"Bearer {token}"}

    lesson = _make_lesson(client, token, "¿por qué llueve?")

    # Node is auto-created at lesson creation with default mastery (model default=1)
    nodes_before = db_session.execute(
        select(KnowledgeNode).where(KnowledgeNode.child_id == child_id)
    ).scalars().all()
    assert len(nodes_before) == 1
    mastery_before = nodes_before[0].mastery

    # Answer quiz correctly (stub: correct_index=1) — should increase mastery
    r = client.post(
        f"/lessons/{lesson['id']}/answer",
        headers=h,
        json={"choice_index": 1},
    )
    assert r.status_code == 200
    assert r.json()["correct"] is True

    db_session.expire_all()
    nodes_after = db_session.execute(
        select(KnowledgeNode).where(KnowledgeNode.child_id == child_id)
    ).scalars().all()
    assert len(nodes_after) == 1
    assert nodes_after[0].mastery == mastery_before + 1


def test_ask_followup_404_on_unknown_lesson(client, db_session):
    """POST /lessons/9999/ask returns 404 when lesson does not exist."""
    child_id, token = _child_token(db_session)
    h = {"Authorization": f"Bearer {token}"}
    r = client.post(
        "/lessons/9999/ask",
        headers=h,
        json={"curiosity": "¿qué es eso?"},
    )
    assert r.status_code == 404


def test_thread_404_on_unknown_lesson(client, db_session):
    """GET /lessons/9999/thread returns 404 when lesson does not exist."""
    child_id, token = _child_token(db_session)
    h = {"Authorization": f"Bearer {token}"}
    r = client.get("/lessons/9999/thread", headers=h)
    assert r.status_code == 404


def test_ask_followup_blocked_by_moderation(client, db_session):
    """POST /lessons/{id}/ask returns 422 on moderated curiosity."""
    child_id, token = _child_token(db_session)
    h = {"Authorization": f"Bearer {token}"}

    root = _make_lesson(client, token, "¿por qué llueve?")

    r = client.post(
        f"/lessons/{root['id']}/ask",
        headers=h,
        json={"curiosity": "quiero ver armas"},
    )
    assert r.status_code == 422
