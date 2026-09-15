# Task B2a: Conversación tipo chat (backend) — hilos + contexto + islas automáticas

Backend `backend/`, venv `./.venv/Scripts/python.exe`. Rama `feature-lecciones-ricas` (seguimos en ella). SIN push. TDD, migración NO destructiva.
Convierte las lecciones en una **conversación**: cada repregunta continúa el MISMO hilo con contexto. Las **islas se crean solas por detrás** (al generar cada turno), sin depender del quiz. El quiz sigue existiendo por turno (opcional; el frontend lo gestiona) y al acertar sube la maestría.

Decisiones de diseño:
- Un **hilo** = lección raíz + sus turnos. Enlace por `parent_id` y `root_id` en `lessons` (Integer nullable, sin FK explícita para simplificar la migración en SQLite). Raíz: ambos NULL.
- **Contexto**: el generador recibe el historial (preguntas+respuestas previas) para continuar coherente.
- **Islas automáticas**: al crear cualquier turno se asegura el nodo de conocimiento (sin subir maestría). El quiz correcto sí sube maestría (comportamiento actual).

**Files:**
- Modify: `app/models/lesson.py` (parent_id, root_id)
- Modify: `app/services/lesson_generator.py` (param `history`)
- Modify: `app/services/ai_providers.py` (param `history` en todos los adaptadores + `_user_prompt`)
- Modify: `app/repositories/knowledge.py` (`ensure_node`)
- Modify: `app/repositories/lesson.py` (`list_thread`)
- Modify: `app/services/lesson_service.py` (`create_lesson` asegura isla; nuevo `continue_conversation`)
- Modify: `app/routers/lessons.py` (POST `/{id}/ask`, GET `/{id}/thread`)
- Migración Alembic (2 columnas, no destructiva)
- Tests

## Step 1: `app/models/lesson.py`
Añade tras `created_at` (o junto a las columnas), usando `Integer` (ya importado):
```python
    parent_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    root_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
```

## Step 2: `app/services/lesson_generator.py` — historial
- En el `Protocol` `LessonGenerator`, cambia la firma:
```python
    def generate(
        self, curiosity: str, age: int, subject: str | None,
        history: list[tuple[str, str]] | None = None,
    ) -> GeneratedLesson: ...
```
- En `StubLessonGenerator.generate`, añade el mismo parámetro `history: list[tuple[str, str]] | None = None` al final. Si `history` no está vacío, antepón al `body` una frase de continuidad:
```python
        if history:
            body = "Sigamos con nuestra conversación. " + body
```
(coloca esa línea justo después de construir `body`, antes del `return`).

## Step 3: `app/services/ai_providers.py` — historial + prompt
- Cambia `_user_prompt` para aceptar historial y construir el contexto:
```python
def _user_prompt(curiosity: str, subject: str | None, history: list[tuple[str, str]] | None = None) -> str:
    if history:
        convo = "\n".join(f"Niño: {q}\nChispa: {a}" for q, a in history)
        return (
            "Conversación hasta ahora:\n" + convo + "\n\n"
            f"El niño continúa preguntando: «{curiosity}». Responde SIGUIENDO el hilo, "
            "sin repetir lo ya dicho, profundizando un poco más. Genera la lección en JSON."
        )
    extra = f" Teje la materia '{subject}'." if subject in SUBJECTS else ""
    return f"Curiosidad del niño: «{curiosity}».{extra} Genera la lección en JSON."
```
- En CADA adaptador (`ClaudeGenerator`, `OllamaGenerator`, `OpenAICompatGenerator`, `GeminiGenerator`), añade el parámetro `history: list[tuple[str, str]] | None = None` a `generate(...)` y pásalo: sustituye `_user_prompt(curiosity, subject)` por `_user_prompt(curiosity, subject, history)` en los 4.

## Step 4: `app/repositories/knowledge.py` — ensure_node
Añade (no incrementa maestría):
```python
def ensure_node(db: Session, child_id: int, concept: str, subject: str) -> KnowledgeNode:
    existing = db.execute(
        select(KnowledgeNode).where(
            KnowledgeNode.child_id == child_id, KnowledgeNode.concept == concept
        )
    ).scalar_one_or_none()
    if existing:
        return existing
    node = KnowledgeNode(child_id=child_id, concept=concept, subject=subject)
    db.add(node)
    db.commit()
    db.refresh(node)
    return node
```

## Step 5: `app/repositories/lesson.py` — list_thread
Añade (importa `select` y `or_` de sqlalchemy arriba):
```python
from sqlalchemy import or_, select

def list_thread(db: Session, child_id: int, lesson_id: int) -> list[Lesson]:
    anchor = get_for_child(db, child_id, lesson_id)
    if anchor is None:
        return []
    root_id = anchor.root_id or anchor.id
    rows = db.execute(
        select(Lesson)
        .where(
            Lesson.child_id == child_id,
            or_(Lesson.id == root_id, Lesson.root_id == root_id),
        )
        .order_by(Lesson.id)
    ).scalars().all()
    return list(rows)
```

