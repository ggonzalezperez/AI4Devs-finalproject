from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.lesson import Lesson


def create(db: Session, lesson: Lesson) -> Lesson:
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


def get_for_child(db: Session, child_id: int, lesson_id: int) -> Lesson | None:
    lesson = db.get(Lesson, lesson_id)
    if lesson is None or lesson.child_id != child_id:
        return None
    return lesson


def list_thread(db: Session, child_id: int, lesson_id: int) -> list[Lesson]:
    anchor = get_for_child(db, child_id, lesson_id)
    if anchor is None:
        return []
    root_id = anchor.root_id or anchor.id
    rows = db.execute(
        select(Lesson)
        .where(
            Lesson.child_id == child_id,
            or_(Lesson.id == root_id, Lesson.root_id == root_id),
        )
        .order_by(Lesson.id)
    ).scalars().all()
    return list(rows)
