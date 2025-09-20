from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import joblib
import numpy as np

from app.config import get_settings

settings = get_settings()

FeatureMap = Dict[str, float]


def build_feature_vector(
    image_vec: np.ndarray, text_tokens: Iterable[str], region: str | None, grapes: Iterable[str] | None, vintage: int | None
) -> FeatureMap:
    tokens = list(text_tokens)
    feature_map: FeatureMap = {
        "image_mean": float(image_vec.mean()),
        "image_std": float(image_vec.std()),
        "text_density": float(len(tokens)),
    }
    if vintage:
        feature_map["vintage"] = float(vintage)
    if region:
        feature_map[f"region::{region.lower()}"] = 1.0
    if grapes:
        for grape in grapes:
            feature_map[f"grape::{grape.lower()}"] = 1.0
    return feature_map


@dataclass
class RegressionResult:
    prediction: float
    importances: List[Tuple[str, float]]


class QualityRegressor:
    def __init__(self, model_path: Path | None = None, meta_path: Path | None = None) -> None:
        self.model_path = model_path or settings.regressor_path
        self.meta_path = meta_path or settings.regressor_meta_path
        self.model = None
        self.feature_names: List[str] | None = None
        self.feature_importances: Dict[str, float] = {}
        self._load()

    def _load(self) -> None:
        if self.model_path.exists():
            data = joblib.load(self.model_path)
            self.model = data.get("model")
            self.feature_names = data.get("feature_names")
        if self.meta_path.exists():
            try:
                meta = json.loads(self.meta_path.read_text())
                self.feature_importances = meta.get("feature_importances", {})
            except json.JSONDecodeError:
                self.feature_importances = {}

    def _vectorize(self, features: FeatureMap) -> np.ndarray:
        keys = self.feature_names or sorted(features.keys())
        return np.array([features.get(key, 0.0) for key in keys], dtype=np.float32)

    def predict(self, features: FeatureMap) -> RegressionResult:
        if self.model is not None and self.feature_names is not None:
            vector = self._vectorize(features)
            pred = float(self.model.predict([vector])[0])
            importances = self.feature_importances or {
                name: float(abs(weight))
                for name, weight in zip(self.feature_names, getattr(self.model, "feature_importances_", []))
            }
            ranked = sorted(importances.items(), key=lambda item: item[1], reverse=True)
            return RegressionResult(prediction=pred, importances=ranked[:5])
        # Fallback heuristic
        base = 75.0
        base += features.get("image_mean", 0.0) * 10
        base += features.get("image_std", 0.0) * 5
        if vintage := features.get("vintage"):
            base += (vintage - 2000) * 0.1
        if grapes := [k for k in features if k.startswith("grape::")]:
            base += len(grapes) * 0.5
        base = max(50.0, min(95.0, base))
        ranked = sorted(((key, value) for key, value in features.items()), key=lambda item: abs(item[1]), reverse=True)[:5]
        return RegressionResult(prediction=base, importances=ranked)


__all__ = ["QualityRegressor", "build_feature_vector", "RegressionResult"]
