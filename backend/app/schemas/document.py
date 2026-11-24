from typing import Optional, List
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    document_id: str
    original_filename: str
    file_size: int
    upload_timestamp: str
    processing_status: str = "indexed"  # pending, processing, indexed, failed
    page_count: int = 0
    chunk_count: int = 0
    indexing_status: str = "complete"
    error: Optional[str] = None


class DocumentListResponse(BaseModel):
    documents: List[DocumentMetadata]
    total: int
