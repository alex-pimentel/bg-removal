from __future__ import annotations

from typing import Any

from fastapi import Header

from src.core import clerk


async def optional_clerk_user(
    authorization: str | None = Header(default=None),
) -> dict[str, Any] | None:
    try:
        return clerk.optional_user(authorization)
    except ValueError:
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail="Invalid authentication token") from None
