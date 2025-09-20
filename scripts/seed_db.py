from __future__ import annotations

import json
import uuid
from pathlib import Path

import joblib
import numpy as np
from PIL import Image
from sqlalchemy import delete
from sqlalchemy.orm import Session
from sklearn.ensemble import GradientBoostingRegressor

from app.config import get_settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.wine import Wine, WineEmbedding, WineStyle
from app.services.embeddings import ImageEmbeddingService, TextEmbeddingService
from app.services.retrieval import serialize_vector
from app.services.scoring import build_feature_vector
from app.utils.strings import tokenize

settings = get_settings()


def synthetic_label_image(seed: str) -> Image.Image:
    digest = uuid.uuid5(uuid.NAMESPACE_DNS, seed).int
    color = ((digest >> 16) & 0xFF, (digest >> 8) & 0xFF, digest & 0xFF)
    image = Image.new("RGB", (224, 224), color=color)
    return image


def load_seed_data(path: Path) -> List[dict]:
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        raise ValueError("seed file must contain a list")
    return data


def seed_wines(session: Session, records: List[dict]) -> None:
    session.execute(delete(WineEmbedding))
    session.execute(delete(Wine))
    image_embedder = ImageEmbeddingService()
    text_embedder = TextEmbeddingService()

    for record in records:
        style_name = (record.get("style") or "unknown").upper()
        style = WineStyle[style_name] if style_name in WineStyle.__members__ else WineStyle.UNKNOWN
        wine = Wine(
            canonical_name=record["canonical_name"],
            producer=record.get("producer"),
            label_text_norm=record.get("label_text_norm"),
            country=record.get("country"),
            region=record.get("region"),
            subregion=record.get("subregion"),
            appellation=record.get("appellation"),
            grapes=record.get("grapes"),
            vintage=record.get("vintage"),
            style=style,
            quality_score=record.get("quality_score"),
            sources=record.get("sources"),
            image_url=record.get("image_url"),
        )
        session.add(wine)
        session.flush()

        label_text = wine.label_text_norm or wine.canonical_name
        text_embedding = text_embedder.embed(label_text)
        image = synthetic_label_image(wine.canonical_name)
        image_embedding = image_embedder.embed(image)

        embedding = WineEmbedding(
            wine_id=wine.id,
            image_vec=serialize_vector(image_embedding.vector),
            text_vec=serialize_vector(text_embedding.vector),
            model_version=image_embedding.version,
        )
        session.add(embedding)

    session.commit()


def train_regressor(session: Session) -> None:
    rows = session.query(Wine, WineEmbedding).join(WineEmbedding).all()
    feature_rows: List[List[float]] = []
    targets: List[float] = []

    feature_keys: List[str] = []

    for wine, embedding in rows:
        image_vec = np.frombuffer(embedding.image_vec, dtype=np.float32)
        tokens = tokenize(wine.label_text_norm or wine.canonical_name)
        features = build_feature_vector(image_vec, tokens, wine.region, wine.grapes, wine.vintage)
        for key in features.keys():
            if key not in feature_keys:
                feature_keys.append(key)
        feature_rows.append(features)
        targets.append(float(wine.quality_score or 80.0))

    if not feature_rows:
        return

    matrix = np.array([[row.get(key, 0.0) for key in feature_keys] for row in feature_rows], dtype=np.float32)
    model = GradientBoostingRegressor(random_state=42)
    model.fit(matrix, targets)

    joblib.dump({"model": model, "feature_names": feature_keys}, settings.regressor_path)
    meta = {"feature_importances": {name: float(val) for name, val in zip(feature_keys, model.feature_importances_)}}
    settings.regressor_meta_path.write_text(json.dumps(meta, indent=2))


def main() -> None:
    Base.metadata.create_all(bind=engine)
    records = load_seed_data(settings.seed_data_path)
    session = SessionLocal()
    try:
        seed_wines(session, records)
        train_regressor(session)
        print(f"Seeded {len(records)} wines", flush=True)
    finally:
        session.close()


if __name__ == "__main__":
    main()
