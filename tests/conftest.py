from __future__ import annotations

import importlib
from pathlib import Path
from typing import Generator

import pytest

from app.config import get_settings


def _configure_settings(tmp_path: Path) -> None:
    get_settings.cache_clear()  # type: ignore[attr-defined]
    import app.config as config_module
    importlib.reload(config_module)
    config_module.get_settings.cache_clear()  # type: ignore[attr-defined]
    settings = config_module.get_settings()
    settings.sync_database_url = f"sqlite:///{tmp_path}"
    settings.database_url = f"sqlite+aiosqlite:///{tmp_path}"


@pytest.fixture(scope="session")
def db_session_local(tmp_path_factory: pytest.TempPathFactory) -> Generator:
    db_path = tmp_path_factory.mktemp("db") / "test.db"
    _configure_settings(db_path)
    import app.db.session as session_module
    importlib.reload(session_module)
    from app.db.base import Base

    Base.metadata.create_all(bind=session_module.engine)

    yield session_module.SessionLocal


@pytest.fixture()
def db_session(db_session_local) -> Generator:
    session = db_session_local()
    try:
        yield session
    finally:
        session.close()
