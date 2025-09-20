from __future__ import annotations

import argparse
from typing import List

import numpy as np

from app.config import get_settings
from app.db.session import SessionLocal
from app.models.wine import WineEmbedding
from app.services.retrieval import save_index

settings = get_settings()


def build_index() -> None:
    session = SessionLocal()
    try:
        embeddings: List[WineEmbedding] = session.query(WineEmbedding).all()
        image_vectors = []
        text_vectors = []
        image_ids = []
        text_ids = []
        image_version = settings.clip_model_version
        text_version = settings.text_model_version
        for emb in embeddings:
            if emb.image_vec:
                image_vectors.append(np.frombuffer(emb.image_vec, dtype=np.float32))
                image_ids.append(emb.wine_id)
                image_version = emb.model_version or image_version
            if emb.text_vec:
                text_vectors.append(np.frombuffer(emb.text_vec, dtype=np.float32))
                text_ids.append(emb.wine_id)
                text_version = emb.model_version or text_version
        if image_vectors:
            save_index(settings.index_image_path, image_ids, np.vstack(image_vectors), image_version)
        if text_vectors:
            save_index(settings.index_text_path, text_ids, np.vstack(text_vectors), text_version)
        print("Indexes built", flush=True)
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="WineLens CLI")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("build-index", help="Rebuild vector indexes")
    args = parser.parse_args()

    if args.command == "build-index":
        build_index()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
