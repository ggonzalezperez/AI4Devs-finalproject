from pydantic import BaseModel, ConfigDict, Field


class LessonCreate(BaseModel):
    curiosity: str = Field(min_length=2, max_length=300)
    subject: str | None = None


class QuizPublic(BaseModel):
    question: str
    options: list[str]


class LessonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    curiosity: str
    subject: str
    concept: str
    title: str
    body: str
    fun_fact: str
    answered: bool
    quiz: QuizPublic
    follow_ups: list[str] = []
    image_url: str | None = None
