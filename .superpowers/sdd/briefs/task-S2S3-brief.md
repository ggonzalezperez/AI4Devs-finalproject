# Task S2+S3: Endpoints de cuentos (niño crea/lee aprobados; familia lista/aprueba/edita/rechaza)

Backend `backend/`, venv `./.venv/Scripts/python.exe`. Rama `feature-cuentos`. SIN push. TDD.
Depende de S1 (modelo `Story`, `story_repo`, `story_service.create_story`) que YA está en la rama.

Reglas de negocio:
- El niño crea un cuento → queda `pending` (lo generan los conceptos de su grafo).
- El niño SOLO puede leer cuentos `approved` (la lista y el detalle ocultan pending/rejected → 404).
- La familia ve TODOS los cuentos de sus hijos (con filtro opcional por estado) y puede aprobar, rechazar y editar (título/cuerpo) al revisar.

**Files:**
- Create: `backend/app/schemas/story.py`
- Create: `backend/app/routers/stories.py`
- Modify: `backend/app/services/story_service.py` (añadir `review_story`)
- Modify: `backend/app/main.py` (registrar router)
- Test: `backend/tests/test_story_api.py`

## Step 1: `backend/app/schemas/story.py`
```python
from typing import Literal

from pydantic import BaseModel, ConfigDict


class StoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    status: str


class StoryReview(BaseModel):
    action: Literal["approve", "reject"]
    title: str | None = None
    body: str | None = None
```

## Step 2: Añadir a `backend/app/services/story_service.py`
El archivo ya tiene los imports de `Session`, `Child`, `Story`, repos y `_generator`, y `create_story`. Añade al final del archivo:
```python
def review_story(
    db: Session,
    story: Story,
    action: str,
    title: str | None = None,
    body: str | None = None,
) -> Story:
    if title is not None:
        story.title = title
    if body is not None:
        story.body = body
    story.status = "approved" if action == "approve" else "rejected"
    story.reviewed_at = _utcnow()
    db.commit()
    db.refresh(story)
    return story
```
Para `_utcnow`: el modelo `Story` ya define `_utcnow` en `app/models/story.py`. Importa esa misma función al principio del servicio (junto a los otros imports), añadiendo:
```python
from app.models.story import Story, _utcnow
```
(si ya hay `from app.models.story import Story`, sustitúyelo por la línea de arriba — NO crees una segunda fuente de tiempo).

## Step 3: `backend/app/routers/stories.py`
Router único con rutas de niño (`/me/stories`) y de familia (`/family/stories`); cada ruta usa su propia dependencia de auth (igual que los routers existentes). Sin `prefix` (rutas completas).
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_child, get_current_family_user
from app.models.child import Child
from app.models.family import User
from app.repositories import story as story_repo
from app.schemas.story import StoryRead, StoryReview
from app.services import story_service

router = APIRouter(tags=["stories"])


# ---- Niño ----

@router.post("/me/stories", response_model=StoryRead, status_code=status.HTTP_201_CREATED)
def create_my_story(
    child: Child = Depends(get_current_child),
    db: Session = Depends(get_db),
) -> StoryRead:
    story = story_service.create_story(db, child)
    return StoryRead.model_validate(story)


@router.get("/me/stories", response_model=list[StoryRead])
def my_stories(
    child: Child = Depends(get_current_child),
    db: Session = Depends(get_db),
) -> list[StoryRead]:
    stories = story_repo.list_for_child(db, child.id, status="approved")
    return [StoryRead.model_validate(s) for s in stories]


@router.get("/me/stories/{story_id}", response_model=StoryRead)
def my_story(
    story_id: int,
    child: Child = Depends(get_current_child),
    db: Session = Depends(get_db),
) -> StoryRead:
    story = story_repo.get_for_child(db, child.id, story_id)
    if story is None or story.status != "approved":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuento no encontrado")
    return StoryRead.model_validate(story)


# ---- Familia ----

@router.get("/family/stories", response_model=list[StoryRead])
def family_stories(
    status_filter: str | None = None,
    user: User = Depends(get_current_family_user),
    db: Session = Depends(get_db),
) -> list[StoryRead]:
    stories = story_repo.list_for_family(db, user.family_id, status=status_filter)
    return [StoryRead.model_validate(s) for s in stories]


@router.put("/family/stories/{story_id}", response_model=StoryRead)
def review_family_story(
    story_id: int,
    payload: StoryReview,
    user: User = Depends(get_current_family_user),
    db: Session = Depends(get_db),
) -> StoryRead:
    story = story_repo.get_for_family(db, user.family_id, story_id)
    if story is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuento no encontrado")
    story = story_service.review_story(db, story, payload.action, payload.title, payload.body)
    return StoryRead.model_validate(story)
