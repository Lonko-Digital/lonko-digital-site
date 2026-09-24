"""Build-time validation for Lonko Chronicles articles.

Contract: docs/chronicles/chronicles-article-contract.yaml (workflow_version 2).
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from .image_dims import read_image_size
from .model import (
    CONTENT_TYPES,
    IMAGERY_FAMILIES,
    PLACEMENT_SECTIONS,
    SCHEMA_TYPES,
    STATUSES,
    Article,
)

ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# Published articles require an explicit social_image.
# Fixtures may fall back to site-wide assets/images/og-share.png (documented fallback).
SITE_OG_FALLBACK = "assets/images/og-share.png"

HERO_DIMS = (1600, 900)
SOCIAL_DIMS = (1200, 628)

# Fail-closed editorial hygiene — reject, do not silently rewrite body copy.
_BODY_LINT_RULES: list[tuple[str, re.Pattern[str]]] = [
    (
        "word-count annotation",
        re.compile(
            r"(?im)^\s*(?:\*|_){0,2}\(\s*~\s*[\d,]+\s*words?\s*\)(?:\*|_){0,2}\s*$"
            r"|<p>\s*(?:<em>)?\s*\(\s*~\s*[\d,]+\s*words?\s*\)\s*(?:</em>)?\s*</p>",
        ),
    ),
    (
        "WORKING NOTE / INTERNAL NOTE marker",
        re.compile(r"(?i)\b(?:WORKING\s+NOTE|INTERNAL\s+NOTE)\b"),
    ),
    (
        "standalone TODO/FIXME editor marker",
        re.compile(r"(?m)^\s*(?:TODO|FIXME)\b[:\s-]"),
    ),
    (
        "draft-history / production-note marker",
        re.compile(
            r"(?i)\b(?:DRAFT\s+ONLY|DO\s+NOT\s+PUBLISH|PRODUCTION\s+NOTE|"
            r"EDITORIAL\s+ONLY|REMOVE\s+BEFORE\s+PUBLISH)\b"
        ),
    ),
]

_SOURCES_HEADING_RE = re.compile(
    r"(?im)^\s{0,3}#{2,6}\s+Sources(?:\s*&\s*Further\s+Reading)?\s*$"
    r"|^\s{0,3}#{2,6}\s+Sources\s+and\s+Further\s+Reading\s*$"
)


def validate_articles(
    articles: list[Article],
    *,
    forbid_drafts: bool = False,
    enforce_production_assets: bool | None = None,
) -> list[str]:
    """Return a list of error strings that must fail the build. Empty = ok.

    When forbid_drafts is True (public output set), any draft is an error.
    When enforce_production_assets is True (default for published/retired),
    require hero+social and exact pixel dimensions. Fixtures never enforce
    production dimensions.
    """
    errors: list[str] = []
    seen_slugs: dict[str, str] = {}
    slug_set = {a.slug for a in articles if a.slug}

    for article in articles:
        label = article.slug or "(missing-slug)"
        prefix = f"{label}: "

        if forbid_drafts and article.status == "draft":
            errors.append(f"{prefix}draft must not appear in public output")

        if article.slug:
            if article.slug in seen_slugs:
                errors.append(
                    f"{prefix}duplicate slug (also in {seen_slugs[article.slug]})"
                )
            else:
                seen_slugs[article.slug] = label
            if not SLUG_RE.match(article.slug):
                errors.append(
                    f"{prefix}invalid slug '{article.slug}' "
                    f"(expected lowercase kebab-case)"
                )
        else:
            errors.append(f"{prefix}missing required field: slug")

        for field_name, value in (
            ("title", article.title),
            ("deck", article.deck),
            ("topic", article.topic),
            ("content_type", article.content_type),
            ("author", article.author),
            ("status", article.status),
            ("schema_type", article.schema_type),
        ):
            if not value:
                errors.append(f"{prefix}missing required field: {field_name}")

        # Published/retired require real dates. Drafts may omit them until
        # APPROVED FOR PUBLICATION; preview builds apply an in-memory overlay.
        if article.status != "draft":
            for field_name, value in (
                ("datePublished", article.datePublished),
                ("dateModified", article.dateModified),
            ):
                if not value:
                    errors.append(f"{prefix}missing required field: {field_name}")

        if article.content_type and article.content_type not in CONTENT_TYPES:
            errors.append(
                f"{prefix}invalid content_type '{article.content_type}' "
                f"(expected {sorted(CONTENT_TYPES)})"
            )
        if article.status and article.status not in STATUSES:
            errors.append(
                f"{prefix}invalid status '{article.status}' "
                f"(expected {sorted(STATUSES)})"
            )
        if article.schema_type and article.schema_type not in SCHEMA_TYPES:
            errors.append(
                f"{prefix}invalid schema_type '{article.schema_type}' "
                f"(expected {sorted(SCHEMA_TYPES)})"
            )
        if article.imagery_family and article.imagery_family not in IMAGERY_FAMILIES:
            errors.append(
                f"{prefix}invalid imagery_family '{article.imagery_family}' "
                f"(expected {sorted(IMAGERY_FAMILIES)})"
            )

        for field_name, value in (
            ("datePublished", article.datePublished),
            ("dateModified", article.dateModified),
        ):
            if value and not _valid_iso_date(value):
                errors.append(f"{prefix}invalid {field_name} '{value}' (expected YYYY-MM-DD)")

        featured = article.placement.get("featured", False)
        if type(featured) not in (bool, int):
            errors.append(
                f"{prefix}placement.featured must be bool or int, got {type(featured).__name__}"
            )

        for section in article.sections:
            if section not in PLACEMENT_SECTIONS:
                errors.append(
                    f"{prefix}invalid placement.sections entry '{section}' "
                    f"(expected {sorted(PLACEMENT_SECTIONS)})"
                )

        is_production = (
            article.status in {"published", "retired"} and not article.is_fixture
        )
        from chronicles_lib.preview import preview_mode_enabled

        is_preview_draft = article.status == "draft" and preview_mode_enabled()
        enforce_assets = (
            enforce_production_assets
            if enforce_production_assets is not None
            else (is_production or is_preview_draft)
        )

        # Body hygiene — fail closed (no silent rewrite)
        for rule_name, pattern in _BODY_LINT_RULES:
            if pattern.search(article.body or ""):
                errors.append(
                    f"{prefix}body contains non-public editorial artifact "
                    f"({rule_name}); remove it from the package"
                )

        # Duplicate Sources presentation
        body_has_sources = bool(_SOURCES_HEADING_RE.search(article.body or ""))
        if article.sources and body_has_sources:
            errors.append(
                f"{prefix}duplicate Sources presentation: front-matter sources "
                f"is non-empty AND body already contains a Sources heading — "
                f"use exactly one form"
            )

        # Source URL uniqueness + shape
        seen_urls: set[str] = set()
        for i, src in enumerate(article.sources):
            url = (src or {}).get("url", "")
            desc = (src or {}).get("description", "")
            if not url or not desc:
                errors.append(
                    f"{prefix}malformed sources[{i}] (must have url and description)"
                )
                continue
            if not (url.startswith("http://") or url.startswith("https://")):
                errors.append(
                    f"{prefix}sources[{i}] url must be absolute http(s): {url!r}"
                )
            key = url.strip().rstrip("/")
            if key in seen_urls:
                errors.append(f"{prefix}duplicate sources url: {url!r}")
            seen_urls.add(key)

        if is_production or is_preview_draft or (enforce_assets and article.status != "draft"):
            if not article.hero_image:
                errors.append(
                    f"{prefix}{'preview draft' if is_preview_draft else 'published/retired'} "
                    f"article missing hero_image"
                )
            if not article.social_image:
                errors.append(
                    f"{prefix}{article.status} article missing social_image "
                    f"(fixtures may fall back to {SITE_OG_FALLBACK})"
                )
            if article.hero_image and not article.hero_alt:
                errors.append(
                    f"{prefix}{'preview draft' if is_preview_draft else 'published/retired'} "
                    f"missing hero_alt"
                )

        if article.package_dir is not None:
            for field_name, rel in (
                ("hero_image", article.hero_image),
                ("social_image", article.social_image),
            ):
                err = _missing_package_asset(article.package_dir, rel, field_name)
                if err:
                    errors.append(f"{prefix}{err}")
                    continue
                if not rel or not enforce_assets or article.is_fixture:
                    continue
                path = (Path(article.package_dir) / Path(rel)).resolve()
                dims = read_image_size(path)
                if dims is None:
                    errors.append(
                        f"{prefix}{field_name} dimensions unreadable: {rel!r}"
                    )
                    continue
                expected = HERO_DIMS if field_name == "hero_image" else SOCIAL_DIMS
                if dims != expected:
                    errors.append(
                        f"{prefix}{field_name} must be exactly "
                        f"{expected[0]}×{expected[1]}px, got {dims[0]}×{dims[1]} "
                        f"({rel!r})"
                    )

        for rel in article.related:
            if rel not in slug_set:
                errors.append(f"{prefix}broken related slug reference: '{rel}'")
            elif rel == article.slug:
                errors.append(f"{prefix}related slug must not reference itself")

    return errors


def _valid_iso_date(value: str) -> bool:
    if not ISO_DATE.match(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _missing_package_asset(
    package_dir: Path, rel: str | None, field_name: str
) -> str | None:
    """Return an error string if a relative package asset path is missing/unsafe."""
    if not rel:
        return None
    if "://" in rel or rel.startswith("/"):
        return None
    candidate = Path(rel)
    if candidate.is_absolute() or ".." in candidate.parts:
        return f"{field_name} path must be package-relative without '..': {rel!r}"
    path = (Path(package_dir) / candidate).resolve()
    try:
        path.relative_to(Path(package_dir).resolve())
    except ValueError:
        return f"{field_name} path escapes package directory: {rel!r}"
    if not path.is_file():
        return f"{field_name} file not found in package: {rel!r}"
    return None
