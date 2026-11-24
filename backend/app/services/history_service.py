import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from backend.app.database import db_manager


class HistoryService:
    def record_qa(
        self,
        document_id: str,
        document_filename: str,
        question_mode: str,
        user_question: str,
        generated_answer: str,
        sources: list,
        requested_question_number: Optional[int] = None,
        detected_question_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        interaction_id = f"int_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()

        record = {
            "interaction_id": interaction_id,
            "document_id": document_id,
            "document_filename": document_filename,
            "question_mode": question_mode,
            "requested_question_number": requested_question_number,
            "detected_question_text": detected_question_text,
            "question": user_question,
            "answer": generated_answer,
            "sources": sources,
            "timestamp": timestamp,
        }

        db_manager.save_history(record)
        return record

    def list_history(self, document_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        return db_manager.list_history(document_id=document_id, limit=limit)

    def get_interaction(self, interaction_id: str) -> Optional[Dict[str, Any]]:
        return db_manager.get_interaction(interaction_id)

    def clear_history(self, document_id: Optional[str] = None) -> int:
        return db_manager.clear_history(document_id=document_id)


history_service = HistoryService()
