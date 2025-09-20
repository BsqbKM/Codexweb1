from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Iterable

import numpy as np
from PIL import Image

from app.config import get_settings
from app.utils.images import resize_for_embedding
from app.utils.strings import tokenize

settings = get_settings()


@dataclass
class EmbeddingResult:
    vector: np.ndarray
    version: str


def _normalize(vector: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm


class ImageEmbeddingService:
    def __init__(self, output_dim: int = 512) -> None:
        self.output_dim = output_dim
        self.version = settings.clip_model_version
        base_rng = np.random.default_rng(42)
        self.projection = base_rng.normal(0, 1, (output_dim, 64 * 64))

    def embed(self, image: Image.Image) -> EmbeddingResult:
        prepared = resize_for_embedding(image, (64, 64))
        arr = np.asarray(prepared, dtype=np.float32) / 255.0
        gray = arr.mean(axis=2).flatten()
        vector = self.projection @ gray
        vector = _normalize(vector.astype(np.float32))
        return EmbeddingResult(vector=vector, version=self.version)


class TextEmbeddingService:
    def __init__(self, output_dim: int = 384) -> None:
        self.output_dim = output_dim
        self.version = settings.text_model_version

    def _token_hash(self, token: str) -> float:
        digest = hashlib.sha1(token.encode("utf-8")).digest()
        return int.from_bytes(digest[:4], "big") / 2**32

    def embed(self, text: str) -> EmbeddingResult:
        tokens = list(tokenize(text)) or [""]
        vec = np.zeros(self.output_dim, dtype=np.float32)
        for token in tokens:
            value = self._token_hash(token)
            idx = int(value * self.output_dim) % self.output_dim
            vec[idx] += 1.0
        vector = _normalize(vec)
        return EmbeddingResult(vector=vector, version=self.version)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def hybrid_score(sim_img: float, sim_txt: float, alpha: float = 0.6) -> float:
    return alpha * sim_img + (1 - alpha) * sim_txt


def batch_cosine_similarity(query: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    if matrix.size == 0:
        return np.zeros(0, dtype=np.float32)
    norms = np.linalg.norm(matrix, axis=1) * np.linalg.norm(query)
    norms[norms == 0] = 1.0
    scores = matrix @ query / norms
    return scores.astype(np.float32)


__all__ = [
    "ImageEmbeddingService",
    "TextEmbeddingService",
    "EmbeddingResult",
    "cosine_similarity",
    "hybrid_score",
    "batch_cosine_similarity",
]
