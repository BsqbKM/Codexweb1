from __future__ import annotations

from PIL import Image

from app.models.wine import Wine, WineEmbedding, WineStyle
from app.services.embeddings import ImageEmbeddingService, TextEmbeddingService
from app.services.retrieval import RetrievalService, serialize_vector


def create_wine(session, name: str, region: str) -> tuple[Wine, bytes, bytes]:
    wine = Wine(
        canonical_name=name,
        producer="Test",
        label_text_norm=f"{name} {region}",
        country="Italy",
        region=region,
        grapes=["Sangiovese"],
        style=WineStyle.RED,
        quality_score=90.0,
    )
    session.add(wine)
    session.flush()

    seed = abs(hash(name)) % 255
    color = (seed, (seed * 3) % 255, (seed * 7) % 255)
    image = Image.new("RGB", (224, 224), color=color)
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
    return wine, image_vec, text_vec


def test_retrieval_hybrid(db_session) -> None:
    db_session.query(WineEmbedding).delete()
    db_session.query(Wine).delete()
    db_session.commit()

    wine1, image_vec, text_vec = create_wine(db_session, "Alpha", "Tuscany")
    create_wine(db_session, "Beta", "Piedmont")

    retrieval = RetrievalService(db_session)
    image_candidates = retrieval.search_image(image_vec, top_k=2)
    text_candidates = retrieval.search_text(text_vec, top_k=2)
    hybrid = retrieval.hybrid_candidates(image_candidates, text_candidates, top_k=2)

    assert hybrid
    assert hybrid[0].wine.id == wine1.id
