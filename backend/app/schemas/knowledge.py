from pydantic import BaseModel, ConfigDict


class KnowledgeNodeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    concept: str
    subject: str
    mastery: int
    root_lesson_id: int | None = None


class Suggestion(BaseModel):
    curiosity: str
    emoji: str


class ChildProfile(BaseModel):
    name: str
    age: int
    islands: int
    avatar: str
    avatar_image_url: str | None = None
