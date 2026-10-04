import io
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from src.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _isolate_external_services(mocker):
    task = MagicMock()
    task.id = "test-task-id"
    mocker.patch("src.api.routes.celery_app.send_task", return_value=task)
    mocker.patch("src.api.routes.r2.upload_input", return_value="tmp/uploads/test")


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


def test_task_status_not_found(mocker):
    mocker.patch(
        "src.api.routes.AsyncResult",
        return_value=MagicMock(state="PENDING", ready=lambda: False),
    )
    response = client.get("/api/tasks/invalid-id/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("PENDING", "FAILURE")


def test_remove_background_invalid_file():
    response = client.post("/api/remove-bg/")
    assert response.status_code == 422
