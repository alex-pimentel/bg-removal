import io

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


class _FakeTask:
    id = "test-task-id"


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


class _FakeRedis:
    def __init__(self, value: bytes | None) -> None:
        self._value = value

    async def get(self, key: str) -> bytes | None:
        return self._value


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_remove_background_returns_task_id(monkeypatch) -> None:
    monkeypatch.setattr(
        "src.api.routes.celery_app.send_task",
        lambda *args, **kwargs: _FakeTask(),
    )
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
    async def _fake_get_redis() -> _FakeRedis:
        return _FakeRedis(None)

    monkeypatch.setattr("src.api.routes.get_redis", _fake_get_redis)
    response = client.get("/api/tasks/abc/result")
    assert response.status_code == 404


def test_task_result_returns_png(monkeypatch) -> None:
    payload = b"\x89PNG\r\n\x1a\nfake"

    async def _fake_get_redis() -> _FakeRedis:
        return _FakeRedis(payload)

    monkeypatch.setattr("src.api.routes.get_redis", _fake_get_redis)
    response = client.get("/api/tasks/abc/result")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content == payload
