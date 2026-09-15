from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.family import Family, User


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()


def create_family_with_user(db: Session, name: str, email: str, password_hash: str) -> User:
    family = Family(name=name)
    db.add(family)
    db.flush()
    user = User(family_id=family.id, email=email, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
