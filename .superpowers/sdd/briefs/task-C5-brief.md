# Task C5: Conectar lesson_service a la config de IA por familia (con fallback al stub)

Backend `backend/`, venv `./.venv/Scripts/python.exe`. Rama `feature-entrega4-ai-config`. SIN push. TDD.

**Objetivo:** `create_lesson` debe usar el **generador del proveedor configurado por la familia** (vía `build_generator`), y si **falla por cualquier motivo** (red, JSON, clave) caer al **stub** para que el niño nunca vea un error. Incrementar `used_count`.

**Files:**
- Modify: `backend/app/services/lesson_service.py`
- Test: `backend/tests/test_lesson_provider_wiring.py`

## Step 1: Modificar `backend/app/services/lesson_service.py`
Reemplaza la línea `_generator: LessonGenerator = StubLessonGenerator()` (y su uso en `create_lesson`) por la integración con la config. El bloque de imports y `create_lesson` debe quedar así (mantén `to_read_dict` y `answer_lesson` tal cual):

```python
from sqlalchemy.orm import Session

from app.models.child import Child
from app.models.lesson import Lesson
from app.repositories import ai_config as ai_config_repo
from app.repositories import knowledge as knowledge_repo  # (si ya estaba importado, no dupliques)
from app.repositories import lesson as lesson_repo
from app.services.ai_providers import build_generator
from app.services.lesson_generator import StubLessonGenerator
from app.services.moderation import check_curiosity

_stub = StubLessonGenerator()


def create_lesson(db: Session, child: Child, curiosity: str, subject: str | None) -> Lesson:
    check_curiosity(curiosity)
    cfg = ai_config_repo.get_or_create(db, child.family_id)
    generator = build_generator(cfg)
    try:
        g = generator.generate(curiosity, age=child.age, subject=subject)
    except Exception:
        # Fallback seguro: el niño nunca ve un fallo del proveedor.
        g = _stub.generate(curiosity, age=child.age, subject=subject)
    try:
        cfg.used_count += 1
        db.commit()
    except Exception:
        db.rollback()
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
```
Nota: elimina el `import` de `LessonGenerator` si queda sin uso (ruff). Conserva `answer_lesson` y `to_read_dict` intactos.

## Step 2: Test `backend/tests/test_lesson_provider_wiring.py`
```python
from datetime import date

from app.models.child import Child
from app.models.family import Family
from app.security import create_token
from app.services import lesson_service
from app.services.lesson_generator import GeneratedLesson


def _child_token(db_session):
    fam = Family(name="F")
    db_session.add(fam)
    db_session.flush()
    child = Child(family_id=fam.id, name="Leo", birthdate=date(2018, 1, 1), pin_hash="x")
    db_session.add(child)
    db_session.commit()
    return create_token(subject=str(child.id), token_type="child")


def test_default_family_uses_stub_and_creates_lesson(client, db_session):
    token = _child_token(db_session)
    r = client.post(
        "/lessons",
        headers={"Authorization": f"Bearer {token}"},
        json={"curiosity": "¿por qué llueve?"},
    )
    assert r.status_code == 201  # provider stub por defecto


def test_provider_failure_falls_back_to_stub(client, db_session, monkeypatch):
    class _Boom:
        def generate(self, *a, **k):
            raise RuntimeError("proveedor caído")

    monkeypatch.setattr(lesson_service, "build_generator", lambda cfg: _Boom())
    token = _child_token(db_session)
    r = client.post(
        "/lessons",
        headers={"Authorization": f"Bearer {token}"},
        json={"curiosity": "¿por qué llueve?"},
    )
    assert r.status_code == 201  # cayó al stub, el niño no ve el error
    assert r.json()["quiz"]["question"]


def test_provider_success_uses_configured_generator(client, db_session, monkeypatch):
    class _Fake:
        def generate(self, curiosity, age, subject):
            return GeneratedLesson(
                subject="arte", concept="c", title="TÍTULO IA", body="b", fun_fact="f",
                quiz_question="¿?", quiz_options=["a", "b", "c"], quiz_correct_index=2,
                quiz_explanation="e",
            )

    monkeypatch.setattr(lesson_service, "build_generator", lambda cfg: _Fake())
    token = _child_token(db_session)
    r = client.post(
        "/lessons",
        headers={"Authorization": f"Bearer {token}"},
        json={"curiosity": "dinosaurios"},
    )
    assert r.status_code == 201
    assert r.json()["title"] == "TÍTULO IA"
    assert r.json()["subject"] == "arte"
```

## Step 3: Tests + suite + ruff
`./.venv/Scripts/python.exe -m pytest tests/test_lesson_provider_wiring.py -v` → PASS. Luego `-q` completa → todo PASS. `./.venv/Scripts/ruff.exe check .` → limpio.

## Step 4: Commit (local, SIN push)
```bash
git add backend/
git commit -m "feat(backend): wire lesson generation to family AI config with safe fallback"
```
