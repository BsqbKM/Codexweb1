from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    upload_id: Optional[str]
    chosen_wine_id: Optional[int]
    correct: bool = Field(..., description="Whether the prediction was correct")
    notes: Optional[str]


class FeedbackResponse(BaseModel):
    status: str = "ok"


__all__ = ["FeedbackRequest", "FeedbackResponse"]
