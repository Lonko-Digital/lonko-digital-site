#!/usr/bin/env python3
"""End-to-end Chronicles publishing-contract acceptance test.

Validates the production authoring contract against the current corpus without
depending on a hard-coded editorial fixture. Also exercises renderer-level
contract details that must remain stable for future publication packages.

Usage:
  python scripts/test_chronicles_publishing_contract.py
"""

from __future__ import annotations

import html as html_lib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from chronicles_lib.build import build, render_article_page  # noqa: E402
from chronicles_lib.model import Article, load_all_articles, public_articles  # noqa: E402

ORG_ID = "https://lonkodigital.com/#organization"
CONTENT = ROOT / "chronicles" / "content"


def _renderer_contract_checks() -> list[str]:
    """Check renderer behavior with a synthetic in-memory article."""
    failures: list[str] = []
    article = Article(
        title="Display Headline",
        deck="Deck",
        slug="publishing-contract-synthetic",
        topic="Marketing",
        content_type="News",
        status="published",
        datePublished="2026-09-22",
        dateModified="2026-09-22",
        schema_type="NewsArticle",
        seo_title="Locked SEO Title",
        meta_description="Locked description",
        og_title="Locked OG title",
        og_description="Locked OG description",
        author="Lonko Digital",
        body=(
            "Body paragraph.\n\n"
            "### Sources & Further Reading\n\n"
            "- [Example source](https://example.com/source)"
        ),
    )
    rendered = render_article_page(article, [article])

    exact_title = f"<title>{html_lib.escape(article.seo_title, quote=True)}</title>"
    if exact_title not in rendered:
        failures.append("explicit seo_title is not emitted as the exact title tag")
    if "Locked SEO Title — Lonko Chronicles" in rendered:
        failures.append("publication suffix is still forced onto explicit seo_title")

    if f'"@id": "{ORG_ID}"' not in rendered:
        failures.append("canonical Organization @id is not referenced in article schema")
    if f'"publisher": {{\n    "@id": "{ORG_ID}"\n  }}' not in rendered:
        failures.append("publisher does not reuse canonical Organization @id")

    if 'id="sources-further-reading"' not in rendered:
        failures.append("authored Sources & Further Reading heading was not rendered")
    if 'data-chronicles-outbound="source"' not in rendered:
        failures.append("authored source links are missing GA4 source-click tracking hook")

    if "BreadcrumbList" not in rendered:
        failures.append("BreadcrumbList missing from rendered article")
    if '"name": "Chronicles"' not in rendered:
        failures.append("Chronicles breadcrumb missing")

    return failures


def _production_surface_checks() -> list[str]:
    failures: list[str] = []

    code = build()
    if code != 0:
        failures.append(f"build exited {code}")
        return failures

    corpus = load_all_articles(CONTENT)
    published = public_articles(corpus)

    # The contract test is allowed to run before the first production article
    # exists. Renderer-level checks above still verify the publication system.
    if not published:
        return failures

    index_html = (ROOT / "chronicles" / "index.html").read_text(encoding="utf-8")
    sitemap = (ROOT / "sitemap-chronicles.xml").read_text(encoding="utf-8")
    feed = (ROOT / "chronicles" / "feed.xml").read_text(encoding="utf-8")
    search_index = json.loads(
        (ROOT / "chronicles" / "assets" / "search-index.json").read_text(encoding="utf-8")
    )

    for article in published:
        page = ROOT / "chronicles" / article.slug / "index.html"
        if not page.is_file():
            failures.append(f"{article.slug}: article webpage missing")
            continue

        rendered = page.read_text(encoding="utf-8")
        canonical = f"https://lonkodigital.com/chronicles/{article.slug}/"

        if f'rel="canonical" href="{canonical}"' not in rendered:
            failures.append(f"{article.slug}: canonical missing or incorrect")
        if "noindex" in rendered:
            failures.append(f"{article.slug}: published page must not be noindex")
        if "BreadcrumbList" not in rendered:
            failures.append(f"{article.slug}: BreadcrumbList missing")
        if f'"@type": "{article.schema_type}"' not in rendered:
            failures.append(f"{article.slug}: {article.schema_type} schema missing")
        if f'"@id": "{ORG_ID}"' not in rendered:
            failures.append(f"{article.slug}: canonical Organization @id missing")

        if article.seo_title:
            exact_title = f"<title>{html_lib.escape(article.seo_title, quote=True)}</title>"
            if exact_title not in rendered:
                failures.append(f"{article.slug}: explicit seo_title not honored exactly")

        if 'id="sources-further-reading"' in rendered and (
            'data-chronicles-outbound="source"' not in rendered
        ):
            failures.append(f"{article.slug}: body sources lack outbound-source tracking")

        if article.slug not in index_html:
            failures.append(f"{article.slug}: index does not link article")
        if f"/chronicles/{article.slug}/" not in sitemap:
            failures.append(f"{article.slug}: sitemap-chronicles missing URL")
        if article.slug not in feed:
            failures.append(f"{article.slug}: feed missing article")
        if not any(item.get("slug") == article.slug for item in search_index):
            failures.append(f"{article.slug}: search-index missing article")

    # Draft packages must never emit a public canonical page.
    for article in corpus:
        if article.status != "draft":
            continue
        if (ROOT / "chronicles" / article.slug / "index.html").exists():
            failures.append(f"{article.slug}: draft package emitted publicly")

    return failures


def main() -> int:
    failures = _renderer_contract_checks()
    failures.extend(_production_surface_checks())

    if failures:
        print("PUBLISHING CONTRACT: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("PUBLISHING CONTRACT: PASS")
    print(
        "  Renderer metadata/schema/tracking contract and all current published "
        "surfaces validated."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
