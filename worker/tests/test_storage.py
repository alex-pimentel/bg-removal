from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.tasks import storage

MODULE = "boto3.client"


@pytest.fixture(autouse=True)
def _settings(monkeypatch):
    monkeypatch.setattr(storage, "R2_ENDPOINT", "https://acct.r2.cloudflarestorage.com")
    monkeypatch.setattr(storage, "R2_ACCESS_KEY_ID", "key")
    monkeypatch.setattr(storage, "R2_SECRET_ACCESS_KEY", "secret")
    monkeypatch.setattr(storage, "R2_BUCKET_TMP", "agenteresolve-tmp")


@pytest.fixture
def s3_mock(mocker) -> MagicMock:
    mock = MagicMock()
    mocker.patch(MODULE, return_value=mock)
    return mock


def test_upload_result_contract(s3_mock, monkeypatch):
    monkeypatch.setattr(storage, "_client", None)

    storage.upload_result("task-9", b"png")

    s3_mock.put_object.assert_called_once_with(
        Bucket="agenteresolve-tmp",
        Key="tmp/results/bg-removal/task-9/result.png",
        Body=b"png",
        ContentType="image/png",
    )


def test_no_redis_result_write(s3_mock, monkeypatch):
    monkeypatch.setattr(storage, "_client", None)
    storage.upload_result("task-9", b"png")

    assert s3_mock.set.call_count == 0
