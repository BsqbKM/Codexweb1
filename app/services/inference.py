from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.wine import InferenceLog, Upload
from app.schemas.inference import InferenceCandidate, InferenceDebug, InferenceFinal, InferenceResponse
from app.services.embeddings import ImageEmbeddingService, TextEmbeddingService
from app.services.explain import ExplainabilityService
from app.services.ocr import OCRService
from app.services.retrieval import RetrievalCandidate, RetrievalService
from app.services.scoring import QualityRegressor, build_feature_vector
from app.services.storage import StorageService
from app.utils.images import auto_crop_label, read_image, remove_exif
from app.utils.strings import tokenize
from app.utils.timing import time_block

settings = get_settings()


@dataclass
class InferenceOutput:
    response: InferenceResponse
    upload: Optional[Upload]


class InferenceService:
    def __init__(
        self,
        db: Session,
        ocr_service: OCRService | None = None,
        image_embedder: ImageEmbeddingService | None = None,
        text_embedder: TextEmbeddingService | None = None,
        quality_regressor: QualityRegressor | None = None,
        retrieval_service: RetrievalService | None = None,
        explain_service: ExplainabilityService | None = None,
        storage_service: StorageService | None = None,
    ) -> None:
        self.db = db
        self.ocr = ocr_service or OCRService()
        self.image_embedder = image_embedder or ImageEmbeddingService()
        self.text_embedder = text_embedder or TextEmbeddingService()
        self.regressor = quality_regressor or QualityRegressor()
        self.retrieval = retrieval_service or RetrievalService(db)
        self.explain = explain_service or ExplainabilityService()
        self.storage = storage_service or StorageService()

    def _store_upload(self, image_bytes: bytes, store_image: bool) -> Upload:
        upload = Upload(store_image=store_image)
        if store_image:
            path = self.storage.save(image_bytes)
            upload.stored_path = str(path)
        self.db.add(upload)
        self.db.commit()
        self.db.refresh(upload)
        return upload

    def _serialize_candidates(self, candidates: List[RetrievalCandidate]) -> List[dict]:
        return [
            {
                "wine_id": cand.wine.id,
                "name": cand.wine.canonical_name,
                "producer": cand.wine.producer,
                "vintage": cand.wine.vintage,
                "match_score": cand.score,
            }
            for cand in candidates
        ]

    def run(self, file: UploadFile, store_image: bool | None = None, top_k: int | None = None) -> InferenceOutput:
        raw_bytes = file.file.read()
        image = read_image(raw_bytes)
        cleaned_bytes = remove_exif(image)
        cropped = auto_crop_label(image)

        upload: Optional[Upload] = None
        if store_image or (store_image is None and settings.store_images_default):
            upload = self._store_upload(cleaned_bytes, True)
        else:
            upload = self._store_upload(b"", False)

        with time_block() as elapsed:
            ocr_text = self.ocr.extract_text(cropped)
            image_embedding = self.image_embedder.embed(cropped)
            text_embedding = self.text_embedder.embed(ocr_text)

            top_k = top_k or settings.default_top_k
            image_candidates = self.retrieval.search_image(image_embedding.vector, top_k)
            text_candidates = self.retrieval.search_text(text_embedding.vector, top_k)
            hybrid_candidates = self.retrieval.hybrid_candidates(image_candidates, text_candidates, top_k=top_k)

            all_candidates = hybrid_candidates or image_candidates or text_candidates
            tokens = tokenize(ocr_text)

            best_candidate: Optional[RetrievalCandidate] = all_candidates[0] if all_candidates else None
            if best_candidate and best_candidate.wine.quality_score is not None:
                final_score = float(best_candidate.wine.quality_score)
                conf_interval = (
                    max(0.0, final_score - 3.0),
                    min(100.0, final_score + 3.0),
                )
                feature_importances = [("db_quality", 1.0)]
            else:
                grapes = (best_candidate.wine.grapes or []) if best_candidate else []
                region = best_candidate.wine.region if best_candidate else None
                vintage = best_candidate.wine.vintage if best_candidate else None
                features = build_feature_vector(
                    image_embedding.vector, tokens, region=region, grapes=grapes, vintage=vintage
                )
                regression = self.regressor.predict(features)
                final_score = float(max(0.0, min(100.0, regression.prediction)))
                conf_interval = (
                    max(0.0, final_score - 5.0),
                    min(100.0, final_score + 5.0),
                )
                feature_importances = regression.importances

            explain_payload = {
                "ocr_tokens": self.explain.ocr_tokens(tokens),
                "image_neighbors": self.explain.neighbors(all_candidates),
                "features": self.explain.feature_importances(feature_importances),
            }

            final_payload = InferenceFinal(
                wine_id=best_candidate.wine.id if best_candidate else None,
                pred_quality=final_score,
                conf_interval=conf_interval,
                explain=explain_payload,
            )

            response = InferenceResponse(
                candidates=[
                    InferenceCandidate(
                        wine_id=cand.wine.id,
                        name=cand.wine.canonical_name,
                        producer=cand.wine.producer,
                        vintage=cand.wine.vintage,
                        match_score=float(cand.score),
                    )
                    for cand in all_candidates[:3]
                ],
                final=final_payload,
                debug=InferenceDebug(
                    model_versions={
                        "clip": image_embedding.version,
                        "ocr": self.ocr.backend.__class__.__name__,
                        "text": text_embedding.version,
                        "regressor": self.regressor.model_path.name if self.regressor.model_path.exists() else "heuristic",
                    },
                    latency_ms=elapsed(),
                ),
            )

        topk_payload = self._serialize_candidates(all_candidates[:top_k])
        log_entry = InferenceLog(
            upload_id=upload.id if upload else None,
            wine_id=best_candidate.wine.id if best_candidate else None,
            topk=topk_payload,
            final_score=final_score,
            explain=explain_payload,
            latency_ms=response.debug.latency_ms,
            model_versions=response.debug.model_versions,
        )
        self.db.add(log_entry)
        self.db.commit()

        return InferenceOutput(response=response, upload=upload)


__all__ = ["InferenceService", "InferenceOutput"]
