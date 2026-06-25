import json

import redis
from fastapi import HTTPException

def get_redis_client():
    try:
        redis_client = redis.Redis(
            host="redis",
            port=6379,
            decode_responses=True
        )
        return redis_client
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis connection failed: {str(e)}")

def enqueue_task(task_type: str, data: dict):
    redis_client = get_redis_client()
    redis_client.rpush(f"tasks:{task_type}", json.dumps(data))

def dequeue_task(task_type: str):
    redis_client = get_redis_client()
    task = redis_client.lpop(f"tasks:{task_type}")
    if task:
        return json.loads(task)
    return None