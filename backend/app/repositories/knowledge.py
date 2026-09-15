from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge import KnowledgeNode


def upsert_node(db: Session, child_id: int, concept: str, subject: str) -> KnowledgeNode:
    existing = db.execute(
        select(KnowledgeNode).where(
            KnowledgeNode.child_id == child_id, KnowledgeNode.concept == concept
        )
    ).scalar_one_or_none()
    if existing:
        existing.mastery += 1
        db.commit()
        db.refresh(existing)
        return existing
    node = KnowledgeNode(child_id=child_id, concept=concept, subject=subject)
    db.add(node)
    db.commit()
    db.refresh(node)
    return node


def ensure_node(
    db: Session, child_id: int, concept: str, subject: str, root_lesson_id: int | None = None
) -> KnowledgeNode:
    existing = db.execute(
        select(KnowledgeNode).where(
            KnowledgeNode.child_id == child_id, KnowledgeNode.concept == concept
        )
    ).scalar_one_or_none()
    if existing:
        return existing
    node = KnowledgeNode(
        child_id=child_id, concept=concept, subject=subject, root_lesson_id=root_lesson_id
    )
    db.add(node)
    db.commit()
    db.refresh(node)
    return node


def list_for_child(db: Session, child_id: int) -> list[KnowledgeNode]:
    return list(
        db.execute(
            select(KnowledgeNode).where(KnowledgeNode.child_id == child_id)
        ).scalars().all()
    )
