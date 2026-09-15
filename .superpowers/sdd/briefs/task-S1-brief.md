# Task S1: Modelo Story + StubStoryGenerator + servicio de creación + migración

Backend `backend/`, venv `./.venv/Scripts/python.exe`. Rama `feature-cuentos`. SIN push. TDD.
Cuentos generados a partir de las "islas" (conceptos del grafo) del niño. Estado: `pending|approved|rejected`.

**Files:**
- Create: `backend/app/models/story.py`
- Modify: `backend/app/models/__init__.py`
- Create: `backend/app/services/story_generator.py`
- Create: `backend/app/repositories/story.py`
- Create: `backend/app/services/story_service.py`
- Test: `backend/tests/test_story.py`
- Migración Alembic (no destructiva).

## Step 1: `backend/app/models/story.py`
```python
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Story(Base):
    __tablename__ = "stories"

    id: Mapped[int] = mapped_column(primary_key=True)
    child_id: Mapped[int] = mapped_column(ForeignKey("children.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending|approved|rejected
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
```

## Step 2: Reexportar en `backend/app/models/__init__.py` (añade al final)
```python
from app.models.story import Story  # noqa: F401
```

## Step 3: `backend/app/services/story_generator.py`
```python
from dataclasses import dataclass


@dataclass
class GeneratedStory:
    title: str
    body: str


class StubStoryGenerator:
    """Cuento determinista a partir de los conceptos que el niño ha explorado.

    Costura para un generador real (LLM) que implementará la misma interfaz.
    """

    def generate(self, child_name: str, age: int, concepts: list[str]) -> GeneratedStory:
        if concepts:
            tema = ", ".join(concepts[:3])
            cuerpo = (
                f"Érase una vez {child_name}, un explorador muy curioso de {age} años. "
                f"En su archipiélago había descubierto islas mágicas sobre {tema}. "
                f"Una mañana, {child_name} montó en su barquito y navegó hacia la isla de "
                f"{concepts[0]}. Allí aprendió que cada pregunta abre una puerta nueva. "
                f"Al volver a casa, {child_name} se durmió feliz, soñando con la próxima aventura."
            )
            titulo = f"La aventura de {child_name} y {concepts[0]}"
        else:
            cuerpo = (
                f"Érase una vez {child_name}, un explorador de {age} años con muchas ganas "
                f"de descubrir el mundo. Su aventura no ha hecho más que empezar."
            )
            titulo = f"El comienzo de {child_name}"
        return GeneratedStory(title=titulo, body=cuerpo)
```

## Step 4: `backend/app/repositories/story.py`
```python
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
```

## Step 5: `backend/app/services/story_service.py`
```python
from sqlalchemy.orm import Session

from app.models.child import Child
from app.models.story import Story
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
```

## Step 6: Test `backend/tests/test_story.py`
```python
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
```

## Step 7: Tests + migración
- `./.venv/Scripts/python.exe -m pytest tests/test_story.py -v` → PASS.
- `./.venv/Scripts/alembic.exe revision --autogenerate -m "stories table"` → verifica que SOLO crea `op.create_table("stories", ...)` (+ índices). Si hay drops sobre tablas existentes, DETENTE y reporta DONE_WITH_CONCERNS sin aplicar. Si limpia: `./.venv/Scripts/alembic.exe upgrade head`.
- Suite completa `-q` → todo PASS.

## Step 8: Commit (local, SIN push)
```bash
git add backend/
git commit -m "feat(backend): Story model + stub generator + creation service + migration"
```
