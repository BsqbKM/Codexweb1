from __future__ import annotations

import uuid
from pathlib import Path

from app.config import get_settings

settings = get_settings()


class StorageService:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or settings.upload_storage_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, data: bytes, suffix: str = ".jpg") -> Path:
        filename = f"{uuid.uuid4()}{suffix}"
        path = self.base_dir / filename
        path.write_bytes(data)
        return path


__all__ = ["StorageService"]
