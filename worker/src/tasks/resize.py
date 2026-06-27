from PIL import Image

MAX_DIMENSION = 1200


def resize_image_safe(image: Image.Image, max_dim: int) -> Image.Image:
    if image.width > max_dim or image.height > max_dim:
        image.thumbnail((max_dim, max_dim), Image.LANCZOS)
    return image
