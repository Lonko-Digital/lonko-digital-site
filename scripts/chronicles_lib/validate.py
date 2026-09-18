"""Build-time validation for Lonko Chronicles articles."""

from __future__ import annotations

import re
from datetime import date

from .model import (
    CONTENT_TYPES,
    IMAGERY_FAMILIES,
    PLACEMENT_SECTIONS,
    SCHEMA_TYPES,
    STATUSES,
    Article,
)

ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Published articles require an explicit social_image.
# Fixtures may fall back to site-wide assets/images/og-share.png (documented fallback).
SITE_OG_FALLBACK = "assets/images/og-share.png"


def validate_articles(articles: list[Article], *, forbid_drafts: bool = False) -> list[str]:
    """Return a list of error strings that must fail the build. Empty = ok.

    When forbid_drafts is True (public output set), any draft is an error.
    Drafts are otherwise validated lightly so authoring packages can be checked
    without requiring full social/hero readiness.
    """
    errors: list[str] = []
    seen_slugs: dict[str, str] = {}
    slug_set = {a.slug for a in articles if a.slug}

    for article in articles:
        label = article.slug or "(missing-slug)"
        prefix = f"{label}: "

        if forbid_drafts and article.status == "draft":
            errors.append(f"{prefix}draft must not appear in public output")

        # Duplicate slugs
        if article.slug:
            if article.slug in seen_slugs:
                errors.append(
                    f"{prefix}duplicate slug (also in {seen_slugs[article.slug]})"
                )
            else:
                seen_slugs[article.slug] = label
        else:
            errors.append(f"{prefix}missing required field: slug")

        # Required metadata
        for field_name, value in (
            ("title", article.title),
            ("deck", article.deck),
            ("topic", article.topic),
            ("content_type", article.content_type),
            ("author", article.author),
            ("status", article.status),
            ("datePublished", article.datePublished),
            ("dateModified", article.dateModified),
            ("schema_type", article.schema_type),
        ):
            if not value:
                errors.append(f"{prefix}missing required field: {field_name}")

        # Enums
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

        # Dates
        for field_name, value in (
            ("datePublished", article.datePublished),
            ("dateModified", article.dateModified),
        ):
            if value and not _valid_iso_date(value):
                errors.append(f"{prefix}invalid {field_name} '{value}' (expected YYYY-MM-DD)")

        # Featured must be explicit bool or int (bool is a subclass of int — use type())
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

        is_publicish = article.status in {"published", "fixture", "retired"} or article.is_fixture

        # Hero alt required when published/fixture/retired with a hero image
        if is_publicish and article.hero_image and not article.hero_alt:
            errors.append(f"{prefix}published/fixture missing hero_alt")

        # Social metadata
        # Published + retired: require social_image (page remains at canonical URL).
        # Fixture: allow fallback to site og-share.png when social_image is absent.
        if article.status in {"published", "retired"} and not article.is_fixture:
            if not article.social_image:
                errors.append(
                    f"{prefix}{article.status} article missing social_image "
                    f"(fixtures may fall back to {SITE_OG_FALLBACK})"
                )
        elif is_publicish and not article.social_image:
            # Fixture path: fallback allowed — no error, documented above.
            pass

        # Sources
        for i, src in enumerate(article.sources):
            url = (src or {}).get("url", "")
            desc = (src or {}).get("description", "")
            if not url or not desc:
                errors.append(
                    f"{prefix}malformed sources[{i}] (must have url and description)"
                )

        # Related slug references
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
