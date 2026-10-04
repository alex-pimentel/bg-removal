from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.core.config import settings

MODULE = "boto3.client"


@pytest.fixture
def s3_mock(mocker) -> MagicMock:
    mock = MagicMock()
    mocker.patch(MODULE, return_value=mock)
    return mock


@pytest.fixture(autouse=True)
def _r2_settings(monkeypatch):
    monkeypatch.setattr(settings, "R2_ENDPOINT", "https://acct.r2.cloudflarestorage.com")
    monkeypatch.setattr(settings, "R2_ACCESS_KEY_ID", "key")
    monkeypatch.setattr(settings, "R2_SECRET_ACCESS_KEY", "secret")
    monkeypatch.setattr(settings, "R2_BUCKET_TMP", "agenteresolve-tmp")


def _client(s3_mock: MagicMock, monkeypatch):
    from src.core import r2

    monkeypatch.setattr(r2, "_client", None)
    return r2


def test_upload_input_key_matches_contract(s3_mock, monkeypatch):
    r2 = _client(s3_mock, monkeypatch)
    r2.upload_input("abc123", "photo.png", b"data", content_type="image/png")

    s3_mock.put_object.assert_called_once_with(
        Bucket="agenteresolve-tmp",
        Key="tmp/uploads/bg-removal/abc123/photo.png",
        Body=b"data",
        ContentType="image/png",
    )


def test_upload_result_key_matches_contract(s3_mock, monkeypatch):
    r2 = _client(s3_mock, monkeypatch)
    r2.upload_result("abc123", b"png-bytes")

    s3_mock.put_object.assert_called_once_with(
        Bucket="agenteresolve-tmp",
        Key="tmp/results/bg-removal/abc123/result.png",
        Body=b"png-bytes",
        ContentType="image/png",
    )


def test_presigned_result_url_uses_expiry(s3_mock, monkeypatch):
    r2 = _client(s3_mock, monkeypatch)
    s3_mock.generate_presigned_url.return_value = "https://signed.example/result"

    url = r2.presigned_result_url("abc123", expires=300)

    s3_mock.generate_presigned_url.assert_called_once_with(
        "get_object",
        Params={
            "Bucket": "agenteresolve-tmp",
            "Key": "tmp/results/bg-removal/abc123/result.png",
        },
        ExpiresIn=300,
    )
    assert url == "https://signed.example/result"


def test_sanitizes_filename_path_traversal(s3_mock, monkeypatch):
    r2 = _client(s3_mock, monkeypatch)
    r2.upload_input("abc123", "../../etc/passwd", b"x")

    key = s3_mock.put_object.call_args.kwargs["Key"]
    assert key == "tmp/uploads/bg-removal/abc123/passwd"
    assert ".." not in key


def test_client_uses_endpoint_and_credentials(mocker, monkeypatch):
    from src.core import r2

    monkeypatch.setattr(r2, "_client", None)
    boto_client = mocker.patch(MODULE, return_value=MagicMock())

    r2.get_client()

    kwargs = boto_client.call_args.kwargs
    assert kwargs["endpoint_url"] == "https://acct.r2.cloudflarestorage.com"
    assert kwargs["aws_access_key_id"] == "key"
    assert kwargs["aws_secret_access_key"] == "secret"
