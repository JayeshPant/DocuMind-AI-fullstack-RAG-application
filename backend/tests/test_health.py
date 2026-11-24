from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "nvidia_configured" in data
    assert "mongodb_connected" in data
    assert "active_documents_count" in data


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "DocuMind AI" in response.json()["message"]
