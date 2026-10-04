from __future__ import annotations

import os
from typing import Any

import boto3
from botocore.config import Config

SERVICE = "bg-removal"

R2_ENDPOINT = os.environ.get("R2_ENDPOINT", "")
R2_ACCESS_KEY_ID = os.environ.get("R2_ACCESS_KEY_ID", "")
R2_SECRET_ACCESS_KEY = os.environ.get("R2_SECRET_ACCESS_KEY", "")
R2_BUCKET_TMP = os.environ.get("R2_BUCKET_TMP", "agenteresolve-tmp")

_client: Any | None = None


def get_client() -> Any:
    global _client
    if _client is None:
        _client = boto3.client(
            "s3",
            endpoint_url=R2_ENDPOINT,
            aws_access_key_id=R2_ACCESS_KEY_ID,
            aws_secret_access_key=R2_SECRET_ACCESS_KEY,
            region_name="auto",
            config=Config(signature_version="s3v4", retries={"max_attempts": 3}),
        )
    return _client


def result_key(task_id: str) -> str:
    return f"tmp/results/{SERVICE}/{task_id}/result.png"


def upload_result(task_id: str, data: bytes) -> str:
    key = result_key(task_id)
    get_client().put_object(
        Bucket=R2_BUCKET_TMP,
        Key=key,
        Body=data,
        ContentType="image/png",
    )
    return key
