from PIL import Image

from src.tasks.resize import resize_image_safe

MAX_DIM = 1200


def test_resize_large_portrait():
    img = Image.new("RGB", (2000, 3000))
    result = resize_image_safe(img, MAX_DIM)
    assert result.width <= MAX_DIM
    assert result.height <= MAX_DIM
    assert result.width == 800
    assert result.height == 1200


def test_resize_large_landscape():
    img = Image.new("RGB", (3000, 2000))
    result = resize_image_safe(img, MAX_DIM)
    assert result.width <= MAX_DIM
    assert result.height <= MAX_DIM
    assert result.width == 1200
    assert result.height == 800


def test_resize_square():
    img = Image.new("RGB", (2500, 2500))
    result = resize_image_safe(img, MAX_DIM)
    assert result.width == MAX_DIM
    assert result.height == MAX_DIM


def test_small_image_unchanged():
    img = Image.new("RGB", (800, 600))
    result = resize_image_safe(img, MAX_DIM)
    assert result.width == 800
    assert result.height == 600


def test_aspect_ratio_preserved():
    img = Image.new("RGB", (2000, 1000))
    result = resize_image_safe(img, MAX_DIM)
    aspect_before = img.width / img.height
    aspect_after = result.width / result.height
    assert abs(aspect_before - aspect_after) < 0.01


def test_upscale_not_allowed():
    img = Image.new("RGB", (100, 100))
    result = resize_image_safe(img, MAX_DIM)
    assert result.width == 100
    assert result.height == 100
