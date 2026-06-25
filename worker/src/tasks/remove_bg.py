import io

from PIL import Image
from rembg import remove

from src.worker import celery_app


@celery_app.task(name="remove_bg", bind=True, max_retries=3, default_retry_delay=5)
def remove_bg(self, image_bytes: bytes) -> dict:
    try:
        input_image = Image.open(io.BytesIO(image_bytes))
        output_image = remove(input_image)
        output_buffer = io.BytesIO()
        output_image.save(output_buffer, format="PNG")

        result_bytes = output_buffer.getvalue()

        from celery import current_app
        from redis import Redis

        r = Redis.from_url(current_app.conf.result_backend)
        r.set(f"result:{self.request.id}", result_bytes, ex=3600)

        return {"status": "completed", "task_id": self.request.id}
    except Exception as exc:
        raise self.retry(exc=exc)
