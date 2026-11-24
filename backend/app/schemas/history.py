from typing import List, Optional
from pydantic import BaseModel
from backend.app.schemas.qa import QAResponse


class HistoryListResponse(BaseModel):
    history: List[QAResponse]
    total: int


class ClearHistoryResponse(BaseModel):
    deleted_count: int
    message: str
