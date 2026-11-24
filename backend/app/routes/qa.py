import logging
from fastapi import APIRouter, HTTPException, status
from backend.app.schemas.qa import AskRequest, AskByNumberRequest, QAResponse, SourceExcerpt
from backend.app.services.document_service import document_service
from backend.app.services.question_number_service import question_number_service
from backend.app.services.rag_service import rag_service
from backend.app.services.history_service import history_service

logger = logging.getLogger("documind.routes.qa")
router = APIRouter(prefix="/api", tags=["Question Answering"])


@router.post("/ask", response_model=QAResponse, status_code=status.HTTP_200_OK)
def ask_question(req: AskRequest):
    # 1. Verify document exists
    doc = document_service.get_document(req.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{req.document_id}' not found.")

    doc_filename = doc.get("original_filename", "document.pdf")

    # 2. Execute RAG
    try:
        answer, retrieved_docs = rag_service.query(req.document_id, req.question)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error querying RAG for question '{req.question}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate answer from language model: {str(e)}")

    # 3. Format sources
    sources = []
    for d in retrieved_docs:
        page_val = d.metadata.get("page", 1)
        if isinstance(page_val, int) and page_val == 0:
            page_val = 1
        sources.append(
            SourceExcerpt(
                page=int(page_val),
                content=d.page_content.strip()[:400],
            )
        )

    # 4. Save to history
    record = history_service.record_qa(
        document_id=req.document_id,
        document_filename=doc_filename,
        question_mode="free_text",
        user_question=req.question,
        generated_answer=answer,
        sources=[s.model_dump() for s in sources],
    )

    return record


@router.post("/ask-by-number", response_model=QAResponse, status_code=status.HTTP_200_OK)
def ask_by_question_number(req: AskByNumberRequest):
    # 1. Verify document exists
    doc = document_service.get_document(req.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{req.document_id}' not found.")

    doc_filename = doc.get("original_filename", "document.pdf")

    # 2. Retrieve document pages for question extraction
    pages = document_service.get_parsed_pages(req.document_id)
    if not pages:
        raise HTTPException(status_code=400, detail=f"Document '{req.document_id}' has no accessible text pages.")

    # 3. Extract requested question number
    found, detected_q, page_num, not_found_msg = question_number_service.find_question_by_number(
        pages, req.question_number
    )

    if not found or not detected_q:
        raise HTTPException(
            status_code=404,
            detail=not_found_msg or f"Question number {req.question_number} was not found in the selected document.",
        )

    # 4. Execute RAG query using detected question text
    try:
        query_prompt = f"Question {req.question_number}: {detected_q}"
        answer, retrieved_docs = rag_service.query(req.document_id, query_prompt)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error querying RAG for question #{req.question_number}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate answer from language model: {str(e)}")

    # 5. Format sources
    sources = []
    for d in retrieved_docs:
        page_val = d.metadata.get("page", 1)
        if isinstance(page_val, int) and page_val == 0:
            page_val = 1
        sources.append(
            SourceExcerpt(
                page=int(page_val),
                content=d.page_content.strip()[:400],
            )
        )

    # 6. Save to history
    record = history_service.record_qa(
        document_id=req.document_id,
        document_filename=doc_filename,
        question_mode="by_number",
        requested_question_number=req.question_number,
        detected_question_text=detected_q,
        user_question=f"Question {req.question_number}: {detected_q}",
        generated_answer=answer,
        sources=[s.model_dump() for s in sources],
    )

    return record
