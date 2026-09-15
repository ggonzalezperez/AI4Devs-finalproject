# Task A2: LessonGenerator (interfaz) + StubLessonGenerator + moderación stub

Usa el código EXACTO. TDD. Backend `backend/`, venv `./.venv/Scripts/python.exe`. Rama `feature-entrega3-nucleo`. SIN deps nuevas. SIN push.

**Files:**
- Create: `backend/app/services/lesson_generator.py`
- Create: `backend/app/services/moderation.py`
- Test: `backend/tests/test_lesson_generator.py`
- Test: `backend/tests/test_moderation.py`

## Step 1: Test `backend/tests/test_lesson_generator.py`

```python
from app.services.lesson_generator import SUBJECTS, StubLessonGenerator


def test_stub_is_deterministic_and_well_formed():
    gen = StubLessonGenerator()
    a = gen.generate("¿por qué llueve?", age=7, subject=None)
    b = gen.generate("¿por qué llueve?", age=7, subject=None)
    assert a.subject == b.subject
    assert a.subject in SUBJECTS
    assert len(a.quiz_options) == 3
    assert 0 <= a.quiz_correct_index < 3
    assert a.concept
    assert "llueve" in a.body.lower() or "llueve" in a.title.lower()


def test_stub_respects_forced_subject():
    gen = StubLessonGenerator()
    g = gen.generate("dinosaurios", age=8, subject="arte")
    assert g.subject == "arte"
```

## Step 2: Ver fallar
`./.venv/Scripts/python.exe -m pytest tests/test_lesson_generator.py -v` → FAIL.

## Step 3: Crear `backend/app/services/lesson_generator.py`

```python
from dataclasses import dataclass
from typing import Protocol

SUBJECTS = ["ciencia", "matematicas", "lenguaje", "arte", "cultura"]


@dataclass
class GeneratedLesson:
    subject: str
    concept: str
    title: str
    body: str
    fun_fact: str
    quiz_question: str
    quiz_options: list[str]
    quiz_correct_index: int
    quiz_explanation: str


class LessonGenerator(Protocol):
    def generate(self, curiosity: str, age: int, subject: str | None) -> GeneratedLesson: ...


class StubLessonGenerator:
    """Generador determinista de marcador de posición (sin IA externa).

    Costura para un adaptador real (LLM) que implementará la misma interfaz.
    """

    def generate(self, curiosity: str, age: int, subject: str | None) -> GeneratedLesson:
        clean = curiosity.strip()
        chosen = subject if subject in SUBJECTS else SUBJECTS[len(clean) % len(SUBJECTS)]
        concept = clean.rstrip("?¿! ").lower()[:120] or "descubrimiento"
        title = clean[:1].upper() + clean[1:] if clean else "Tu curiosidad"
        body = (
            f"Vamos a explorar «{clean}». Para tus {age} años, lo importante es observar y "
            f"hacer preguntas. Cada respuesta abre una isla nueva en tu archipiélago."
        )
        fun_fact = f"Dato curioso: casi nadie se pregunta «{clean}», ¡y es fascinante!"
        return GeneratedLesson(
            subject=chosen,
            concept=concept,
            title=title,
            body=body,
            fun_fact=fun_fact,
            quiz_question=f"¿Qué es lo mejor para aprender sobre «{clean}»?",
            quiz_options=["Adivinar sin mirar", "Observar y preguntar", "No hacer nada"],
            quiz_correct_index=1,
            quiz_explanation="Observar y preguntar es la mejor forma de descubrir.",
        )
```

## Step 4: Ver pasar
`./.venv/Scripts/python.exe -m pytest tests/test_lesson_generator.py -v` → PASS.

## Step 5: Test `backend/tests/test_moderation.py`

```python
import pytest

from app.services.moderation import ModerationError, check_curiosity


def test_allows_normal_curiosity():
    check_curiosity("¿por qué el cielo es azul?")


def test_blocks_inappropriate_term():
    with pytest.raises(ModerationError):
        check_curiosity("quiero ver armas y violencia explícita")
```

## Step 6: Crear `backend/app/services/moderation.py`

```python
class ModerationError(Exception):
    pass


# Lista mínima de bloqueo (placeholder). Un servicio real de moderación
# implementará esta misma función con más cobertura.
_BLOCKLIST = [
    "arma", "armas", "violencia", "droga", "drogas", "sexo", "sexual",
    "suicid", "matar", "porno",
]


def check_curiosity(text: str) -> None:
    lowered = text.lower()
    if any(term in lowered for term in _BLOCKLIST):
        raise ModerationError("Esta pregunta es mejor verla con un adulto.")
```

## Step 7: Tests moderación
`./.venv/Scripts/python.exe -m pytest tests/test_moderation.py -v` → PASS.

## Step 8: Commit (local, SIN push)
```bash
git add backend/
git commit -m "feat(backend): LessonGenerator interface + deterministic stub + moderation stub"
```
