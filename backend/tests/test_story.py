from datetime import date

from app.models.child import Child
from app.models.family import Family
from app.models.knowledge import KnowledgeNode
from app.services import story_service


def _child(db_session):
    fam = Family(name="F")
    db_session.add(fam)
    db_session.flush()
    child = Child(family_id=fam.id, name="Leo", birthdate=date(2018, 1, 1), pin_hash="x")
    db_session.add(child)
    db_session.commit()
    return child


def test_create_story_is_pending_and_weaves_concepts(db_session):
    child = _child(db_session)
    db_session.add(KnowledgeNode(child_id=child.id, concept="flotabilidad", subject="ciencia"))
    db_session.commit()
    story = story_service.create_story(db_session, child)
    assert story.id is not None
    assert story.status == "pending"
    assert "flotabilidad" in story.title or "flotabilidad" in story.body
    assert "Leo" in story.body


def test_create_story_without_concepts(db_session):
    child = _child(db_session)
    story = story_service.create_story(db_session, child)
    assert story.status == "pending"
    assert "Leo" in story.body
