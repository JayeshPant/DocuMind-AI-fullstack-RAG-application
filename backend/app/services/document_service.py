import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.app.config import settings
from backend.app.database import db_manager
from backend.app.services.pdf_service import pdf_service
from backend.app.services.rag_service import rag_service

logger = logging.getLogger("documind.documents")


class DocumentService:
    def __init__(self):
        # Cache of parsed document pages in memory for quick question-number extraction
        self._parsed_pages_cache: Dict[str, list] = {}

    def get_parsed_pages(self, document_id: str) -> Optional[list]:
        if document_id in self._parsed_pages_cache:
            return self._parsed_pages_cache[document_id]

        doc = db_manager.get_document(document_id)
        if not doc or "file_path" not in doc:
            return None

        file_path = Path(doc["file_path"])
        if not file_path.exists():
            return None

        try:
            pages, _ = pdf_service.load_and_split(file_path, document_id, doc.get("original_filename", "document.pdf"))
            self._parsed_pages_cache[document_id] = pages
            return pages
        except Exception as e:
            logger.error(f"Failed to load parsed pages for doc {document_id}: {e}")
            return None

    def process_and_index_file(self, file_bytes: bytes, original_filename: str) -> Dict[str, Any]:
        # 1. Validate
        pdf_service.validate_pdf(file_bytes, original_filename)

        # 2. Save
        doc_id, file_path = pdf_service.save_uploaded_file(file_bytes, original_filename)

        # 3. Load & Split
        pages, chunks = pdf_service.load_and_split(file_path, doc_id, original_filename)
        self._parsed_pages_cache[doc_id] = pages

        # 4. Vector index
        rag_service.index_document(doc_id, chunks)

        # 5. Metadata record
        doc_record = {
            "document_id": doc_id,
            "original_filename": original_filename,
            "file_size": len(file_bytes),
            "file_path": str(file_path),
            "page_count": len(pages),
            "chunk_count": len(chunks),
            "processing_status": "indexed",
            "indexing_status": "complete",
        }
        db_manager.save_document(doc_record)
        return doc_record

    def list_documents(self) -> List[Dict[str, Any]]:
        return db_manager.list_documents()

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        return db_manager.get_document(doc_id)

    def delete_document(self, doc_id: str) -> bool:
        doc = db_manager.get_document(doc_id)
        # 1. Delete vector collection
        rag_service.delete_document_vectors(doc_id)

        # 2. Remove cache
        if doc_id in self._parsed_pages_cache:
            del self._parsed_pages_cache[doc_id]

        # 3. Delete physical file if exists
        if doc and "file_path" in doc:
            try:
                p = Path(doc["file_path"])
                if p.exists():
                    p.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete local file for doc {doc_id}: {e}")

        # 4. Remove from DB
        return db_manager.delete_document(doc_id)

    def preload_stats_pdf_if_available(self):
        """
        Preloads the professor's STATS.pdf on startup if present in document_loader/
        and not already indexed.
        """
        stats_path = settings.DOCUMENT_LOADER_DIR / "STATS.pdf"
        if not stats_path.exists():
            return

        doc_id = "doc_stats_default"
        existing = db_manager.get_document(doc_id)
        if existing and rag_service.get_vectorstore(doc_id) is not None:
            return  # Already indexed and active

        try:
            logger.info(f"Preloading default document from {stats_path}...")
            with open(stats_path, "rb") as f:
                file_bytes = f.read()

            pages, chunks = pdf_service.load_and_split(stats_path, doc_id, "STATS.pdf")
            self._parsed_pages_cache[doc_id] = pages
            rag_service.index_document(doc_id, chunks)

            doc_record = {
                "document_id": doc_id,
                "original_filename": "STATS.pdf",
                "file_size": len(file_bytes),
                "file_path": str(stats_path),
                "page_count": len(pages),
                "chunk_count": len(chunks),
                "processing_status": "indexed",
                "indexing_status": "complete",
            }
            db_manager.save_document(doc_record)
            logger.info("Successfully preloaded STATS.pdf as 'doc_stats_default'.")
        except Exception as e:
            logger.warning(f"Could not preload STATS.pdf: {e}")


document_service = DocumentService()
