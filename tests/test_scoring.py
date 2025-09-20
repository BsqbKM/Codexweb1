from __future__ import annotations

import numpy as np

from app.services.scoring import QualityRegressor, build_feature_vector


def test_quality_regressor_fallback(tmp_path) -> None:
    regressor = QualityRegressor(model_path=tmp_path / "missing.joblib", meta_path=tmp_path / "missing.json")
    image_vec = np.ones(512, dtype=np.float32)
    features = build_feature_vector(image_vec, ["barolo", "2016"], region="Piedmont", grapes=["Nebbiolo"], vintage=2016)
    result = regressor.predict(features)
    assert 50.0 <= result.prediction <= 95.0
    assert result.importances
