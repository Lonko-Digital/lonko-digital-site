"""Helpers to build synthetic Drive packages for bridge tests."""

from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path
from typing import Any

import yaml

from chronicles_bridge.hashutil import content_sha256, write_checksums


def write_png(path: Path, rgb: tuple[int, int, int] = (40, 80, 120), w: int = 64, h: int = 64) -> None:
    r, g, b = rgb

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + bytes([r, g, b]) * w for _ in range(h))
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def build_package(
    dest: Path,
    *,
    slug: str,
    package_id: str,
    meta: dict[str, Any],
    body: str,
    producer: str = "bridge-test",
) -> Path:
    """Create a complete Drive package at dest/slug with checksums + manifest."""
    package = dest / slug
    if package.exists():
        import shutil

        shutil.rmtree(package)
    assets = package / "assets"
    assets.mkdir(parents=True)
    write_png(assets / "social.png", (200, 40, 40))
    write_png(assets / "hero.png", (40, 40, 200))

    full_meta = {
        "title": meta.get("title", "Bridge Test Article"),
        "deck": meta.get("deck", "Synthetic package for Drive bridge acceptance."),
        "slug": meta.get("slug", slug),
        "topic": meta.get("topic", "Marketing"),
        "tags": meta.get("tags", ["bridge", "test"]),
        "content_type": meta.get("content_type", "Analysis"),
        "author": meta.get("author", "Lonko Digital"),
        "status": meta.get("status", "published"),
        "datePublished": meta.get("datePublished", "2026-09-17"),
        "dateModified": meta.get("dateModified", "2026-09-17"),
        "schema_type": meta.get("schema_type", "Article"),
        "seo_title": meta.get("seo_title"),
        "meta_description": meta.get("meta_description"),
        "og_title": meta.get("og_title"),
        "og_description": meta.get("og_description"),
        "social_image": "assets/social.png",
        "hero_image": "assets/hero.png",
        "hero_alt": meta.get("hero_alt", "Illustrative chart for bridge test"),
        "imagery_family": meta.get("imagery_family", "chart-diagram"),
        "hero_caption": meta.get("hero_caption"),
        "sources": meta.get(
            "sources",
            [{"url": "https://lonkodigital.com/", "description": "Lonko Digital"}],
        ),
        "placement": meta.get(
            "placement",
            {"featured": False, "sections": ["owners"]},
        ),
        "related": meta.get("related", []),
    }
    # Drop nulls for cleaner YAML
    full_meta = {k: v for k, v in full_meta.items() if v is not None}

    (package / "article.yaml").write_text(
        yaml.safe_dump(full_meta, sort_keys=True, allow_unicode=True),
        encoding="utf-8",
    )
    (package / "body.md").write_text(body.rstrip() + "\n", encoding="utf-8")
    write_checksums(package)
    digest = content_sha256(package)
    manifest = {
        "package_id": package_id,
        "slug": slug,
        "content_sha256": digest,
        "created_at": "2026-09-17T20:00:00Z",
        "producer": producer,
    }
    (package / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return package
