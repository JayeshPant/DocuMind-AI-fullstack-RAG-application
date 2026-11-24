from typing import Optional, List
from pydantic import BaseModel, Field


class SourceExcerpt(BaseModel):
    page: int
    content: str


class AskRequest(BaseModel):
    document_id: str = Field(..., description="The ID of the document to query")
    question: str = Field(..., min_length=1, max_length=2000, description="The user question")


class AskByNumberRequest(BaseModel):
    document_id: str = Field(..., description="The ID of the document to search")
    question_number: int = Field(..., ge=1, le=10000, description="The positive question number (e.g. 1, 5, 10)")


class QAResponse(BaseModel):
    interaction_id: str
    document_id: str
    document_filename: str
    question_mode: str  # "free_text" or "by_number"
    requested_question_number: Optional[int] = None
    detected_question_text: Optional[str] = None
    question: str
    answer: str
    sources: List[SourceExcerpt] = []
    timestamp: str
