from __future__ import annotations

import io
from unittest.mock import MagicMock

import pytest
from PIL import Image


def _png() -> bytes:
    img = Image.new("RGB", (30, 30), color="red")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_task_uploads_result_to_r2_and_skips_redis(mocker):
    from src.tasks import remove_bg as task_module

    mocker.patch.object(
        task_module,
        "remove",
        return_value=Image.new("RGBA", (30, 30), color=(0, 0, 0, 0)),
    )
    upload = mocker.patch.object(task_module.storage, "upload_result")

    result = task_module.remove_bg.apply(args=[_png()]).get()

    assert upload.call_count == 1
    task_id, data = upload.call_args.args
    assert task_id == result["task_id"]
    assert data.startswith(b"\x89PNG")


def test_task_does_not_write_result_blob_to_redis(mocker):
    from src.tasks import remove_bg as task_module

    mocker.patch.object(
        task_module,
        "remove",
        return_value=Image.new("RGBA", (30, 30), color=(0, 0, 0, 0)),
    )
    mocker.patch.object(task_module.storage, "upload_result", MagicMock())
    redis_cls = mocker.patch("src.tasks.remove_bg.Redis", create=True)

    task_module.remove_bg.apply(args=[_png()]).get()

    assert redis_cls.call_count == 0


def test_task_retries_on_failure(mocker):
    from src.tasks import remove_bg as task_module

    mocker.patch.object(task_module, "remove", side_effect=ValueError("removal failed"))

    with pytest.raises(Exception, match="removal failed"):
        task_module.remove_bg.apply(args=[_png()]).get()
