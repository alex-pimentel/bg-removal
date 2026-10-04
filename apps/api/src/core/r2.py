from __future__ import annotations

from typing import Any

import boto3
from botocore.config import Config

from src.core.config import settings

SERVICE = "bg-removal"
_client: Any | None = None


def _key(prefix: str, task_id: str, filename: str) -> str:
    safe_name = filename.replace("\\", "/").rsplit("/", 1)[-1] or "file"
    return f"tmp/{prefix}/{SERVICE}/{task_id}/{safe_name}"


def get_client() -> Any:
    global _client
    if _client is None:
        _client = boto3.client(
            "s3",
            endpoint_url=settings.R2_ENDPOINT,
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            region_name="auto",
            config=Config(signature_version="s3v4", retries={"max_attempts": 3}),
        )
    return _client


def upload_input(
    task_id: str,
    filename: str,
    data: bytes,
    content_type: str = "application/octet-stream",
) -> str:
    key = _key("uploads", task_id, filename)
    get_client().put_object(
        Bucket=settings.R2_BUCKET_TMP,
        Key=key,
        Body=data,
        ContentType=content_type,
    )
    return key


def upload_result(task_id: str, data: bytes) -> str:
    key = _key("results", task_id, "result.png")
    get_client().put_object(
        Bucket=settings.R2_BUCKET_TMP,
        Key=key,
        Body=data,
        ContentType="image/png",
    )
    return key


def result_key(task_id: str) -> str:
    return _key("results", task_id, "result.png")


def presigned_result_url(task_id: str, expires: int | None = None) -> str:
    return str(
        get_client().generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.R2_BUCKET_TMP, "Key": result_key(task_id)},
            ExpiresIn=expires or settings.RESULT_URL_TTL,
        )
    )
