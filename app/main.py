from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import feedback, health, infer, wines
from app.config import get_settings
from app.db import session
from app.db.base import Base
from app.middleware.rate_limit import RateLimitMiddleware

settings = get_settings()
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    application = FastAPI(title=settings.app_name, version="0.1.0")

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_middleware(
        RateLimitMiddleware,
        limit=settings.rate_limit_calls,
        window_seconds=settings.rate_limit_period_seconds,
    )

    application.include_router(health.router)
    application.include_router(infer.router)
    application.include_router(wines.router)
    application.include_router(feedback.router)

    @application.on_event("startup")
    def startup() -> None:
        if settings.environment == "dev":
            Base.metadata.create_all(bind=session.engine)
            logger.info("Ensured database schema is created for dev environment")

    return application


app = create_app()


__all__ = ["app", "create_app"]
