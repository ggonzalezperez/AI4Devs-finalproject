# Task A1: Modelos Lesson y KnowledgeNode + dependencia get_current_child + migración

Usa el código EXACTO. Sigue TDD. Backend en `backend/`, venv: `./.venv/Scripts/python.exe`. Rama `feature-entrega3-nucleo`.

**Files:**
- Create: `backend/app/models/lesson.py`
- Create: `backend/app/models/knowledge.py`
- Modify: `backend/app/models/__init__.py`
- Modify: `backend/app/deps.py` (añadir `get_current_child` al final)
- Test: `backend/tests/test_models_nucleo.py`
- Test: `backend/tests/test_deps_child.py`
- Migración Alembic autogenerada (no destructiva).

## Step 1: Crear `backend/app/models/lesson.py`

```python
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True)
    child_id: Mapped[int] = mapped_column(ForeignKey("children.id"), index=True)
    curiosity: Mapped[str] = mapped_column(String(300))
    subject: Mapped[str] = mapped_column(String(40))
    concept: Mapped[str] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    fun_fact: Mapped[str] = mapped_column(Text)
    quiz_question: Mapped[str] = mapped_column(String(300))
    quiz_options: Mapped[list] = mapped_column(JSON)
    quiz_correct_index: Mapped[int] = mapped_column(Integer)
    quiz_explanation: Mapped[str] = mapped_column(Text)
    answered: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
```

## Step 2: Crear `backend/app/models/knowledge.py`

```python
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    child_id: Mapped[int] = mapped_column(ForeignKey("children.id"), index=True)
    concept: Mapped[str] = mapped_column(String(120))
    subject: Mapped[str] = mapped_column(String(40))
    mastery: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
```

## Step 3: Reemplazar `backend/app/models/__init__.py`

```python
from app.models.family import Family, User  # noqa: F401
from app.models.child import Child  # noqa: F401
from app.models.lesson import Lesson  # noqa: F401
from app.models.knowledge import KnowledgeNode  # noqa: F401
```

## Step 4: Añadir `get_current_child` al final de `backend/app/deps.py`

(El archivo ya importa `jwt`, `Depends`, `HTTPException`, `status`, `HTTPAuthorizationCredentials`, `bearer`, `get_db`, `decode_token`, `Session`. Añade el import de `Child` y la función.)

```python
from app.models.child import Child


def get_current_child(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> Child:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Falta token")
    try:
        payload = decode_token(credentials.credentials)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    if payload.get("type") != "child":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Tipo de token inválido"
        )
    child = db.get(Child, int(payload["sub"]))
    if child is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Niño no encontrado")
    return child
```

## Step 5: Crear test `backend/tests/test_models_nucleo.py`

```python
from datetime import date

from app.models.child import Child
from app.models.family import Family
from app.models.knowledge import KnowledgeNode
from app.models.lesson import Lesson


def test_create_lesson_and_node(db_session):
    fam = Family(name="F")
    db_session.add(fam)
    db_session.flush()
    child = Child(family_id=fam.id, name="Leo", birthdate=date(2018, 1, 1), pin_hash="x")
    db_session.add(child)
    db_session.flush()

    lesson = Lesson(
        child_id=child.id, curiosity="¿por qué flotan los barcos?", subject="ciencia",
        concept="flotabilidad", title="Los barcos", body="...", fun_fact="...",
        quiz_question="¿Qué empuja al barco?", quiz_options=["viento", "agua", "sol"],
        quiz_correct_index=1, quiz_explanation="El agua empuja hacia arriba.",
    )
    node = KnowledgeNode(child_id=child.id, concept="flotabilidad", subject="ciencia")
    db_session.add_all([lesson, node])
    db_session.commit()

    assert lesson.id is not None
    assert lesson.answered is False
    assert lesson.quiz_options[1] == "agua"
    assert node.mastery == 1
```

## Step 6: Crear test `backend/tests/test_deps_child.py`

```python
from app.security import create_token, decode_token


def test_child_token_type_is_child():
    token = create_token(subject="5", token_type="child")
    payload = decode_token(token)
    assert payload["type"] == "child"
    assert payload["sub"] == "5"
```

## Step 7: Ejecutar tests

`./.venv/Scripts/python.exe -m pytest tests/test_models_nucleo.py tests/test_deps_child.py -v` → PASS.

## Step 8: Generar y revisar migración (NO destructiva)

```bash
./.venv/Scripts/alembic.exe revision --autogenerate -m "nucleo: lessons and knowledge_nodes"
```
Abre el archivo generado en `alembic/versions/` y confirma que SOLO contiene `op.create_table("lessons", ...)` y `op.create_table("knowledge_nodes", ...)` (+ índices). Si aparece cualquier `op.drop_table`, `op.drop_column` o `op.drop_index` sobre tablas existentes (families/users/children), DETENTE y reporta DONE_WITH_CONCERNS sin aplicar. Si es limpia:
```bash
./.venv/Scripts/alembic.exe upgrade head
```

## Step 9: Suite completa del backend

`./.venv/Scripts/python.exe -m pytest -q` → todo PASS.

## Step 10: Commit (local, SIN push)

```bash
git add backend/
git commit -m "feat(backend): nucleo models (Lesson, KnowledgeNode) + child auth dependency"
```
