from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="WINELENS_", case_sensitive=False)

    app_name: str = "WineLens"
    environment: str = "dev"
    debug: bool = False

    database_url: str = "sqlite+aiosqlite:///./winelens.db"
    sync_database_url: str = "sqlite:///./winelens.db"

    storage_dir: Path = Path("storage")
    seed_data_path: Path = Path("data/seed_wines.json")

    max_upload_size_mb: int = 8
    allowed_origins: List[str] = ["*"]

    store_images_default: bool = False
    log_pii: bool = False

    rate_limit_calls: int = 60
    rate_limit_period_seconds: int = 60

    default_top_k: int = 5

    clip_model_version: str = "clip-vit-b32-stub"
    text_model_version: str = "sbert-minilm-stub"
    regressor_version: str = "gbm-stub"

    index_image_path: Path = Path("storage/image_index.npz")
    index_text_path: Path = Path("storage/text_index.npz")
    regressor_path: Path = Path("storage/quality_regressor.joblib")
    regressor_meta_path: Path = Path("storage/quality_regressor_meta.json")

    upload_storage_dir: Path = Path("storage/uploads")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    settings.upload_storage_dir.mkdir(parents=True, exist_ok=True)
    return settings


__all__ = ["Settings", "get_settings"]
