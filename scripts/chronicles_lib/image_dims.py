"""Read intrinsic image dimensions without a full media pipeline.

Supports PNG, JPEG, WebP, and SVG (viewBox / width+height). Returns None when
dimensions cannot be determined. Used for accurate hero <img> attrs and OG metas.
"""

from __future__ import annotations

import re
import struct
from pathlib import Path


def read_image_size(path: Path) -> tuple[int, int] | None:
    """Return (width, height) for a local image file, or None if unknown."""
    path = Path(path)
    if not path.is_file():
        return None
    suffix = path.suffix.lower()
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if suffix == ".png" or data[:8] == b"\x89PNG\r\n\x1a\n":
        return _png_size(data)
    if suffix in {".jpg", ".jpeg"} or data[:2] == b"\xff\xd8":
        return _jpeg_size(data)
    if suffix == ".webp" or (data[:4] == b"RIFF" and data[8:12] == b"WEBP"):
        return _webp_size(data)
    if suffix == ".svg" or b"<svg" in data[:512].lower():
        return _svg_size(data)
    return None


def _png_size(data: bytes) -> tuple[int, int] | None:
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    w, h = struct.unpack(">II", data[16:24])
    if w <= 0 or h <= 0:
        return None
    return w, h


def _jpeg_size(data: bytes) -> tuple[int, int] | None:
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        return None
    i = 2
    n = len(data)
    while i + 9 < n:
        if data[i] != 0xFF:
            return None
        while i < n and data[i] == 0xFF:
            i += 1
        if i >= n:
            return None
        marker = data[i]
        i += 1
        # Standalone markers without length
        if marker in {0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
            continue
        if i + 2 > n:
            return None
        length = struct.unpack(">H", data[i : i + 2])[0]
        if length < 2 or i + length > n:
            return None
        # SOF0–SOF3, SOF5–SOF7, SOF9–SOF11, SOF13–SOF15
        if marker in {
            0xC0,
            0xC1,
            0xC2,
            0xC3,
            0xC5,
            0xC6,
            0xC7,
            0xC9,
            0xCA,
            0xCB,
            0xCD,
            0xCE,
            0xCF,
        }:
            if length < 7:
                return None
            h, w = struct.unpack(">HH", data[i + 3 : i + 7])
            if w <= 0 or h <= 0:
                return None
            return w, h
        i += length
    return None


def _webp_size(data: bytes) -> tuple[int, int] | None:
    if len(data) < 30 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return None
    chunk = data[12:16]
    if chunk == b"VP8X" and len(data) >= 30:
        # Canvas size is 24-bit little-endian minus one
        w = 1 + int.from_bytes(data[24:27], "little")
        h = 1 + int.from_bytes(data[27:30], "little")
        return (w, h) if w > 0 and h > 0 else None
    if chunk == b"VP8L" and len(data) >= 25:
        bits = struct.unpack("<I", data[21:25])[0]
        w = (bits & 0x3FFF) + 1
        h = ((bits >> 14) & 0x3FFF) + 1
        return (w, h) if w > 0 and h > 0 else None
    if chunk == b"VP8 " and len(data) >= 30:
        # Lossy bitstream frame header starts at offset 23
        if data[23] != 0x9D or data[24:27] != b"\x01\x2a":
            return None
        w = struct.unpack("<H", data[26:28])[0] & 0x3FFF
        h = struct.unpack("<H", data[28:30])[0] & 0x3FFF
        return (w, h) if w > 0 and h > 0 else None
    return None


_SVG_VIEWBOX = re.compile(
    r"viewBox\s*=\s*[\"']\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s*[\"']",
    re.IGNORECASE,
)
_SVG_WIDTH = re.compile(
    r"<svg[^>]*\bwidth\s*=\s*[\"']\s*([0-9.]+)\s*(?:px)?\s*[\"']",
    re.IGNORECASE | re.DOTALL,
)
_SVG_HEIGHT = re.compile(
    r"<svg[^>]*\bheight\s*=\s*[\"']\s*([0-9.]+)\s*(?:px)?\s*[\"']",
    re.IGNORECASE | re.DOTALL,
)


def _svg_size(data: bytes) -> tuple[int, int] | None:
    try:
        text = data.decode("utf-8", errors="ignore")
    except Exception:  # noqa: BLE001
        return None
    # Prefer explicit width/height on <svg> when both are numeric px values
    wm = _SVG_WIDTH.search(text)
    hm = _SVG_HEIGHT.search(text)
    if wm and hm:
        try:
            w = int(round(float(wm.group(1))))
            h = int(round(float(hm.group(1))))
            if w > 0 and h > 0:
                return w, h
        except ValueError:
            pass
    vm = _SVG_VIEWBOX.search(text)
    if not vm:
        return None
    try:
        _min_x, _min_y, w_f, h_f = (float(vm.group(i)) for i in range(1, 5))
        w = int(round(w_f))
        h = int(round(h_f))
    except ValueError:
        return None
    if w <= 0 or h <= 0:
        return None
    return w, h
