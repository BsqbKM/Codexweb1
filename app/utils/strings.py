from __future__ import annotations

import re
import unicodedata
from typing import Iterable, List

YEAR_PATTERN = re.compile(r"\b((?:19|20)\d{2})\b")


def strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def normalize_ocr_text(text: str) -> str:
    text = text.lower()
    text = strip_accents(text)
    text = re.sub(r"[^a-z0-9\s\-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_years(text: str) -> List[int]:
    return [int(match) for match in YEAR_PATTERN.findall(text)]


def tokenize(text: str) -> List[str]:
    return [token for token in normalize_ocr_text(text).split(" ") if token]


def top_tokens(tokens: Iterable[str], top_k: int = 5) -> List[tuple[str, float]]:
    freq: dict[str, int] = {}
    for token in tokens:
        freq[token] = freq.get(token, 0) + 1
    total = sum(freq.values()) or 1
    sorted_items = sorted(freq.items(), key=lambda item: item[1], reverse=True)
    return [(token, count / total) for token, count in sorted_items[:top_k]]


__all__ = ["normalize_ocr_text", "extract_years", "tokenize", "top_tokens", "strip_accents"]
