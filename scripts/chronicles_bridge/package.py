"""Drive package load, raster checks, and staging into chronicles/content."""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from chronicles_lib.model import Article, load_article
from chronicles_lib.validate import validate_articles

from .hashutil import content_sha256, verify_checksums

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RASTER_SUFFIXES = frozenset({".png", ".jpg", ".jpeg", ".webp", ".avif"})
ALLOWED_SUFFIXES = RASTER_SUFFIXES | frozenset(
    {".md", ".yaml", ".yml", ".json", ".txt"}
)
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_PACKAGE_BYTES = 32 * 1024 * 1024

# Temporary fail-safe flag — soft-retire is implemented; keep False.
QUARANTINE_RETIREMENT_PACKAGES = False


@dataclass
class DriveManifest:
    package_id: str
    slug: str
    content_sha256: str
    created_at: str
    producer: str

    @classmethod
    def load(cls, path: Path) -> DriveManifest:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("manifest.json must be a JSON object")
        required = ("package_id", "slug", "content_sha256", "created_at", "producer")
        missing = [k for k in required if not str(raw.get(k, "")).strip()]
        if missing:
            raise ValueError(f"manifest.json missing fields: {', '.join(missing)}")
        return cls(
            package_id=str(raw["package_id"]).strip(),
            slug=str(raw["slug"]).strip(),
            content_sha256=str(raw["content_sha256"]).strip().lower(),
            created_at=str(raw["created_at"]).strip(),
            producer=str(raw["producer"]).strip(),
        )


@dataclass
class PackageInspection:
    package_dir: Path
    manifest: DriveManifest
    article: Article
    computed_sha256: str
    errors: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def _reject_traversal(rel: str) -> str | None:
    parts = Path(rel).parts
    if ".." in parts or rel.startswith("/") or rel.startswith("\\"):
        return f"path traversal rejected: {rel}"
    return None


def scan_package_files(package_dir: Path) -> list[str]:
    errors: list[str] = []
    total = 0
    for path in package_dir.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(package_dir).as_posix()
        trav = _reject_traversal(rel)
        if trav:
            errors.append(trav)
            continue
        if any(part.startswith(".") for part in Path(rel).parts):
            continue
        suffix = path.suffix.lower()
        name = path.name.lower()
        if name in {"manifest.json", "checksums.sha256"}:
            continue
        if suffix and suffix not in ALLOWED_SUFFIXES and name not in {
            "article.yaml",
            "article.yml",
            "body.md",
        }:
            errors.append(f"disallowed file type: {rel}")
        if suffix == ".svg":
            errors.append(f"SVG not accepted via Drive intake (v1 raster-only): {rel}")
        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            errors.append(f"file exceeds {MAX_FILE_BYTES} bytes: {rel}")
        total += size
    if total > MAX_PACKAGE_BYTES:
        errors.append(f"package exceeds {MAX_PACKAGE_BYTES} bytes")
    return errors


def _load_yaml_meta(package_dir: Path) -> dict[str, Any]:
    for name in ("article.yaml", "article.yml"):
        path = package_dir / name
        if path.is_file():
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if not isinstance(data, dict):
                raise ValueError(f"{name} must be a YAML mapping")
            return data
    raise FileNotFoundError("missing article.yaml")


def stage_article_md(package_dir: Path, dest_dir: Path) -> Path:
    """Merge article.yaml + body.md into deterministic article.md + copy assets."""
    meta = _load_yaml_meta(package_dir)
    body_path = package_dir / "body.md"
    if not body_path.is_file():
        raise FileNotFoundError("missing body.md")
    body = body_path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    if body and not body.endswith("\n"):
        body += "\n"

    # Deterministic front matter dump
    fm = yaml.safe_dump(
        meta,
        sort_keys=True,
        default_flow_style=False,
        allow_unicode=True,
        width=1000,
    )
    article_md = f"---\n{fm}---\n{body}"

    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    (dest_dir / "article.md").write_text(article_md, encoding="utf-8")

    assets_src = package_dir / "assets"
    if assets_src.is_dir():
        dest_assets = dest_dir / "assets"
        shutil.copytree(assets_src, dest_assets)
        # Reject SVG that slipped through
        for p in dest_assets.rglob("*"):
            if p.is_file() and p.suffix.lower() == ".svg":
                raise ValueError(f"SVG not accepted via Drive intake: {p.name}")

    # Remap asset paths in front matter if authors used bare filenames
    return dest_dir / "article.md"


def inspect_drive_package(package_dir: Path) -> PackageInspection:
    package_dir = Path(package_dir)
    errors: list[str] = []
    warnings: list[str] = []
    manifest: DriveManifest | None = None
    article: Article | None = None
    computed = ""

    try:
        manifest = DriveManifest.load(package_dir / "manifest.json")
    except Exception as exc:  # noqa: BLE001 — surface as package error
        errors.append(f"manifest.json: {exc}")
        return PackageInspection(package_dir, DriveManifest("", "", "", "", ""), Article(
            title="", deck="", slug="", topic="", content_type="", status="draft",
            datePublished="", dateModified="", schema_type="",
        ), "", errors, warnings)

    if not SLUG_RE.match(manifest.slug):
        errors.append(f"invalid slug in manifest: {manifest.slug!r}")
    if package_dir.name != manifest.slug:
        errors.append(
            f"folder name {package_dir.name!r} must match manifest.slug {manifest.slug!r}"
        )

    errors.extend(scan_package_files(package_dir))
    errors.extend(verify_checksums(package_dir))

    try:
        computed = content_sha256(package_dir)
        if manifest.content_sha256 and manifest.content_sha256 != computed:
            errors.append(
                f"manifest content_sha256 mismatch "
                f"(declared {manifest.content_sha256}, computed {computed})"
            )
    except Exception as exc:  # noqa: BLE001
        errors.append(f"content hash failed: {exc}")

    # Stage to a temp sibling for v4 load/validate
    tmp = package_dir / ".staged_validate"
    try:
        if not errors:
            stage_article_md(package_dir, tmp)
            article = load_article(tmp)
            if article.slug != manifest.slug:
                errors.append(
                    f"article slug {article.slug!r} must match manifest.slug {manifest.slug!r}"
                )
            if article.status == "fixture":
                errors.append("status=fixture is not allowed via Drive intake")
            if QUARANTINE_RETIREMENT_PACKAGES and article.status == "retired":
                errors.append(
                    "status=retired quarantined until soft-retire implementation is complete"
                )
            # Raster requirement for published/retired imagery fields
            for field, val in (
                ("social_image", article.social_image),
                ("hero_image", article.hero_image),
            ):
                if not val:
                    continue
                suffix = Path(str(val)).suffix.lower()
                if suffix == ".svg":
                    errors.append(f"{field} must be raster for Drive intake, got SVG")
                elif suffix and suffix not in RASTER_SUFFIXES:
                    errors.append(f"{field} has unsupported extension {suffix}")
            v_errs = validate_articles([article])
            errors.extend(v_errs)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"v4 package staging/validation failed: {exc}")
    finally:
        if tmp.exists():
            shutil.rmtree(tmp, ignore_errors=True)

    if article is None:
        article = Article(
            title="",
            deck="",
            slug=manifest.slug,
            topic="",
            content_type="",
            status="draft",
            datePublished="",
            dateModified="",
            schema_type="",
        )

    return PackageInspection(
        package_dir=package_dir,
        manifest=manifest,
        article=article,
        computed_sha256=computed or manifest.content_sha256,
        errors=errors,
        warnings=warnings,
    )
