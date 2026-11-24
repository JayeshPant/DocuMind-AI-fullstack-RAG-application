from typing import Optional
from fastapi import APIRouter, HTTPException, status
from backend.app.schemas.qa import QAResponse
from backend.app.schemas.history import HistoryListResponse, ClearHistoryResponse
from backend.app.services.history_service import history_service

router = APIRouter(prefix="/api/history", tags=["History"])


@router.get("", response_model=HistoryListResponse)
def get_history(document_id: Optional[str] = None, limit: int = 50):
    records = history_service.list_history(document_id=document_id, limit=limit)
    return {"history": records, "total": len(records)}


@router.get("/{interaction_id}", response_model=QAResponse)
def get_interaction(interaction_id: str):
    record = history_service.get_interaction(interaction_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Interaction '{interaction_id}' not found.")
    return record


@router.delete("", response_model=ClearHistoryResponse)
def clear_history(document_id: Optional[str] = None):
    deleted_count = history_service.clear_history(document_id=document_id)
    scope = f"for document '{document_id}'" if document_id else "globally"
    return {
        "deleted_count": deleted_count,
        "message": f"Successfully cleared {deleted_count} interaction record(s) {scope}.",
    }
