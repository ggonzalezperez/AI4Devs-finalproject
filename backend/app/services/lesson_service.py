from pathlib import Path

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.child import Child
from app.models.lesson import Lesson
from app.repositories import ai_config as ai_config_repo
from app.repositories import knowledge as knowledge_repo
from app.repositories import lesson as lesson_repo
from app.services.ai_providers import build_generator
from app.services.image_generator import build_image_prompt
from app.services.image_providers import build_image_generator
from app.services.lesson_generator import StubLessonGenerator
from app.services.moderation import check_curiosity

_stub = StubLessonGenerator()


_EXTENSIONES = {"image/webp": "webp", "image/jpeg": "jpg", "image/png": "png"}


def _attach_image(db: Session, cfg, lesson: Lesson, age: int) -> None:
    gen = build_image_generator(cfg)
    try:
        img = gen.generate(build_image_prompt(lesson.concept, age))
    except Exception:
        img = None
    if img is None:
        return
    try:
        media = Path(get_settings().media_dir) / "lessons"
        media.mkdir(parents=True, exist_ok=True)
        # La extensión sigue al formato real. Antes se guardaba todo como .png,
        # y con WebP eso deja ficheros que mienten sobre su contenido: el
        # navegador lo resuelve, pero cualquier herramienta que mire el nombre no.
        ext = _EXTENSIONES.get(img.mime, "png")
        (media / f"{lesson.id}.{ext}").write_bytes(img.data)
        lesson.image_url = f"/media/lessons/{lesson.id}.{ext}"
        db.commit()
    except Exception:
        db.rollback()


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
        follow_ups=g.follow_ups,
    )
    lesson = lesson_repo.create(db, lesson)
    knowledge_repo.ensure_node(db, child.id, lesson.concept, lesson.subject, root_lesson_id=lesson.root_id or lesson.id)
    _attach_image(db, cfg, lesson, child.age)
    return lesson


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
    knowledge_repo.ensure_node(db, child.id, lesson.concept, lesson.subject, root_lesson_id=lesson.root_id or lesson.id)
    _attach_image(db, cfg, lesson, child.age)
    return lesson


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
        "follow_ups": lesson.follow_ups or [],
        "image_url": lesson.image_url,
    }
