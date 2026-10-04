import io

import pytest
from PIL import Image

import src.tasks.remove_bg as task_module


class _FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, bytes] = {}

    def set(self, key: str, value: bytes, ex: int | None = None) -> None:
        self.store[key] = value


def _png_bytes() -> bytes:
    img = Image.new("RGB", (50, 50), color="green")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_remove_bg_task_stores_result(monkeypatch) -> None:
    fake = _FakeRedis()
    monkeypatch.setattr(task_module, "remove", lambda image: image.convert("RGBA"))
    monkeypatch.setattr("redis.Redis.from_url", staticmethod(lambda url: fake))

    result = task_module.remove_bg.apply(args=[_png_bytes()]).get()

    assert result["status"] == "completed"
    assert any(key.startswith("result:") for key in fake.store)


def test_remove_bg_task_retries_on_failure(monkeypatch) -> None:
    def _boom(image: Image.Image) -> Image.Image:
        raise ValueError("removal failed")

    monkeypatch.setattr(task_module, "remove", _boom)

    with pytest.raises(Exception, match="removal failed"):
        task_module.remove_bg.apply(args=[_png_bytes()]).get()
