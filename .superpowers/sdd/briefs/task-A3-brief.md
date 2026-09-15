# Task A3: Endpoints de lecciones (generar + obtener)

Usa el código EXACTO. TDD. Backend `backend/`, venv `./.venv/Scripts/python.exe`. Rama `feature-entrega3-nucleo`. SIN push.

**Files:**
- Create: `backend/app/schemas/lesson.py`
- Create: `backend/app/repositories/lesson.py`
- Create: `backend/app/services/lesson_service.py`
- Create: `backend/app/routers/lessons.py`
- Modify: `backend/app/main.py` (incluir router lessons, manteniendo CORS y los demás routers)
- Test: `backend/tests/test_lessons_api.py`

## Step 1: Test `backend/tests/test_lessons_api.py`

```python
from datetime import date

from app.models.child import Child
from app.models.family import Family
from app.security import create_token


def _child_token(db_session):
    fam = Family(name="F")
    db_session.add(fam)
    db_session.flush()
    child = Child(family_id=fam.id, name="Leo", birthdate=date(2018, 1, 1), pin_hash="x")
    db_session.add(child)
    db_session.commit()
    return create_token(subject=str(child.id), token_type="child")


def test_create_lesson_returns_quiz_without_answer(client, db_session):
    token = _child_token(db_session)
    r = client.post(
        "/lessons",
        headers={"Authorization": f"Bearer {token}"},
        json={"curiosity": "¿por qué llueve?"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["quiz"]["question"]
    assert len(body["quiz"]["options"]) == 3
    assert "correct_index" not in body["quiz"]
    assert body["answered"] is False


def test_create_lesson_blocked_by_moderation(client, db_session):
    token = _child_token(db_session)
    r = client.post(
        "/lessons",
        headers={"Authorization": f"Bearer {token}"},
        json={"curiosity": "quiero ver armas"},
    )
    assert r.status_code == 422


def test_get_lesson_requires_child_auth(client):
    assert client.get("/lessons/1").status_code == 401
```

## Step 2: Ver fallar
`./.venv/Scripts/python.exe -m pytest tests/test_lessons_api.py -v` → FAIL.

## Step 3: Crear `backend/app/schemas/lesson.py`

```python
from pydantic import BaseModel, ConfigDict, Field


class LessonCreate(BaseModel):
    curiosity: str = Field(min_length=2, max_length=300)
    subject: str | None = None


class QuizPublic(BaseModel):
    question: str
    options: list[str]


class LessonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    curiosity: str
    subject: str
    concept: str
    title: str
    body: str
    fun_fact: str
    answered: bool
    quiz: QuizPublic
```

## Step 4: Crear `backend/app/repositories/lesson.py`

```python
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
```

## Step 5: Crear `backend/app/services/lesson_service.py`

```python
from sqlalchemy.orm import Session

from app.models.child import Child
from app.models.lesson import Lesson
from app.repositories import lesson as lesson_repo
from app.services.lesson_generator import LessonGenerator, StubLessonGenerator
from app.services.moderation import check_curiosity

_generator: LessonGenerator = StubLessonGenerator()


def create_lesson(db: Session, child: Child, curiosity: str, subject: str | None) -> Lesson:
    check_curiosity(curiosity)
    g = _generator.generate(curiosity, age=child.age, subject=subject)
    lesson = Lesson(
        child_id=child.id,
        curiosity=curiosity,
        subject=g.subject,
        concept=g.concept,
        title=g.title,
        body=g.body,
        fun_fact=g.fun_fact,
        quiz_question=g.quiz_question,
        quiz_options=g.quiz_options,
        quiz_correct_index=g.quiz_correct_index,
        quiz_explanation=g.quiz_explanation,
    )
    return lesson_repo.create(db, lesson)


def to_read_dict(lesson: Lesson) -> dict:
    return {
        "id": lesson.id,
        "curiosity": lesson.curiosity,
        "subject": lesson.subject,
        "concept": lesson.concept,
        "title": lesson.title,
        "body": lesson.body,
        "fun_fact": lesson.fun_fact,
        "answered": lesson.answered,
        "quiz": {"question": lesson.quiz_question, "options": lesson.quiz_options},
    }
```

## Step 6: Crear `backend/app/routers/lessons.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_child
from app.models.child import Child
from app.repositories import lesson as lesson_repo
from app.schemas.lesson import LessonCreate, LessonRead
from app.services import lesson_service
from app.services.moderation import ModerationError

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.post("", response_model=LessonRead, status_code=status.HTTP_201_CREATED)
def create_lesson(
    payload: LessonCreate,
    child: Child = Depends(get_current_child),
    db: Session = Depends(get_db),
) -> LessonRead:
    try:
        lesson = lesson_service.create_lesson(db, child, payload.curiosity, payload.subject)
    except ModerationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return LessonRead.model_validate(lesson_service.to_read_dict(lesson))


@router.get("/{lesson_id}", response_model=LessonRead)
def get_lesson(
    lesson_id: int,
    child: Child = Depends(get_current_child),
    db: Session = Depends(get_db),
) -> LessonRead:
    lesson = lesson_repo.get_for_child(db, child.id, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lección no encontrada")
    return LessonRead.model_validate(lesson_service.to_read_dict(lesson))
```

## Step 7: Incluir el router en `backend/app/main.py`
Añade `lessons` al import `from app.routers import ...` y `app.include_router(lessons.router)`. NO toques el middleware CORS ni los demás routers.

## Step 8: Tests
`./.venv/Scripts/python.exe -m pytest tests/test_lessons_api.py -v` → PASS. Luego suite completa `-q` → todo PASS.

## Step 9: Commit (local, SIN push)
```bash
git add backend/
git commit -m "feat(backend): lessons endpoints (generate + get) with moderation"
```
