#!/usr/bin/env python3
"""Smoke test: Chronicles GA4/dataLayer foundation is wired into article pages."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from chronicles_lib.build import CHRONICLES_JS, render_article_page, write_chronicles_js  # noqa: E402
from chronicles_lib.model import Article  # noqa: E402

REQUIRED_EVENTS = (
    "chronicles_scroll_depth",
    "chronicles_share",
    "chronicles_outbound_source_click",
    "chronicles_internal_link_click",
    "chronicles_to_site_nav",
)


def main() -> int:
    failures: list[str] = []

    for name in REQUIRED_EVENTS:
        if name not in CHRONICLES_JS:
            failures.append(f"CHRONICLES_JS missing event name: {name}")

    if "dataLayer" not in CHRONICLES_JS:
        failures.append("CHRONICLES_JS missing dataLayer push helper")
    if "initChroniclesMeasure" not in CHRONICLES_JS:
        failures.append("CHRONICLES_JS missing initChroniclesMeasure")

    article = Article(
        title="GA4 Foundation Test",
        deck="Synthetic renderer-level measurement test.",
        slug="ga4-foundation-synthetic",
        topic="Marketing",
        content_type="News",
        status="published",
        datePublished="2026-09-22",
        dateModified="2026-09-22",
        schema_type="NewsArticle",
        author="Lonko Digital",
        body=(
            "Body.\n\n"
            "### Sources & Further Reading\n\n"
            "- [Source](https://example.com/source)"
        ),
    )
    rendered = render_article_page(article, [article])

    if 'data-chronicles-page="article"' not in rendered:
        failures.append("article HTML missing data-chronicles-page=article")
    if f'data-article-slug="{article.slug}"' not in rendered:
        failures.append("article HTML missing data-article-slug")
    if 'data-share-method="copy"' not in rendered:
        failures.append("share controls missing data-share-method")
    if "chronicles.js" not in rendered:
        failures.append("article HTML does not load chronicles.js")
    if 'data-chronicles-outbound="source"' not in rendered:
        failures.append("authored source links missing outbound-source tracking hook")

    write_chronicles_js()
    emitted = ROOT / "chronicles" / "assets" / "chronicles.js"
    if not emitted.is_file():
        failures.append("chronicles/assets/chronicles.js was not written")
    else:
        body = emitted.read_text(encoding="utf-8")
        for name in REQUIRED_EVENTS:
            if name not in body:
                failures.append(f"emitted chronicles.js missing {name}")

    if failures:
        print("CHRONICLES GA4 FOUNDATION: FAIL")
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print("CHRONICLES GA4 FOUNDATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
