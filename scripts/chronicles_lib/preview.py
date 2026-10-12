"""Preview-mode helpers for unpublished draft articles (Production System v2).

Production builds leave CHRONICLES_PREVIEW unset: drafts are not rendered.
Preview builds set CHRONICLES_PREVIEW=1 so drafts render with noindex and an
unset publication dates until approval. Preview rendering never fabricates dates.
"""

from __future__ import annotations

import os

from chronicles_lib.model import Article


def preview_mode_enabled() -> bool:
    return os.environ.get("CHRONICLES_PREVIEW", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def apply_preview_date_overlay(article: Article) -> Article:
    """Compatibility hook: preserve authored dates, including missing draft dates."""
    return article
