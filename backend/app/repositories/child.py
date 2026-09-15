from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.child import Child


def create_child(
    db: Session, family_id: int, name: str, birthdate: date, pin_hash: str, avatar: str = "fox"
) -> Child:
    child = Child(family_id=family_id, name=name, birthdate=birthdate, pin_hash=pin_hash, avatar=avatar)
    db.add(child)
    db.commit()
    db.refresh(child)
    return child


def list_children(db: Session, family_id: int) -> list[Child]:
    return list(
        db.execute(select(Child).where(Child.family_id == family_id)).scalars().all()
    )


def get_child_for_family(db: Session, family_id: int, child_id: int) -> Child | None:
    child = db.get(Child, child_id)
    if child is None or child.family_id != family_id:
        return None
    return child
