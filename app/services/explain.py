from __future__ import annotations

from typing import Iterable, List, Sequence

from app.services.retrieval import RetrievalCandidate
from app.utils.strings import top_tokens


class ExplainabilityService:
    def ocr_tokens(self, tokens: Iterable[str], top_k: int = 5) -> List[dict]:
        return [
            {"text": token, "weight": round(weight, 3)}
            for token, weight in top_tokens(tokens, top_k=top_k)
        ]

    def neighbors(self, candidates: Sequence[RetrievalCandidate], top_k: int = 3) -> List[dict]:
        return [
            {"wine_id": cand.wine.id, "sim": round(cand.score, 3)}
            for cand in candidates[:top_k]
        ]

    def feature_importances(self, importances: Sequence[tuple[str, float]], top_k: int = 5) -> List[dict]:
        return [
            {"name": name, "gain": round(float(value), 3)}
            for name, value in list(importances)[:top_k]
        ]


__all__ = ["ExplainabilityService"]
