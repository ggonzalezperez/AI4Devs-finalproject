# Task UX3: Endpoint GET /me/profile (nombre + edad + nº de islas del niño)

Backend `backend/`, venv `./.venv/Scripts/python.exe`. Rama `feature-ux-improvements`. SIN push. TDD.
Para la cabecera del mundo del niño (nombre + islas).

**Files:**
- Modify: `backend/app/schemas/knowledge.py` (añadir ChildProfile)
- Modify: `backend/app/routers/me.py` (endpoint /me/profile)
- Test: `backend/tests/test_me_profile.py`

## Step 1: Añadir a `backend/app/schemas/knowledge.py`
```python
class ChildProfile(BaseModel):
    name: str
    age: int
    islands: int
```
(Mantén `KnowledgeNodeRead` y `Suggestion`. Asegura el import `from pydantic import BaseModel, ConfigDict` ya presente.)

## Step 2: Añadir endpoint en `backend/app/routers/me.py`
Importa el schema (`from app.schemas.knowledge import ChildProfile`) y añade:
```python
@router.get("/profile", response_model=ChildProfile)
def my_profile(
    child: Child = Depends(get_current_child),
    db: Session = Depends(get_db),
) -> ChildProfile:
    nodes = knowledge_repo.list_for_child(db, child.id)
    return ChildProfile(name=child.name, age=child.age, islands=len(nodes))
```
(El router ya importa `get_current_child`, `Child`, `knowledge_repo`, `get_db`, `Session` por la Task A5; reutilízalos.)

## Step 3: Test `backend/tests/test_me_profile.py`
```python
from datetime import date

from app.models.child import Child
from app.models.family import Family
from app.security import create_token


def _child_token(db_session):
    fam = Family(name="F")
    db_session.add(fam)
    db_session.flush()
    child = Child(family_id=fam.id, name="Nora", birthdate=date(2018, 1, 1), pin_hash="x")
    db_session.add(child)
    db_session.commit()
    return create_token(subject=str(child.id), token_type="child")


def test_profile_returns_name_age_islands(client, db_session):
    token = _child_token(db_session)
    h = {"Authorization": f"Bearer {token}"}
    r = client.get("/me/profile", headers=h)
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Nora"
    assert body["age"] >= 6
    assert body["islands"] == 0
    # Tras acertar una lección, sube a 1
    lesson = client.post("/lessons", headers=h, json={"curiosity": "¿por qué llueve?"}).json()
    client.post(f"/lessons/{lesson['id']}/answer", headers=h, json={"choice_index": 1})
    assert client.get("/me/profile", headers=h).json()["islands"] == 1


def test_profile_requires_child_auth(client):
    assert client.get("/me/profile").status_code == 401
```

## Step 4: Tests + suite
`./.venv/Scripts/python.exe -m pytest tests/test_me_profile.py -v` → PASS. Luego `-q` completa → todo PASS.

## Step 5: Commit (local, SIN push)
```bash
git add backend/
git commit -m "feat(backend): GET /me/profile (child name, age, islands count)"
```