## Step 6: `app/services/lesson_service.py`
- En `create_lesson`, tras `lesson = lesson_repo.create(db, lesson)` y antes del `return`, asegura la isla en segundo plano:
```python
    knowledge_repo.ensure_node(db, child.id, lesson.concept, lesson.subject)
    return lesson
```
(cambia el `return lesson_repo.create(db, lesson)` por las dos líneas: crear, asegurar nodo, return.)
- Añade la función de continuación:
```python
def continue_conversation(db: Session, child: Child, parent: Lesson, question: str) -> Lesson:
    check_curiosity(question)
    root_id = parent.root_id or parent.id
    thread = lesson_repo.list_thread(db, child.id, root_id)
    history = [(t.curiosity, t.body) for t in thread]
    cfg = ai_config_repo.get_or_create(db, child.family_id)
    generator = build_generator(cfg)
    try:
        g = generator.generate(question, age=child.age, subject=None, history=history)
    except Exception:
        g = _stub.generate(question, age=child.age, subject=None, history=history)
    try:
        cfg.used_count += 1
        db.commit()
    except Exception:
        db.rollback()
    lesson = Lesson(
        child_id=child.id,
        curiosity=question,
        subject=g.subject,
        concept=g.concept,
        title=g.title,
        body=g.body,
        fun_fact=g.fun_fact,
        quiz_question=g.quiz_question,
        quiz_options=g.quiz_options,
        quiz_correct_index=g.quiz_correct_index,
        quiz_explanation=g.quiz_explanation,
        follow_ups=g.follow_ups,
        parent_id=parent.id,
        root_id=root_id,
    )
    lesson = lesson_repo.create(db, lesson)
    knowledge_repo.ensure_node(db, child.id, lesson.concept, lesson.subject)
    return lesson
```

## Step 7: `app/routers/lessons.py` — endpoints
Añade (reutiliza `LessonCreate` para el body de ask; sus campos son `curiosity` + `subject`, usamos `curiosity`):
```python
@router.post("/{lesson_id}/ask", response_model=LessonRead, status_code=status.HTTP_201_CREATED)
def ask_followup(
    lesson_id: int,
    payload: LessonCreate,
    child: Child = Depends(get_current_child),
    db: Session = Depends(get_db),
) -> LessonRead:
    parent = lesson_repo.get_for_child(db, child.id, lesson_id)
    if parent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lección no encontrada")
    try:
        lesson = lesson_service.continue_conversation(db, child, parent, payload.curiosity)
    except ModerationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return LessonRead.model_validate(lesson_service.to_read_dict(lesson))


@router.get("/{lesson_id}/thread", response_model=list[LessonRead])
def lesson_thread(
    lesson_id: int,
    child: Child = Depends(get_current_child),
    db: Session = Depends(get_db),
) -> list[LessonRead]:
    turns = lesson_repo.list_thread(db, child.id, lesson_id)
    if not turns:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lección no encontrada")
    return [LessonRead.model_validate(lesson_service.to_read_dict(t)) for t in turns]
```

## Step 8: Migración
- `./.venv/Scripts/alembic.exe revision --autogenerate -m "lesson conversation threading"`
- Verifica que SOLO añade `op.add_column('lessons', ...)` para `parent_id` y `root_id` (+ índice de root_id + downgrade). Si hay drops/alters sobre otras tablas, DETENTE y reporta DONE_WITH_CONCERNS sin aplicar.
- Aplica: `./.venv/Scripts/alembic.exe upgrade head`.

## Step 9: Tests (`tests/test_lessons.py` o nuevo `tests/test_conversation.py`)
Reutiliza el patrón de token de niño existente. Cubre:
- Crear lección raíz → existe su isla automáticamente (GET /me/knowledge tiene 1 nodo SIN responder el quiz).
- POST `/lessons/{root}/ask` con otra pregunta → 201, devuelve un turno nuevo; GET `/lessons/{root}/thread` devuelve 2 turnos en orden (raíz primero).
- El turno hijo tiene `parent_id`/`root_id` apuntando a la raíz (puedes comprobarlo indirectamente: el thread del hijo y el de la raíz coinciden).
- `ensure_node` NO sube maestría (crear 2 turnos con el mismo concepto deja mastery sin incrementar respecto a crear 1); el quiz correcto sí.
- Mantén verdes los tests existentes. `./.venv/Scripts/python.exe -m pytest -q` → todo PASS.

## Step 10: Commit (local, SIN push)
```bash
git add backend/
git commit -m "feat(backend): conversational lesson threads (context-aware follow-ups + auto islands)"
```
