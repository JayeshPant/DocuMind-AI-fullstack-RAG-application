from backend.app.routes.health import router as health_router
from backend.app.routes.documents import router as documents_router
from backend.app.routes.qa import router as qa_router
from backend.app.routes.history import router as history_router

__all__ = [
    "health_router",
    "documents_router",
    "qa_router",
    "history_router",
]
