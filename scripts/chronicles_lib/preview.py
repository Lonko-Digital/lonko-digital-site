"""Preview-mode helpers for unpublished draft articles (Production System v2).

Production builds leave CHRONICLES_PREVIEW unset: drafts are not rendered.
Preview builds set CHRONICLES_PREVIEW=1 so drafts render with noindex and an
in-memory date overlay that never writes publication dates into package files.
"""

from __future__ import annotations

import os
from dataclasses import replace
from datetime import date

from chronicles_lib.model import Article


def preview_mode_enabled() -> bool:
    return os.environ.get("CHRONICLES_PREVIEW", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def apply_preview_date_overlay(article: Article) -> Article:
    """Fill missing draft dates for render/schema only. Does not mutate packages."""
    if article.status != "draft":
        return article
    today = date.today().isoformat()
    pub = (article.datePublished or "").strip() or today
    mod = (article.dateModified or "").strip() or pub
    if pub == article.datePublished and mod == article.dateModified:
        return article
    return replace(article, datePublished=pub, dateModified=mod)
