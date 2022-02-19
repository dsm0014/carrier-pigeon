from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/pigeon/")
    assert response.status_code == 200
    assert "<title>NATS+Python Example Project</title>" in str(response.content)
