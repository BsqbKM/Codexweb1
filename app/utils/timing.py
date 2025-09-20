from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Iterator


@contextmanager
def time_block() -> Iterator[callable[[], int]]:
    start = time.perf_counter()

    def elapsed() -> int:
        return int((time.perf_counter() - start) * 1000)

    yield elapsed


__all__ = ["time_block"]
