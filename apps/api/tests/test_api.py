import io
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from src.core.config import settings
from src.main import app

client = TestClient(app)


def _png_bytes() -> bytes:
    img = Image.new("RGB", (50, 50), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class _FakeAsyncResult:
    def __init__(
        self,
        state: str,
        *,
        ready: bool = False,
        successful: bool = False,
        result: object = None,
    ) -> None:
        self.state = state
        self._ready = ready
        self._successful = successful
        self.result = result

    def ready(self) -> bool:
        return self._ready

    def successful(self) -> bool:
        return self._successful


@pytest.fixture(autouse=True)
def _isolate_external_services(mocker):
    task = MagicMock()
    task.id = "test-task-id"
    mocker.patch("src.api.routes.celery_app.send_task", return_value=task)
    mocker.patch("src.api.routes.r2.upload_input", return_value="tmp/uploads/test")


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_remove_background_returns_task_id() -> None:
    files = {"file": ("test.png", _png_bytes(), "image/png")}
    response = client.post("/api/remove-bg/", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "test-task-id"


def test_remove_background_file_too_large(monkeypatch) -> None:
    monkeypatch.setattr(settings, "MAX_FILE_SIZE", 10)
    files = {"file": ("test.png", _png_bytes(), "image/png")}
    response = client.post("/api/remove-bg/", files=files)
    assert response.status_code == 413


def test_remove_background_invalid_file() -> None:
    response = client.post("/api/remove-bg/")
    assert response.status_code == 422


def test_task_status_not_found(monkeypatch) -> None:
    monkeypatch.setattr(
        "src.api.routes.AsyncResult",
        lambda task_id, app=None: _FakeAsyncResult("PENDING"),
    )
    response = client.get("/api/tasks/invalid-id/status")
    assert response.status_code == 200
    assert response.json()["status"] in ("PENDING", "FAILURE")


def test_task_status_pending(monkeypatch) -> None:
    monkeypatch.setattr(
        "src.api.routes.AsyncResult",
        lambda task_id, app=None: _FakeAsyncResult("PENDING"),
    )
    response = client.get("/api/tasks/abc/status")
    assert response.status_code == 200
    assert response.json() == {
        "task_id": "abc",
        "status": "PENDING",
        "result": None,
    }


def test_task_status_success(monkeypatch) -> None:
    monkeypatch.setattr(
        "src.api.routes.AsyncResult",
        lambda task_id, app=None: _FakeAsyncResult("SUCCESS", ready=True, successful=True),
    )
    response = client.get("/api/tasks/abc/status")
    assert response.status_code == 200
    assert response.json()["result"] == "completed"


def test_task_status_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "src.api.routes.AsyncResult",
        lambda task_id, app=None: _FakeAsyncResult(
            "FAILURE", ready=True, successful=False, result="boom"
        ),
    )
    response = client.get("/api/tasks/abc/status")
    assert response.status_code == 500
    assert response.json()["detail"] == "boom"


def test_task_result_not_found(monkeypatch) -> None:
    def _raise(task_id: str) -> str:
        raise KeyError("missing")

    monkeypatch.setattr("src.api.routes.r2.presigned_result_url", _raise)
    response = client.get("/api/tasks/abc/result")
    assert response.status_code == 404


def test_task_result_redirects_to_presigned_url(monkeypatch) -> None:
    monkeypatch.setattr(
        "src.api.routes.r2.presigned_result_url",
        lambda task_id: f"https://signed.example/{task_id}",
    )
    response = client.get("/api/tasks/abc/result", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://signed.example/abc"