```
Nota: el query param se llama `status_filter` (no `status`, que colisiona con `fastapi.status`). En la URL será `/family/stories?status_filter=pending`.

## Step 4: Registrar en `backend/app/main.py`
Añade `stories` al import de routers y `app.include_router(stories.router)`:
```python
from app.routers import ai_config, auth, children, lessons, me, stories
```
y, tras `app.include_router(ai_config.router)`:
```python
app.include_router(stories.router)
```

## Step 5: Test `backend/tests/test_story_api.py`
```python
from datetime import date

from app.models.child import Child
from app.models.family import Family, User
from app.security import create_token


def _setup(db_session):
    fam = Family(name="F")
    db_session.add(fam)
    db_session.flush()
    user = User(family_id=fam.id, email="p@e.com", password_hash="x")
    child = Child(family_id=fam.id, name="Leo", birthdate=date(2018, 1, 1), pin_hash="x")
    db_session.add_all([user, child])
    db_session.commit()
    child_h = {"Authorization": f"Bearer {create_token(subject=str(child.id), token_type='child')}"}
    fam_h = {"Authorization": f"Bearer {create_token(subject=str(user.id), token_type='family')}"}
    return child, child_h, fam_h


def test_child_creates_pending_story(client, db_session):
    _child, child_h, _fam_h = _setup(db_session)
    r = client.post("/me/stories", headers=child_h)
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "pending"
    assert "Leo" in body["body"]


def test_child_only_sees_approved(client, db_session):
    _child, child_h, fam_h = _setup(db_session)
    sid = client.post("/me/stories", headers=child_h).json()["id"]
    # Pendiente: no aparece en su lista ni en el detalle
    assert client.get("/me/stories", headers=child_h).json() == []
    assert client.get(f"/me/stories/{sid}", headers=child_h).status_code == 404
    # La familia lo aprueba
    client.put(f"/family/stories/{sid}", headers=fam_h, json={"action": "approve"})
    lst = client.get("/me/stories", headers=child_h).json()
    assert len(lst) == 1 and lst[0]["id"] == sid
    assert client.get(f"/me/stories/{sid}", headers=child_h).status_code == 200


def test_family_lists_and_reviews(client, db_session):
    _child, child_h, fam_h = _setup(db_session)
    sid = client.post("/me/stories", headers=child_h).json()["id"]
    # La familia ve el pendiente
    pend = client.get("/family/stories", headers=fam_h, params={"status_filter": "pending"}).json()
    assert len(pend) == 1 and pend[0]["id"] == sid
    # Edita y aprueba en un solo paso
    r = client.put(
        f"/family/stories/{sid}",
        headers=fam_h,
        json={"action": "approve", "title": "Nuevo título"},
    )
    assert r.status_code == 200
    assert r.json()["title"] == "Nuevo título"
    assert r.json()["status"] == "approved"


def test_family_rejects_story(client, db_session):
    _child, child_h, fam_h = _setup(db_session)
    sid = client.post("/me/stories", headers=child_h).json()["id"]
    client.put(f"/family/stories/{sid}", headers=fam_h, json={"action": "reject"})
    # Rechazado: no aparece para el niño
    assert client.get("/me/stories", headers=child_h).json() == []
    rej = client.get("/family/stories", headers=fam_h, params={"status_filter": "rejected"}).json()
    assert len(rej) == 1


def test_auth_guards(client, db_session):
    _child, child_h, fam_h = _setup(db_session)
    # Niño no puede usar endpoints de familia y viceversa (tipo de token inválido → 401)
    assert client.get("/family/stories", headers=child_h).status_code == 401
    assert client.post("/me/stories", headers=fam_h).status_code == 401
    # Sin token → 401
    assert client.get("/me/stories").status_code == 401
    assert client.get("/family/stories").status_code == 401


def test_family_cannot_review_other_familys_story(client, db_session):
    _child, child_h, _fam_h = _setup(db_session)
    sid = client.post("/me/stories", headers=child_h).json()["id"]
    # Otra familia
    other = Family(name="Otra")
    db_session.add(other)
    db_session.flush()
    other_user = User(family_id=other.id, email="o@e.com", password_hash="x")
    db_session.add(other_user)
    db_session.commit()
    other_h = {"Authorization": f"Bearer {create_token(subject=str(other_user.id), token_type='family')}"}
    assert client.put(f"/family/stories/{sid}", headers=other_h, json={"action": "approve"}).status_code == 404
```

## Step 6: Tests + suite + lint
- `./.venv/Scripts/python.exe -m pytest tests/test_story_api.py -v` → PASS.
- Suite completa `./.venv/Scripts/python.exe -m pytest -q` → todo PASS.
- `./.venv/Scripts/ruff.exe check app tests` → limpio (si no existe ruff en venv, omite).

## Step 7: Commit (local, SIN push)
```bash
git add backend/
git commit -m "feat(backend): story endpoints (child create/read approved, family list/review)"
```
