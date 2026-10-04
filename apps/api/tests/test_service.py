import io

from PIL import Image

import src.services.background_removal as service


def _png_bytes() -> bytes:
    img = Image.new("RGB", (20, 20), color="red")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_remove_background_returns_png(monkeypatch) -> None:
    def _fake_remove(image: Image.Image) -> Image.Image:
        return image.convert("RGBA")

    monkeypatch.setattr(service, "remove", _fake_remove)
    result = service.remove_background(_png_bytes())
    assert result.startswith(b"\x89PNG")
