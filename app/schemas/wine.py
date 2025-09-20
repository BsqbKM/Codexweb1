from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.wine import WineStyle


class WineSchema(BaseModel):
    id: int
    canonical_name: str
    producer: Optional[str]
    label_text_norm: Optional[str]
    country: Optional[str]
    region: Optional[str]
    subregion: Optional[str]
    appellation: Optional[str]
    grapes: Optional[dict]
    vintage: Optional[int]
    style: WineStyle
    quality_score: Optional[float]
    sources: Optional[dict]
    image_url: Optional[str]

    model_config = ConfigDict(from_attributes=True)


__all__ = ["WineSchema"]
