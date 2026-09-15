from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.child import Child
from app.models.story import Story


def create(db: Session, story: Story) -> Story:
    db.add(story)
    db.commit()
    db.refresh(story)
    return story


def list_for_child(db: Session, child_id: int, status: str | None = None) -> list[Story]:
    q = select(Story).where(Story.child_id == child_id)
    if status:
        q = q.where(Story.status == status)
    return list(db.execute(q).scalars().all())


def get_for_child(db: Session, child_id: int, story_id: int) -> Story | None:
    s = db.get(Story, story_id)
    if s is None or s.child_id != child_id:
        return None
    return s


def get_for_family(db: Session, family_id: int, story_id: int) -> Story | None:
    s = db.get(Story, story_id)
    if s is None:
        return None
    child = db.get(Child, s.child_id)
    if child is None or child.family_id != family_id:
        return None
    return s


def list_for_family(db: Session, family_id: int, status: str | None = None) -> list[Story]:
    q = (
        select(Story)
        .join(Child, Child.id == Story.child_id)
        .where(Child.family_id == family_id)
    )
    if status:
        q = q.where(Story.status == status)
    return list(db.execute(q).scalars().all())
