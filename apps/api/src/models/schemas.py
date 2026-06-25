from pydantic import BaseModel


class TaskResponse(BaseModel):
    task_id: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: str | None = None
