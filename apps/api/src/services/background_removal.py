import io

from PIL import Image
from rembg import remove


def remove_background(image_bytes: bytes) -> bytes:
    input_image = Image.open(io.BytesIO(image_bytes))
    output_image = remove(input_image)
    output_buffer = io.BytesIO()
    output_image.save(output_buffer, format="PNG")
    return output_buffer.getvalue()
