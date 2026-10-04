from typing import Annotated, Any

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import RedirectResponse

from src.api.deps import optional_clerk_user
from src.core import r2
from src.core.celery_app import celery_app
from src.core.config import settings
from src.models.schemas import TaskResponse, TaskStatusResponse

router = APIRouter()


@router.post("/remove-bg/", response_model=TaskResponse)
async def remove_background(
    file: Annotated[UploadFile, File(...)],
    user: Annotated[dict[str, Any] | None, Depends(optional_clerk_user)] = None,
) -> TaskResponse:
    contents = await file.read()

    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    task = celery_app.send_task(
        "remove_bg",
        args=[contents],
        queue=settings.CELERY_QUEUE,
    )

    r2.upload_input(
        task.id,
        file.filename or "upload",
        contents,
        content_type=file.content_type or "application/octet-stream",
    )

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
async def get_task_result(task_id: str) -> RedirectResponse:
    try:
        url = r2.presigned_result_url(task_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail="Result not found") from exc

    return RedirectResponse(url=url, status_code=307)
