from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field


class OCRToken(BaseModel):
    text: str
    weight: float


class Neighbor(BaseModel):
    wine_id: int
    sim: float


class FeatureImportance(BaseModel):
    name: str
    gain: float


class InferenceCandidate(BaseModel):
    wine_id: int
    name: str
    producer: Optional[str]
    vintage: Optional[int]
    match_score: float


class InferenceFinal(BaseModel):
    wine_id: Optional[int]
    pred_quality: float = Field(..., ge=0, le=100)
    conf_interval: Tuple[float, float]
    explain: Dict[str, Any]


class InferenceDebug(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    model_versions: Dict[str, str]
    latency_ms: int


class InferenceResponse(BaseModel):
    candidates: List[InferenceCandidate]
    final: InferenceFinal
    debug: InferenceDebug


class InferencePayload(BaseModel):
    store_image: Optional[bool] = False


__all__ = [
    "InferenceResponse",
    "InferenceCandidate",
    "InferenceFinal",
    "InferenceDebug",
    "InferencePayload",
]
