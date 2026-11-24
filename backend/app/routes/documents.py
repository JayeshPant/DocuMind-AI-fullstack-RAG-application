import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from backend.app.schemas.document import DocumentMetadata, DocumentListResponse
from backend.app.services.document_service import document_service

logger = logging.getLogger("documind.routes.documents")
router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentMetadata, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename must be provided.")

    try:
        content = await file.read()
        doc_record = document_service.process_and_index_file(content, file.filename)
        return doc_record
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process and index document: {str(e)}")


@router.get("", response_model=DocumentListResponse)
def list_documents():
    docs = document_service.list_documents()
    return {"documents": docs, "total": len(docs)}


@router.get("/{document_id}", response_model=DocumentMetadata)
def get_document(document_id: str):
    doc = document_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document with ID '{document_id}' not found.")
    return doc


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
def delete_document(document_id: str):
    deleted = document_service.delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Document with ID '{document_id}' not found or could not be deleted.")
    return {"status": "success", "message": f"Document '{document_id}' and associated vectors deleted successfully."}
