from unittest.mock import MagicMock
from langchain_core.documents import Document
from backend.app.services.rag_service import rag_service
from backend.app.services.document_service import document_service
from backend.app.database import db_manager


def test_document_isolation_in_qdrant():
    doc_a_id = "doc_test_alpha"
    doc_b_id = "doc_test_beta"

    chunks_a = [
        Document(page_content="Alpha topic: Quantum Computing uses qubits.", metadata={"page": 1, "document_id": doc_a_id})
    ]
    chunks_b = [
        Document(page_content="Beta topic: Botanical photosyntheis occurs in leaves.", metadata={"page": 1, "document_id": doc_b_id})
    ]

    rag_service.index_document(doc_a_id, chunks_a)
    rag_service.index_document(doc_b_id, chunks_b)

    # Querying doc A
    vs_a = rag_service.get_vectorstore(doc_a_id)
    retrieved_a = vs_a.as_retriever(search_kwargs={"k": 2}).invoke("What is photosynthesis?")
    # Doc A must only return doc A chunks, never doc B
    for doc in retrieved_a:
        assert doc.metadata["document_id"] == doc_a_id
        assert "Beta topic" not in doc.page_content

    # Querying doc B
    vs_b = rag_service.get_vectorstore(doc_b_id)
    retrieved_b = vs_b.as_retriever(search_kwargs={"k": 2}).invoke("What is quantum computing?")
    for doc in retrieved_b:
        assert doc.metadata["document_id"] == doc_b_id
        assert "Alpha topic" not in doc.page_content

    # Clean up
    rag_service.delete_document_vectors(doc_a_id)
    rag_service.delete_document_vectors(doc_b_id)


def test_database_persistence():
    doc_data = {
        "document_id": "doc_test_db",
        "original_filename": "test.pdf",
        "file_size": 1234,
    }
    db_manager.save_document(doc_data)
    fetched = db_manager.get_document("doc_test_db")
    assert fetched is not None
    assert fetched["original_filename"] == "test.pdf"

    history_record = {
        "interaction_id": "int_test_123",
        "document_id": "doc_test_db",
        "question": "What is x?",
        "answer": "x is a variable.",
    }
    db_manager.save_history(history_record)
    hist_fetched = db_manager.get_interaction("int_test_123")
    assert hist_fetched is not None
    assert hist_fetched["answer"] == "x is a variable."

    # Cleanup
    db_manager.delete_document("doc_test_db")
    assert db_manager.get_document("doc_test_db") is None
