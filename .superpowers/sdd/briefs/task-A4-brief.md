# Task A4: Responder el reto + actualizar grafo de conocimiento

Usa el código EXACTO. TDD. Backend `backend/`, venv `./.venv/Scripts/python.exe`. Rama `feature-entrega3-nucleo`. SIN push.

**Files:**
- Create: `backend/app/repositories/knowledge.py`
- Create: `backend/app/schemas/answer.py`
- Modify: `backend/app/services/lesson_service.py` (añadir `answer_lesson`)
- Modify: `backend/app/routers/lessons.py` (endpoint answer)
- Test: `backend/tests/test_answer_api.py`

## Step 1: Test `backend/tests/test_answer_api.py`

```python
from datetime import date

from sqlalchemy import select

from app.models.child import Child
from app.models.family import Family
from app.models.knowledge import KnowledgeNode
from app.security import create_token


def _child_token(db_session):
    fam = Family(name="F")
    db_session.add(fam)
    db_session.flush()
    child = Child(family_id=fam.id, name="Leo", birthdate=date(2018, 1, 1), pin_hash="x")
    db_session.add(child)
    db_session.commit()
    return child.id, create_token(subject=str(child.id), token_type="child")


def _make_lesson(client, token):
    return client.post(
        "/lessons", headers={"Authorization": f"Bearer {token}"},
        json={"curiosity": "¿por qué llueve?"},
    ).json()


def test_correct_answer_creates_knowledge_node(client, db_session):
    child_id, token = _child_token(db_session)
    lesson = _make_lesson(client, token)
    r = client.post(
        f"/lessons/{lesson['id']}/answer",
        headers={"Authorization": f"Bearer {token}"},
        json={"choice_index": 1},
    )
    assert r.status_code == 200
    assert r.json()["correct"] is True
    nodes = db_session.execute(
        select(KnowledgeNode).where(KnowledgeNode.child_id == child_id)
    ).scalars().all()
    assert len(nodes) == 1
    assert nodes[0].concept == lesson["concept"]


def test_wrong_answer_creates_no_node(client, db_session):
    child_id, token = _child_token(db_session)
    lesson = _make_lesson(client, token)
    r = client.post(
        f"/lessons/{lesson['id']}/answer",
        headers={"Authorization": f"Bearer {token}"},
        json={"choice_index": 0},
    )
    assert r.status_code == 200
    assert r.json()["correct"] is False
    nodes = db_session.execute(
        select(KnowledgeNode).where(KnowledgeNode.child_id == child_id)
    ).scalars().all()
    assert len(nodes) == 0
```

## Step 2: Ver fallar
`./.venv/Scripts/python.exe -m pytest tests/test_answer_api.py -v` → FAIL.

## Step 3: Crear `backend/app/repositories/knowledge.py`

```python
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


def list_for_child(db: Session, child_id: int) -> list[KnowledgeNode]:
    return list(
        db.execute(
            select(KnowledgeNode).where(KnowledgeNode.child_id == child_id)
        ).scalars().all()
    )
```

## Step 4: Crear `backend/app/schemas/answer.py`

```python
from pydantic import BaseModel


class AnswerRequest(BaseModel):
    choice_index: int


class AnswerResult(BaseModel):
    correct: bool
    explanation: str
    concept: str
```

## Step 5: Añadir `answer_lesson` en `backend/app/services/lesson_service.py`
Añade el import `from app.repositories import knowledge as knowledge_repo` (junto a los demás imports) y la función:

```python
def answer_lesson(db: Session, child: Child, lesson, choice_index: int) -> dict:
    correct = choice_index == lesson.quiz_correct_index
    if correct and not lesson.answered:
        lesson.answered = True
        db.commit()
        knowledge_repo.upsert_node(db, child.id, lesson.concept, lesson.subject)
    return {
        "correct": correct,
        "explanation": lesson.quiz_explanation,
        "concept": lesson.concept,
    }
```

## Step 6: Añadir el endpoint en `backend/app/routers/lessons.py`
Añade los imports `from app.schemas.answer import AnswerRequest, AnswerResult` y la ruta (al final del archivo, dentro del mismo router):

```python
@router.post("/{lesson_id}/answer", response_model=AnswerResult)
def answer_lesson(
    lesson_id: int,
    payload: AnswerRequest,
    child: Child = Depends(get_current_child),
    db: Session = Depends(get_db),
) -> AnswerResult:
    lesson = lesson_repo.get_for_child(db, child.id, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lección no encontrada")
    return AnswerResult(**lesson_service.answer_lesson(db, child, lesson, payload.choice_index))
```

## Step 7: Tests
`./.venv/Scripts/python.exe -m pytest tests/test_answer_api.py -v` → PASS. Luego suite completa `-q` → todo PASS.

## Step 8: Commit (local, SIN push)
```bash
git add backend/
git commit -m "feat(backend): answer quiz updates child knowledge graph"
```
