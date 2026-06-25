import io

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)

def test_remove_background():
    img = Image.new("RGB", (50, 50), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    files = {"file": ("test.png", buf.getvalue(), "image/png")}
    response = client.post("/remove-bg/", files=files)
    assert response.status_code == 200
    assert "image" in response.json()
    assert response.json()["image"].startswith("data:image/png;base64,")

def test_remove_background_png():
    img = Image.new("RGBA", (50, 50), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    files = {"file": ("test.png", buf.getvalue(), "image/png")}
    response = client.post("/remove-bg/?format=png", files=files)
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert len(response.content) > 100

def test_remove_background_error():
    response = client.post("/remove-bg/", files={})
    assert response.status_code == 422
    assert "detail" in response.json()