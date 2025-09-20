from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

import numpy as np
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.wine import Wine, WineEmbedding
from app.services.embeddings import batch_cosine_similarity

settings = get_settings()


@dataclass
class RetrievalCandidate:
    wine: Wine
    score: float
    source: str


@dataclass
class LoadedIndex:
    ids: np.ndarray
    vectors: np.ndarray
    version: str


class RetrievalService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.image_index = self._load_index(settings.index_image_path)
        self.text_index = self._load_index(settings.index_text_path)

    def _load_index(self, path: Path) -> LoadedIndex | None:
        if not path.exists():
            return None
        data = np.load(path, allow_pickle=True)
        return LoadedIndex(
            ids=data["ids"],
            vectors=data["vectors"],
            version=str(data["version"]),
        )

    def _fallback_vectors(self, field: str) -> LoadedIndex | None:
        rows: List[WineEmbedding] = self.db.query(WineEmbedding).all()
        vectors = []
        ids = []
        for row in rows:
            blob = getattr(row, field)
            if not blob:
                continue
            vector = np.frombuffer(blob, dtype=np.float32)
            vectors.append(vector)
            ids.append(row.wine_id)
        if not ids:
            return None
        matrix = np.vstack(vectors)
        version = rows[0].model_version if rows else "unknown"
        return LoadedIndex(ids=np.array(ids), vectors=matrix, version=version)

    def _ensure_index(self, index: LoadedIndex | None, field: str) -> LoadedIndex | None:
        if index:
            return index
        return self._fallback_vectors(field)

    def search_image(self, vector: np.ndarray, top_k: int) -> List[RetrievalCandidate]:
        index = self._ensure_index(self.image_index, "image_vec")
        return self._search(index, vector, top_k, source="image")

    def search_text(self, vector: np.ndarray, top_k: int) -> List[RetrievalCandidate]:
        index = self._ensure_index(self.text_index, "text_vec")
        return self._search(index, vector, top_k, source="text")

    def _search(
        self, index: LoadedIndex | None, query_vec: np.ndarray, top_k: int, source: str
    ) -> List[RetrievalCandidate]:
        if not index or index.vectors.size == 0:
            return []
        scores = batch_cosine_similarity(query_vec, index.vectors)
        order = np.argsort(scores)[::-1][:top_k]
        candidates: List[RetrievalCandidate] = []
        for idx in order:
            wine_id = int(index.ids[idx])
            wine = self.db.query(Wine).filter(Wine.id == wine_id).first()
            if not wine:
                continue
            candidates.append(RetrievalCandidate(wine=wine, score=float(scores[idx]), source=source))
        return candidates

    def hybrid_candidates(
        self,
        image_candidates: Sequence[RetrievalCandidate],
        text_candidates: Sequence[RetrievalCandidate],
        alpha: float = 0.6,
        top_k: int = 5,
    ) -> List[RetrievalCandidate]:
        scores: dict[int, float] = {}
        wines: dict[int, Wine] = {}

        def accumulate(cands: Sequence[RetrievalCandidate], weight: float) -> None:
            for cand in cands:
                wines[cand.wine.id] = cand.wine
                scores[cand.wine.id] = scores.get(cand.wine.id, 0.0) + cand.score * weight

        accumulate(image_candidates, alpha)
        accumulate(text_candidates, 1 - alpha)
        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_k]
        return [RetrievalCandidate(wine=wines[wine_id], score=score, source="hybrid") for wine_id, score in ranked]


def serialize_vector(vector: np.ndarray) -> bytes:
    return vector.astype(np.float32).tobytes()


def save_index(path: Path, ids: Sequence[int], vectors: np.ndarray, version: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, ids=np.array(ids, dtype=np.int32), vectors=vectors.astype(np.float32), version=version)


__all__ = ["RetrievalService", "RetrievalCandidate", "serialize_vector", "save_index"]
