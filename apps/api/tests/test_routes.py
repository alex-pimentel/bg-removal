from __future__ import annotations

import io
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from src.core.config import settings
from src.main import app


@pytest.fixture
def client(mocker) -> TestClient:
    # Celery producer: avoid touching Redis during tests.
    task = MagicMock()
    task.id = "task-123"
    mocker.patch("src.api.routes.celery_app.send_task", return_value=task)
    # R2 upload helper.
    mocker.patch("src.api.routes.r2.upload_input", return_value="tmp/uploads/...")
    return TestClient(app)


def _png() -> bytes:
    img = Image.new("RGB", (20, 20), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_upload_stores_in_r2_and_returns_task_id(client, mocker):
    upload = mocker.patch("src.api.routes.r2.upload_input")

    response = client.post(
        "/api/remove-bg/",
        files={"file": ("photo.png", _png(), "image/png")},
    )

    assert response.status_code == 200
    assert response.json()["task_id"] == "task-123"

    args = upload.call_args.args
    assert args[0] == "task-123"
    assert args[1] == "photo.png"
    assert args[2] == _png()


def test_upload_rejects_oversized(client, monkeypatch):
    monkeypatch.setattr(settings, "MAX_FILE_SIZE", 10)
    response = client.post(
        "/api/remove-bg/",
        files={"file": ("photo.png", _png(), "image/png")},
    )
    assert response.status_code == 413


def test_result_redirects_to_presigned_url(client, mocker):
    mocker.patch(
        "src.api.routes.r2.presigned_result_url",
        return_value="https://signed.example/result.png",
    )

    response = client.get("/api/tasks/task-123/result", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "https://signed.example/result.png"


def test_bearer_token_is_verified_when_configured(client, mocker, monkeypatch):
    monkeypatch.setattr(settings, "CLERK_JWKS_URL", "https://clerk.example/jwks")
    monkeypatch.setattr(settings, "CLERK_ISSUER", "https://clerk.example")
    verify = mocker.patch(
        "src.api.deps.clerk.optional_user",
        return_value={"sub": "user_1"},
    )

    response = client.post(
        "/api/remove-bg/",
        files={"file": ("photo.png", _png(), "image/png")},
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 200
    assert verify.called


def test_anonymous_allowed(client):
    response = client.post(
        "/api/remove-bg/",
        files={"file": ("photo.png", _png(), "image/png")},
    )
    assert response.status_code == 200


def test_invalid_bearer_rejected(client, mocker, monkeypatch):
    monkeypatch.setattr(settings, "CLERK_JWKS_URL", "https://clerk.example/jwks")
    monkeypatch.setattr(settings, "CLERK_ISSUER", "https://clerk.example")
    mocker.patch("src.api.deps.clerk.optional_user", side_effect=ValueError("bad"))

    response = client.post(
        "/api/remove-bg/",
        files={"file": ("photo.png", _png(), "image/png")},
        headers={"Authorization": "Bearer nope"},
    )

    assert response.status_code == 401
