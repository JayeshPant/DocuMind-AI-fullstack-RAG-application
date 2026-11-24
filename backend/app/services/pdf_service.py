import os
import uuid
import logging
from pathlib import Path
from typing import List, Tuple
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.app.config import settings

logger = logging.getLogger("documind.pdf")


class PDFService:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )

    def validate_pdf(self, file_bytes: bytes, filename: str) -> None:
        if not filename.lower().endswith(".pdf"):
            raise ValueError(f"Invalid file extension for '{filename}'. Only PDF files are supported.")
        
        # Check PDF magic bytes (%PDF)
        if len(file_bytes) < 4 or file_bytes[:4] != b"%PDF":
            raise ValueError("Invalid PDF file: Missing %PDF header.")

        # Max file size: 25MB
        max_size = 25 * 1024 * 1024
        if len(file_bytes) > max_size:
            raise ValueError(f"File size exceeds maximum limit of 25MB ({len(file_bytes)} bytes).")

    def save_uploaded_file(self, file_bytes: bytes, original_filename: str) -> Tuple[str, Path]:
        doc_id = f"doc_{uuid.uuid4().hex[:12]}"
        safe_name = f"{doc_id}_{Path(original_filename).name}"
        file_path = self.upload_dir / safe_name
        
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        return doc_id, file_path

    def load_and_split(self, file_path: Path, doc_id: str, original_filename: str) -> Tuple[List[Document], List[Document]]:
        """
        Loads PDF using PyPDFLoader and returns (pages, chunks).
        """
        logger.info(f"Loading PDF from: {file_path}")
        loader = PyPDFLoader(str(file_path))
        pages = loader.load()
        
        if not pages:
            raise ValueError("The uploaded PDF is empty or contains no readable pages.")

        # Enrich page metadata with doc_id and filename
        for i, page in enumerate(pages):
            page.metadata["document_id"] = doc_id
            page.metadata["source_filename"] = original_filename
            # Normalize page index (0-indexed or 1-indexed)
            if "page" not in page.metadata:
                page.metadata["page"] = i + 1

        chunks = self.text_splitter.split_documents(pages)
        # Ensure all chunks retain document_id and page metadata
        for chunk in chunks:
            chunk.metadata["document_id"] = doc_id
            chunk.metadata["source_filename"] = original_filename

        logger.info(f"Loaded {len(pages)} pages and created {len(chunks)} text chunks for doc {doc_id}.")
        return pages, chunks


pdf_service = PDFService()
