from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/healthz")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


__all__ = ["router"]
