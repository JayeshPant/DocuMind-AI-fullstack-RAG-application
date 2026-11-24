import io
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_invalid_pdf_extension():
    file = io.BytesIO(b"Hello world")
    response = client.post(
        "/api/documents/upload",
        files={"file": ("test.txt", file, "text/plain")},
    )
    assert response.status_code == 400
    assert "Only PDF files are supported" in response.json()["detail"]


def test_corrupt_pdf_magic_bytes():
    file = io.BytesIO(b"Not a valid pdf binary content")
    response = client.post(
        "/api/documents/upload",
        files={"file": ("fake.pdf", file, "application/pdf")},
    )
    assert response.status_code == 400
    assert "Missing %PDF header" in response.json()["detail"]


def test_valid_pdf_upload_and_lifecycle():
    # Construct minimal valid PDF
    valid_pdf = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj
4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj
5 0 obj << /Length 120 >> stream
BT
/F1 12 Tf
50 720 Td
(Q1. What is regression analysis?) Tj
0 -20 Td
(Regression analysis is a set of statistical methods.) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000227 00000 n 
0000000306 00000 n 
trailer << /Size 6 /Root 1 0 R >>
startxref
480
%%EOF"""

    file = io.BytesIO(valid_pdf)
    upload_res = client.post(
        "/api/documents/upload",
        files={"file": ("sample_test.pdf", file, "application/pdf")},
    )
    assert upload_res.status_code == 201
    doc_data = upload_res.json()
    doc_id = doc_data["document_id"]
    assert doc_data["original_filename"] == "sample_test.pdf"
    assert doc_data["page_count"] >= 1

    # Get document
    get_res = client.get(f"/api/documents/{doc_id}")
    assert get_res.status_code == 200
    assert get_res.json()["document_id"] == doc_id

    # List documents
    list_res = client.get("/api/documents")
    assert list_res.status_code == 200
    docs = list_res.json()["documents"]
    assert any(d["document_id"] == doc_id for d in docs)

    # Delete document
    del_res = client.delete(f"/api/documents/{doc_id}")
    assert del_res.status_code == 200

    # Verify deleted
    get_after = client.get(f"/api/documents/{doc_id}")
    assert get_after.status_code == 404
