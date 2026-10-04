import io
from typing import Any

from PIL import Image
from rembg import remove

from src.tasks import storage
from src.tasks.resize import MAX_DIMENSION, resize_image_safe
from src.worker import celery_app


@celery_app.task(name="remove_bg", bind=True, max_retries=3, default_retry_delay=5)
def remove_bg(self: Any, image_bytes: bytes) -> dict[str, Any]:
    try:
        input_image: Image.Image = Image.open(io.BytesIO(image_bytes))
        input_image = resize_image_safe(input_image, MAX_DIMENSION)
        output_image = remove(input_image)
        output_buffer = io.BytesIO()
        output_image.save(output_buffer, format="PNG")

        result_bytes = output_buffer.getvalue()
        storage.upload_result(self.request.id, result_bytes)

        return {"status": "completed", "task_id": self.request.id}
    except Exception as exc:
        raise self.retry(exc=exc)
