from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque, DefaultDict

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int, window_seconds: int) -> None:
        super().__init__(app)
        self.limit = limit
        self.window = window_seconds
        self.calls: DefaultDict[str, Deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        client_ip = request.client.host if request.client else "anon"
        now = time.monotonic()
        history = self.calls[client_ip]
        while history and history[0] <= now - self.window:
            history.popleft()
        if len(history) >= self.limit:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
        history.append(now)
        response = await call_next(request)
        return response
