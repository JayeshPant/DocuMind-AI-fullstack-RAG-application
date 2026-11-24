from fastapi import APIRouter
from backend.app.config import settings
from backend.app.database import db_manager
from backend.app.services.document_service import document_service

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health")
def health_check():
    docs = document_service.list_documents()
    return {
        "status": "healthy",
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "nvidia_configured": settings.is_nvidia_configured(),
        "mongodb_connected": db_manager.is_connected,
        "mongodb_error": db_manager.connection_error if not db_manager.is_connected else None,
        "active_documents_count": len(docs),
    }
