from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


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
    follow_ups: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    answered: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    parent_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    root_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
