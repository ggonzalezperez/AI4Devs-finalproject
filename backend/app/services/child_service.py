from datetime import date

from sqlalchemy.orm import Session

from app.models.child import Child
from app.repositories import child as child_repo
from app.repositories import knowledge as knowledge_repo
from app.schemas.knowledge import ChildProfile
from app.security import hash_secret, verify_secret


def create_child(db: Session, family_id: int, name: str, birthdate: date, pin: str, avatar: str = "fox") -> Child:
    return child_repo.create_child(db, family_id, name, birthdate, hash_secret(pin), avatar)


def list_children(db: Session, family_id: int) -> list[Child]:
    return child_repo.list_children(db, family_id)


def verify_child_pin(db: Session, family_id: int, child_id: int, pin: str) -> Child | None:
    child = child_repo.get_child_for_family(db, family_id, child_id)
    if child and verify_secret(pin, child.pin_hash):
        return child
    return None


def build_profile(db: Session, child: Child) -> ChildProfile:
    """Ficha del explorador, compartida por el propio niño (`/me/profile`) y su
    familia (`/children/{id}/profile`). `islands` es derivado, no una columna."""
    nodes = knowledge_repo.list_for_child(db, child.id)
    return ChildProfile(
        name=child.name,
        age=child.age,
        islands=len(nodes),
        avatar=child.avatar,
        avatar_image_url=child.avatar_image_url,
    )
