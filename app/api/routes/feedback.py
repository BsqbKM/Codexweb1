from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.wine import Feedback, Upload, Wine
from app.schemas.feedback import FeedbackRequest, FeedbackResponse

router = APIRouter(prefix="/api/v1", tags=["feedback"])


@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(payload: FeedbackRequest, db: Session = Depends(get_db)) -> FeedbackResponse:
    upload_id = uuid.UUID(payload.upload_id) if payload.upload_id else None
    upload = db.query(Upload).filter(Upload.id == upload_id).first() if upload_id else None
    if upload_id and not upload:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found")

    if payload.chosen_wine_id:
        wine = db.query(Wine).filter(Wine.id == payload.chosen_wine_id).first()
        if not wine:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wine not found")

    feedback = Feedback(
        upload_id=upload_id,
        chosen_wine_id=payload.chosen_wine_id,
        correct=payload.correct,
        notes=payload.notes,
    )
    db.add(feedback)
    db.commit()
    return FeedbackResponse()


__all__ = ["router"]
