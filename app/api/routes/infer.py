from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.config import get_settings
from app.schemas.inference import InferenceResponse
from app.services.inference import InferenceService

router = APIRouter(prefix="/api/v1", tags=["inference"])
settings = get_settings()
ALLOWED_MIME = {"image/jpeg", "image/png"}


@router.post("/infer", response_model=InferenceResponse)
async def infer(
    image: UploadFile = File(...),
    store_image: bool = Query(False, description="Persist the uploaded image for future retraining"),
    db: Session = Depends(get_db),
) -> InferenceResponse:
    if image.content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported file type")
    contents = await image.read()
    if len(contents) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large")
    image.file.seek(0)

    service = InferenceService(db)
    result = service.run(image, store_image=store_image)
    return result.response


__all__ = ["router"]
