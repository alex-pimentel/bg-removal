from __future__ import annotations

from typing import Any

import httpx
from jose import jwt

from src.core.config import settings

_jwks_cache: tuple[dict[str, Any], float] | None = None
_JWKS_TTL = 3600.0


def _fetch_jwks() -> dict[str, Any]:
    global _jwks_cache
    import time

    if _jwks_cache is not None and _jwks_cache[1] > time.time():
        return _jwks_cache[0]

    response = httpx.get(settings.CLERK_JWKS_URL)
    response.raise_for_status()
    jwks: dict[str, Any] = response.json()
    _jwks_cache = (jwks, time.time() + _JWKS_TTL)
    return jwks


def verify_token(token: str) -> dict[str, Any]:
    if not settings.CLERK_JWKS_URL or not settings.CLERK_ISSUER:
        raise ValueError("Clerk is not configured")

    jwks = _fetch_jwks()
    try:
        claims: dict[str, Any] = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=settings.CLERK_AUDIENCE or None,
            issuer=settings.CLERK_ISSUER,
        )
    except Exception as exc:
        raise ValueError(f"Invalid token: {exc}") from exc
    return claims


def optional_user(authorization: str | None) -> dict[str, Any] | None:
    if not authorization:
        return None

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise ValueError("Invalid Authorization header")

    return verify_token(token)
