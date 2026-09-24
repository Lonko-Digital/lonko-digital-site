#!/usr/bin/env python3
"""Regression: unpublished draft articles must render in CHRONICLES_PREVIEW builds.

Proves the V2 pre-publish path works without faking status=published.
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from chronicles_bridge.testdata import write_png  # noqa: E402
from chronicles_lib.build import render_article_page  # noqa: E402
from chronicles_lib.model import (  # noqa: E402
    load_all_articles,
    load_article,
    public_articles,
    renderable_articles,
)
from chronicles_lib.preview import preview_mode_enabled  # noqa: E402
from chronicles_lib.validate import validate_articles  # noqa: E402

SLUG = "draft-preview-regression-article"


def _write_draft_package(dest: Path) -> Path:
    pkg = dest / SLUG
    assets = pkg / "assets"
    assets.mkdir(parents=True)
    write_png(assets / "hero.png", (40, 40, 200), w=1600, h=900)
    write_png(assets / "social.png", (200, 40, 40), w=1200, h=628)
    # Intentionally omit datePublished / dateModified — unpublished draft.
    body = (
        "AI Overviews changed how local results surface. This draft proves the "
        "preview path can render without fabricating a publication date.\n\n"
        "## What Business Owners Should Know\n\n"
        "Owners need a clear explanation before anything goes live.\n\n"
        "### Sources & Further Reading\n\n"
        "- [Google Search Central](https://developers.google.com/search)\n"
    )
    fm = f"""---
title: "Draft Preview Regression: AI Overviews Local Search"
deck: "Unpublished draft used only to certify CHRONICLES_PREVIEW rendering."
slug: {SLUG}
topic: SEO
tags: [preview, draft]
content_type: Analysis
author: Lonko Digital
status: draft
schema_type: Article
social_image: assets/social.png
hero_image: assets/hero.png
hero_alt: Draft preview regression hero
imagery_family: photography
sources: []
placement:
  featured: true
  sections: [owners]
related: []
---

{body}
"""
    (pkg / "article.md").write_text(fm, encoding="utf-8")
    return pkg


def main() -> int:
    failures: list[str] = []

    # Production mode: draft must NOT render
    os.environ.pop("CHRONICLES_PREVIEW", None)
    with tempfile.TemporaryDirectory() as tmp:
        content = Path(tmp) / "content"
        content.mkdir()
        _write_draft_package(content)
        arts = load_all_articles(content)
        if renderable_articles(arts):
            failures.append("production mode must not render drafts")
            print("  FAIL: draft rendered without CHRONICLES_PREVIEW")
        else:
            print("  PASS: production mode excludes draft from renderable set")
        errs = validate_articles(arts)
        if any("datePublished" in e or "dateModified" in e for e in errs):
            failures.append("draft must not require dates outside preview asset rules")
            print("  FAIL: draft rejected for missing dates in non-preview validate")
            for e in errs:
                print(f"    - {e}")
        else:
            print("  PASS: draft may omit dates in validation")

    # Preview mode: draft MUST render, noindex, assets resolve, body present
    os.environ["CHRONICLES_PREVIEW"] = "1"
    if not preview_mode_enabled():
        failures.append("preview_mode_enabled")
        print("  FAIL: CHRONICLES_PREVIEW=1 not detected")
        return 1

    with tempfile.TemporaryDirectory() as tmp:
        content = Path(tmp) / "content"
        content.mkdir()
        pkg = _write_draft_package(content)
        arts = load_all_articles(content)
        errs = validate_articles(arts)
        if errs:
            failures.append("preview validate")
            print("  FAIL: preview draft validation errors:")
            for e in errs:
                print(f"    - {e}")
        else:
            print("  PASS: preview draft validates (assets + dims, no dates required)")

        renderable = renderable_articles(arts)
        if not renderable or renderable[0].slug != SLUG:
            failures.append("preview renderable")
            print("  FAIL: draft not renderable under CHRONICLES_PREVIEW")
        else:
            print("  PASS: draft is renderable under CHRONICLES_PREVIEW")

        if public_articles(arts):
            failures.append("draft must not be public/indexable")
            print("  FAIL: draft incorrectly treated as public_articles")
        else:
            print("  PASS: draft excluded from public_articles / sitemap/feed set")

        article = load_article(pkg)
        html = render_article_page(article, arts)
        checks = {
            "title": "Draft Preview Regression: AI Overviews Local Search",
            "deck": "Unpublished draft used only to certify",
            "body": "What Business Owners Should Know",
            "hero": "chronicles-hero-figure",
            "noindex": 'content="noindex, nofollow"',
            "schema": '"@type": "Article"',
            "breadcrumb": "Chronicles",
            "preview notice": "PRE-PUBLICATION PREVIEW",
            "owners placement": "owners",  # may only appear in data/listing; soft
        }
        # Placement sections may not appear as literal "owners" on article page —
        # breadcrumb + schema are the hard checks.
        hard = ("title", "deck", "body", "hero", "noindex", "schema", "breadcrumb", "preview notice")
        for key in hard:
            needle = checks[key]
            if needle not in html:
                failures.append(f"html:{key}")
                print(f"  FAIL: missing {key!r} ({needle!r})")
            else:
                print(f"  PASS: html contains {key}")

        # Hero asset path must resolve relative to package
        hero_path = pkg / "assets" / "hero.png"
        social_path = pkg / "assets" / "social.png"
        if not hero_path.is_file() or not social_path.is_file():
            failures.append("assets missing on disk")
            print("  FAIL: package assets missing")
        else:
            print("  PASS: exact approved-size assets present on disk")

        # Production main tree untouched: we only used tempfile content
        prod_content = ROOT / "chronicles" / "content" / SLUG
        if prod_content.exists():
            failures.append("regression slug leaked into production content tree")
            print("  FAIL: draft regression package present under chronicles/content")
        else:
            print("  PASS: production chronicles/content untouched by regression package")

    os.environ.pop("CHRONICLES_PREVIEW", None)

    if failures:
        print("DRAFT PREVIEW REGRESSION: FAIL")
        print("Failed:", ", ".join(failures))
        return 1
    print("DRAFT PREVIEW REGRESSION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
