from __future__ import annotations

from app.utils.strings import extract_years, normalize_ocr_text, tokenize, top_tokens


def test_normalize_and_tokenize() -> None:
    text = "Château di Testo 2016!!!"
    normalized = normalize_ocr_text(text)
    assert "chateau" in normalized
    tokens = tokenize(text)
    assert tokens == ["chateau", "di", "testo", "2016"]


def test_extract_years() -> None:
    text = "Vintage 1999 Reserve 2015"
    years = extract_years(text)
    assert years == [1999, 2015]


def test_top_tokens() -> None:
    tokens = ["barolo", "barolo", "piedmont", "2016"]
    top = top_tokens(tokens, top_k=2)
    assert top[0][0] == "barolo"
    assert round(top[0][1], 2) == 0.5
