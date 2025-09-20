from __future__ import annotations

import time
from pathlib import Path
from tempfile import SpooledTemporaryFile

from fastapi import UploadFile

from app.db.session import SessionLocal
from app.services.inference import InferenceService


SAMPLE_DIR = Path("samples/labels")


def run_sample(path: Path, service: InferenceService) -> float:
    data = path.read_bytes()
    file_obj = SpooledTemporaryFile(max_size=len(data))
    file_obj.write(data)
    file_obj.seek(0)
    upload = UploadFile(filename=path.name, file=file_obj, content_type="image/jpeg")
    start = time.perf_counter()
    service.run(upload, store_image=False)
    latency = (time.perf_counter() - start) * 1000
    file_obj.close()
    return latency


def main() -> None:
    session = SessionLocal()
    try:
        service = InferenceService(session)
        latencies = []
        for path in SAMPLE_DIR.glob("*.jpg"):
            latency = run_sample(path, service)
            latencies.append(latency)
            print(f"Processed {path.name} in {latency:.2f} ms")
        if latencies:
            avg = sum(latencies) / len(latencies)
            p95 = sorted(latencies)[int(len(latencies) * 0.95) - 1] if latencies else 0
            print(f"Average latency: {avg:.2f} ms | p95: {p95:.2f} ms")
        else:
            print("No samples found. Add JPEG files to samples/labels/")
    finally:
        session.close()


if __name__ == "__main__":
    main()
