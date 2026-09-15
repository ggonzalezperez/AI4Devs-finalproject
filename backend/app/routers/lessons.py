from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_child
from app.models.child import Child
from app.repositories import lesson as lesson_repo
from app.schemas.answer import AnswerRequest, AnswerResult
from app.schemas.lesson import LessonCreate, LessonRead
from app.services import lesson_service
from app.services.moderation import ModerationError

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.post("", response_model=LessonRead, status_code=status.HTTP_201_CREATED)
def create_lesson(
    payload: LessonCreate,
    child: Child = Depends(get_current_child),
    db: Session = Depends(get_db),
) -> LessonRead:
    try:
        lesson = lesson_service.create_lesson(db, child, payload.curiosity, payload.subject)
    except ModerationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)) from e
    return LessonRead.model_validate(lesson_service.to_read_dict(lesson))


@router.get("/{lesson_id}", response_model=LessonRead)
def get_lesson(
    lesson_id: int,
    child: Child = Depends(get_current_child),
    db: Session = Depends(get_db),
) -> LessonRead:
    lesson = lesson_repo.get_for_child(db, child.id, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lección no encontrada")
    return LessonRead.model_validate(lesson_service.to_read_dict(lesson))


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
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)) from e
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
