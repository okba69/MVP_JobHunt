from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_get_jobs_empty():
    response = client.get("/api/jobs")
    assert response.status_code == 200
    assert response.json() == []
