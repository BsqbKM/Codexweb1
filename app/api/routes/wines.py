from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.wine import Wine
from app.schemas.wine import WineSchema

router = APIRouter(prefix="/api/v1", tags=["wines"])


@router.get("/wines/{wine_id}", response_model=WineSchema)
def get_wine(
    wine_id: int = Path(..., description="Wine identifier"),
    db: Session = Depends(get_db),
) -> Wine:
    wine = db.query(Wine).filter(Wine.id == wine_id).first()
    if not wine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wine not found")
    return wine


__all__ = ["router"]
