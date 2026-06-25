from celery.result import AsyncResult
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from src.core.celery_app import celery_app
from src.core.config import settings
from src.core.redis import get_redis
from src.models.schemas import TaskResponse, TaskStatusResponse

router = APIRouter()


@router.post("/remove-bg/", response_model=TaskResponse)
async def remove_background(file: UploadFile = File(...)) -> TaskResponse:
    contents = await file.read()

    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    task = celery_app.send_task("remove_bg", args=[contents])
    return TaskResponse(task_id=task.id)


@router.get("/tasks/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    result = AsyncResult(task_id, app=celery_app)

    response = TaskStatusResponse(
        task_id=task_id,
        status=result.state,
    )

    if result.ready():
        if result.successful():
            response.result = "completed"
        else:
            raise HTTPException(status_code=500, detail=str(result.result))

    return response


@router.get("/tasks/{task_id}/result")
async def get_task_result(task_id: str) -> Response:
    redis_client = await get_redis()
    result_data = await redis_client.get(f"result:{task_id}")

    if result_data is None:
        raise HTTPException(status_code=404, detail="Result not found")

    return Response(content=result_data, media_type="image/png")
