from pydantic import BaseModel


class AnswerRequest(BaseModel):
    choice_index: int


class AnswerResult(BaseModel):
    correct: bool
    explanation: str
    concept: str
