import io

from fastapi.testclient import TestClient
from PIL import Image

from src.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_remove_background_returns_task_id():
    img = Image.new("RGB", (50, 50), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    files = {"file": ("test.png", buf.getvalue(), "image/png")}
    response = client.post("/api/remove-bg/", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert isinstance(data["task_id"], str)


def test_task_status_not_found():
    response = client.get("/api/tasks/invalid-id/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("PENDING", "FAILURE")


def test_remove_background_invalid_file():
    response = client.post("/api/remove-bg/")
    assert response.status_code == 422
