from pydantic import BaseModel
from typing import Any


# ---- Existing ----
class GenerateQuestionsResponse(BaseModel):
    question_type: str
    count: int
    questions: list


class ExplainRequest(BaseModel):
    question: str
    correct_answer: str


# ---- New: Documents ----
class DocumentCreate(BaseModel):
    title: str


class DocumentOut(BaseModel):
    id: int
    title: str
    created_at: str  # serialize as ISO string

    class Config:
        from_attributes = True


# ---- New: Cards ----
class CardsBulkIn(BaseModel):
    cards: list[dict[str, Any]]


class CardOut(BaseModel):
    id: int
    document_id: int
    type: str
    question: str
    options: list[str] | None = None
    correct_answer: str | None = None
    answer: str | None = None
    explanation: str | None = None

    class Config:
        from_attributes = True


# ---- New: Progress ----
class ProgressIn(BaseModel):
    card_id: int
    correct: bool


class ProgressOut(BaseModel):
    card_id: int
    times_seen: int
    times_correct: int
    last_seen_at: str | None

    class Config:
        from_attributes = True
