# Task B1a: Lecciones ricas (backend) — prompt adaptado a edad + follow_ups

Backend `backend/`, venv `./.venv/Scripts/python.exe`. Rama `feature-lecciones-ricas`. SIN push (lo hace el controlador). TDD, migración NO destructiva.
Eleva la calidad de las lecciones adaptando la pedagogía de la skill `teach` a niños (ver `Ideas/Chispa - Diseño Lecciones (teach-adaptado).md`). Añade `follow_ups` (preguntas de continuación) para la conversación.

**Files:**
- Modify: `app/services/lesson_generator.py` (GeneratedLesson.follow_ups + stub más rico)
- Modify: `app/services/ai_providers.py` (nuevo system prompt por edad + parse follow_ups + max_tokens)
- Modify: `app/models/lesson.py` (columna follow_ups)
- Modify: `app/schemas/lesson.py` (LessonRead.follow_ups)
- Modify: `app/services/lesson_service.py` (persistir + to_read_dict)
- Migración Alembic (add_column, no destructiva)
- Tests

## Step 1: `app/services/lesson_generator.py`
- Cambia el import: `from dataclasses import dataclass, field`
- En `GeneratedLesson`, añade al final: `follow_ups: list[str] = field(default_factory=list)`
- En `StubLessonGenerator.generate`, enriquece el `body` y añade `follow_ups`. Sustituye el `body`, `fun_fact` y el `return` por:
```python
        body = (
            f"¡Buena pregunta! Vamos a descubrir «{clean}» juntos. Para tus {age} años, lo "
            f"importante es observar el mundo y atreverte a preguntar. Cada cosa que te "
            f"sorprende esconde un porqué, y cada porqué que descubres se convierte en una "
            f"isla nueva de tu archipiélago. ¿Sigues la pista de esta curiosidad?"
        )
        fun_fact = f"¿Sabías que casi nadie se detiene a pensar en «{clean}»? ¡Tú sí, y eso es de exploradores!"
        return GeneratedLesson(
            subject=chosen,
            concept=concept,
            title=title,
            body=body,
            fun_fact=fun_fact,
            quiz_question=f"¿Qué es lo mejor para descubrir sobre «{clean}»?",
            quiz_options=["Adivinar sin mirar", "Observar y preguntar", "Quedarme quieto"],
            quiz_correct_index=1,
            quiz_explanation="Observar y preguntar es la mejor forma de descubrir.",
            follow_ups=[
                f"¿Por qué ocurre «{clean}»?",
                "¿Me das un ejemplo divertido?",
                "¿Qué más puedo descubrir de esto?",
            ],
        )
```
(Las 3 opciones del quiz mantienen longitud parecida, según la regla.)

## Step 2: `app/services/ai_providers.py`
Sustituye `_system_prompt` (y añade `_age_band`) por:
```python
def _age_band(age: int) -> str:
    if age <= 5:
        return (
            "Edad 3-5 (aún no lee bien): 2 o 3 frases muy cortas, palabras muy sencillas y "
            "algún sonido divertido (¡pum!, ¡splash!). Compara con cosas que ve cada día "
            "(juguetes, animales, comida). Quiz muy fácil."
        )
    if age <= 8:
        return (
            "Edad 6-8: 4 a 6 frases. Una analogía clara del día a día y un porqué sencillo. "
            "Quiz de dificultad media."
        )
    return (
        "Edad 9-12: 6 a 9 frases. Puedes introducir UNA palabra nueva y explicarla. Muestra "
        "una causa y su efecto, y propón un pequeño reto del mundo real. Quiz algo más exigente."
    )


def _system_prompt(age: int) -> str:
    return (
        f"Eres Chispa, un guía cálido y curioso que ayuda a un niño de {age} años a resolver "
        "su curiosidad CON CONOCIMIENTO. Hablas como alguien mayor que sabe mucho y disfruta "
        "enseñando: cercano, con asombro, nunca por encima del niño.\n"
        "Pedagogía:\n"
        "- Ancla TODO a la pregunta del niño (su curiosidad es la misión).\n"
        "- Enseña UNA sola idea clara (un '¡ajá!'), sin abrumar.\n"
        "- Usa una analogía de su mundo (juguetes, animales, comida, juegos).\n"
        "- Añade un dato sorprendente que despierte más ganas de saber.\n"
        "- Termina invitando a seguir preguntando.\n"
        "- Sé veraz y apropiado a su edad; no inventes.\n"
        f"Estilo para esta edad: {_age_band(age)}\n"
        "El quiz es práctica de recuerdo: 3 opciones de longitud parecida (número de palabras "
        "similar); ninguna debe destacar por formato o longitud; solo una correcta.\n"
        "'follow_ups' son 2 o 3 preguntas cortas y atractivas, en la voz del niño, que podría "
        "hacer a continuación para profundizar.\n"
        "Responde SOLO con JSON válido, sin texto adicional ni markdown. Forma exacta: "
        '{"subject": "ciencia|matematicas|lenguaje|arte|cultura", "concept": "...", '
        '"title": "...", "body": "...", "fun_fact": "...", '
        '"follow_ups": ["...", "...", "..."], '
        '"quiz": {"question": "...", "options": ["a","b","c"], "correct_index": 0, "explanation": "..."}}'
    )
```
En `_parse_lesson`, antes del `return`, parsea follow_ups y pásalo al constructor:
```python
    raw_fu = data.get("follow_ups")
    follow_ups = [str(x) for x in raw_fu][:3] if isinstance(raw_fu, list) else []
```
y añade `follow_ups=follow_ups,` al `GeneratedLesson(...)`.
En `ClaudeGenerator.generate`, cambia `"max_tokens": 800` por `"max_tokens": 1400`.

## Step 3: `app/models/lesson.py`
Añade la columna (tras `quiz_explanation` o junto a las demás):
```python
    follow_ups: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
```
(`JSON` ya está importado.)

## Step 4: `app/schemas/lesson.py`
En `LessonRead`, añade: `follow_ups: list[str] = []`

## Step 5: `app/services/lesson_service.py`
- En `create_lesson`, al construir `Lesson(...)`, añade: `follow_ups=g.follow_ups,`
- En `to_read_dict`, añade al dict: `"follow_ups": lesson.follow_ups or [],`

## Step 6: Migración
- `./.venv/Scripts/alembic.exe revision --autogenerate -m "lesson follow_ups column"`
- Verifica que SOLO añade `op.add_column('lessons', sa.Column('follow_ups', ... ))` (+ downgrade drop_column). Si hay drops/alters sobre otras tablas, DETENTE y reporta DONE_WITH_CONCERNS sin aplicar.
- Aplica: `./.venv/Scripts/alembic.exe upgrade head`.
(La columna es nullable → las filas existentes quedan NULL y `to_read_dict` las convierte en `[]`.)

## Step 7: Tests
- Stub: añade/actualiza un test que verifique `g.follow_ups` no vacío y `len(g.follow_ups) <= 3`.
- API: en el test de creación/lectura de lección (mira `tests/test_lessons.py` o equivalente y reutiliza su patrón de token de niño), añade que la respuesta incluye `"follow_ups"` y es una lista.
- Mantén verdes los tests existentes. Ejecuta `./.venv/Scripts/python.exe -m pytest -q` → todo PASS.

## Step 8: Commit (local, SIN push)
```bash
git add backend/
git commit -m "feat(backend): richer age-adapted lessons (teach-based prompt + follow_ups)"
```
