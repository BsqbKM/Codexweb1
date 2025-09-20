from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum as PgEnum, Float, ForeignKey, Integer, JSON, LargeBinary, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class WineStyle(str, Enum):
    RED = "red"
    WHITE = "white"
    ROSE = "rose"
    SPARKLING = "sparkling"
    DESSERT = "dessert"
    FORTIFIED = "fortified"
    UNKNOWN = "unknown"


class Wine(Base):
    __tablename__ = "wine"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    canonical_name: Mapped[str] = mapped_column(String(255), nullable=False)
    producer: Mapped[Optional[str]] = mapped_column(String(255))
    label_text_norm: Mapped[Optional[str]] = mapped_column(Text)
    country: Mapped[Optional[str]] = mapped_column(String(128))
    region: Mapped[Optional[str]] = mapped_column(String(128))
    subregion: Mapped[Optional[str]] = mapped_column(String(128))
    appellation: Mapped[Optional[str]] = mapped_column(String(128))
    grapes: Mapped[Optional[dict]] = mapped_column(JSON)
    vintage: Mapped[Optional[int]] = mapped_column(Integer)
    style: Mapped[WineStyle] = mapped_column(PgEnum(WineStyle), default=WineStyle.UNKNOWN)
    quality_score: Mapped[Optional[float]] = mapped_column(Float)
    sources: Mapped[Optional[dict]] = mapped_column(JSON)
    image_url: Mapped[Optional[str]] = mapped_column(String(512))

    embeddings: Mapped["WineEmbedding"] = relationship(back_populates="wine", uselist=False)
    inference_logs: Mapped[list["InferenceLog"]] = relationship(back_populates="wine")


class WineEmbedding(Base):
    __tablename__ = "wine_embedding"

    wine_id: Mapped[int] = mapped_column(ForeignKey("wine.id", ondelete="CASCADE"), primary_key=True)
    image_vec: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    text_vec: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    model_version: Mapped[str] = mapped_column(String(64), default="unknown")

    wine: Mapped[Wine] = relationship(back_populates="embeddings")


class Upload(Base):
    __tablename__ = "upload"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_session_id: Mapped[Optional[str]] = mapped_column(String(128))
    stored_path: Mapped[Optional[str]] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    store_image: Mapped[bool] = mapped_column(Boolean, default=False)
    consent_flags: Mapped[Optional[dict]] = mapped_column(JSON)

    inference_logs: Mapped[list["InferenceLog"]] = relationship(back_populates="upload")


class InferenceLog(Base):
    __tablename__ = "inference_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    upload_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("upload.id"), nullable=True)
    wine_id: Mapped[Optional[int]] = mapped_column(ForeignKey("wine.id"), nullable=True)
    topk: Mapped[Optional[dict]] = mapped_column(JSON)
    final_score: Mapped[Optional[float]] = mapped_column(Float)
    explain: Mapped[Optional[dict]] = mapped_column(JSON)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer)
    model_versions: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    upload: Mapped[Optional[Upload]] = relationship(back_populates="inference_logs")
    wine: Mapped[Optional[Wine]] = relationship(back_populates="inference_logs")


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    upload_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("upload.id"), nullable=True)
    chosen_wine_id: Mapped[Optional[int]] = mapped_column(ForeignKey("wine.id"), nullable=True)
    correct: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    upload: Mapped[Optional[Upload]] = relationship()
    wine: Mapped[Optional[Wine]] = relationship()


__all__ = [
    "Wine",
    "WineEmbedding",
    "Upload",
    "InferenceLog",
    "Feedback",
    "WineStyle",
]
