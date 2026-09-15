# Task A5: Endpoints GET /me/knowledge y GET /me/suggestions

Usa el código EXACTO. TDD. Backend `backend/`, venv `./.venv/Scripts/python.exe`. Rama `feature-entrega3-nucleo`. SIN push.

**Files:**
- Create: `backend/app/schemas/knowledge.py`
- Create: `backend/app/routers/me.py`
- Modify: `backend/app/main.py` (incluir router me)
- Test: `backend/tests/test_me_api.py`

## Step 1: Test `backend/tests/test_me_api.py`

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


def test_knowledge_empty_then_grows(client, db_session):
    token = _child_token(db_session)
    h = {"Authorization": f"Bearer {token}"}
    assert client.get("/me/knowledge", headers=h).json() == []
    lesson = client.post("/lessons", headers=h, json={"curiosity": "¿por qué llueve?"}).json()
    client.post(f"/lessons/{lesson['id']}/answer", headers=h, json={"choice_index": 1})
    nodes = client.get("/me/knowledge", headers=h).json()
    assert len(nodes) == 1
    assert nodes[0]["concept"] == lesson["concept"]


def test_suggestions_returns_list(client, db_session):
    token = _child_token(db_session)
    r = client.get("/me/suggestions", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert len(r.json()) >= 3
    assert "curiosity" in r.json()[0]


def test_me_requires_child_auth(client):
    assert client.get("/me/knowledge").status_code == 401
```

## Step 2: Ver fallar
`./.venv/Scripts/python.exe -m pytest tests/test_me_api.py -v` → FAIL.

## Step 3: Crear `backend/app/schemas/knowledge.py`

```python
from pydantic import BaseModel, ConfigDict


class KnowledgeNodeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    concept: str
    subject: str
    mastery: int


class Suggestion(BaseModel):
    curiosity: str
    emoji: str
```

## Step 4: Crear `backend/app/routers/me.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_child
from app.models.child import Child
from app.repositories import knowledge as knowledge_repo
from app.schemas.knowledge import KnowledgeNodeRead, Suggestion

router = APIRouter(prefix="/me", tags=["me"])

_SUGGESTIONS = [
    {"curiosity": "¿Por qué flotan los barcos?", "emoji": "⛵"},
    {"curiosity": "¿Por qué llueve?", "emoji": "🌧️"},
    {"curiosity": "¿Cómo vuelan los aviones?", "emoji": "✈️"},
    {"curiosity": "¿Por qué brillan las estrellas?", "emoji": "⭐"},
    {"curiosity": "¿Cómo nacen los volcanes?", "emoji": "🌋"},
]


@router.get("/knowledge", response_model=list[KnowledgeNodeRead])
def my_knowledge(
    child: Child = Depends(get_current_child),
    db: Session = Depends(get_db),
) -> list[KnowledgeNodeRead]:
    return [
        KnowledgeNodeRead.model_validate(n) for n in knowledge_repo.list_for_child(db, child.id)
    ]


@router.get("/suggestions", response_model=list[Suggestion])
def my_suggestions(child: Child = Depends(get_current_child)) -> list[Suggestion]:
    return [Suggestion(**s) for s in _SUGGESTIONS]
```

## Step 5: Incluir el router en `backend/app/main.py`
Añade `me` al import `from app.routers import ...` y `app.include_router(me.router)`. NO toques CORS ni los demás routers.

## Step 6: Suite completa
`./.venv/Scripts/python.exe -m pytest -q` → todo PASS.

## Step 7: Commit (local, SIN push)
```bash
git add backend/
git commit -m "feat(backend): /me/knowledge and /me/suggestions endpoints"
```
