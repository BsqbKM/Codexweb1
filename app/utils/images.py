from __future__ import annotations

import io
from typing import Tuple

import numpy as np
from PIL import Image, ImageOps


def read_image(data: bytes) -> Image.Image:
    image = Image.open(io.BytesIO(data))
    image = ImageOps.exif_transpose(image)
    return image.convert("RGB")


def remove_exif(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=90)
    buffer.seek(0)
    return buffer.read()


def auto_crop_label(image: Image.Image) -> Image.Image:
    gray = image.convert("L")
    arr = np.array(gray)
    mask = arr > arr.mean()
    coords = np.argwhere(mask)
    if coords.size == 0:
        return image
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0)
    cropped = image.crop((x0, y0, x1, y1))
    if cropped.size[0] < 64 or cropped.size[1] < 64:
        return image
    return cropped


def resize_for_embedding(image: Image.Image, size: Tuple[int, int] = (224, 224)) -> Image.Image:
    return image.resize(size, Image.BICUBIC)


__all__ = ["read_image", "remove_exif", "auto_crop_label", "resize_for_embedding"]
