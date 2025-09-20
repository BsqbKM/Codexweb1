from __future__ import annotations

from tempfile import SpooledTemporaryFile

import pytest
from fastapi import UploadFile
from PIL import Image

from app.models.wine import Wine, WineEmbedding, WineStyle
from app.schemas.inference import InferenceResponse
from app.services.embeddings import ImageEmbeddingService, TextEmbeddingService
from app.services.inference import InferenceService
from app.services.ocr import DummyBackend, OCRService
from app.services.retrieval import serialize_vector


def prepare_wine(session) -> tuple[Wine, SpooledTemporaryFile]:
    wine = Wine(
        canonical_name="Alpha Selection",
        producer="Test Winery",
        label_text_norm="alpha selection tuscany 2018",
        country="Italy",
        region="Tuscany",
        grapes=["Sangiovese"],
        style=WineStyle.RED,
        vintage=2018,
        quality_score=92.5,
    )
    session.add(wine)
    session.flush()

    image = Image.new("RGB", (224, 224), color=(180, 60, 60))
    image_embedder = ImageEmbeddingService()
    text_embedder = TextEmbeddingService()
    image_vec = image_embedder.embed(image).vector
    text_vec = text_embedder.embed(wine.label_text_norm).vector
    embedding = WineEmbedding(
        wine_id=wine.id,
        image_vec=serialize_vector(image_vec),
        text_vec=serialize_vector(text_vec),
        model_version=image_embedder.version,
    )
    session.add(embedding)
    session.commit()

    buffer = SpooledTemporaryFile(max_size=1_000_000, mode="w+b")
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    return wine, buffer


def test_inference_service_matches_seed(db_session) -> None:
    wine, buffer = prepare_wine(db_session)
    upload_file = UploadFile(buffer, filename="sample.jpg")

    ocr_service = OCRService(backend=DummyBackend("Alpha Selection Tuscany 2018"))
    service = InferenceService(
        db_session,
        ocr_service=ocr_service,
        image_embedder=ImageEmbeddingService(),
        text_embedder=TextEmbeddingService(),
    )

    result = service.run(upload_file, store_image=False)
    response = result.response
    assert isinstance(response, InferenceResponse)
    assert response.final.wine_id == wine.id
    assert pytest.approx(response.final.pred_quality, rel=1e-3) == wine.quality_score
    assert response.candidates
