from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from PIL import Image

from app.utils.strings import normalize_ocr_text


class OCRBackend(Protocol):
    def extract(self, image: Image.Image) -> str: ...


@dataclass
class PytesseractBackend:
    def extract(self, image: Image.Image) -> str:
        try:
            import pytesseract
        except Exception:
            return ""
        return pytesseract.image_to_string(image)


@dataclass
class EasyOCRBackend:
    def extract(self, image: Image.Image) -> str:
        try:
            import easyocr
        except Exception:
            return ""
        reader = easyocr.Reader(["en", "it", "fr", "es", "ru"], gpu=False)
        results = reader.readtext(image, detail=0)
        return " \n".join(results)


@dataclass
class DummyBackend:
    fallback_text: str = ""

    def extract(self, image: Image.Image) -> str:
        return self.fallback_text


class OCRService:
    def __init__(self, backend: OCRBackend | None = None) -> None:
        self.backend = backend or PytesseractBackend()

    def extract_text(self, image: Image.Image) -> str:
        raw_text = self.backend.extract(image) or ""
        return normalize_ocr_text(raw_text)


__all__ = ["OCRService", "PytesseractBackend", "EasyOCRBackend", "DummyBackend"]
