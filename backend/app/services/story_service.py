from sqlalchemy.orm import Session

from app.models.child import Child
from app.models.story import Story, _utcnow
from app.repositories import knowledge as knowledge_repo
from app.repositories import story as story_repo
from app.services.story_generator import StubStoryGenerator

_generator = StubStoryGenerator()


def create_story(db: Session, child: Child) -> Story:
    nodes = knowledge_repo.list_for_child(db, child.id)
    concepts = [n.concept for n in nodes]
    g = _generator.generate(child.name, child.age, concepts)
    story = Story(child_id=child.id, title=g.title, body=g.body, status="pending")
    return story_repo.create(db, story)


def review_story(
    db: Session,
    story: Story,
    action: str,
    title: str | None = None,
    body: str | None = None,
) -> Story:
    if title is not None:
        story.title = title
    if body is not None:
        story.body = body
    story.status = "approved" if action == "approve" else "rejected"
    story.reviewed_at = _utcnow()
    db.commit()
    db.refresh(story)
    return story
