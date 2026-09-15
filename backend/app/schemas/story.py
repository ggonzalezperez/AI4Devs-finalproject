from typing import Literal

from pydantic import BaseModel, ConfigDict


class StoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    status: str


class StoryReview(BaseModel):
    action: Literal["approve", "reject"]
    title: str | None = None
    body: str | None = None
