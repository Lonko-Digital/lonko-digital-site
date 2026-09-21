#!/usr/bin/env python3
"""Smoke test: Chronicles GA4/dataLayer foundation is wired into article pages."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from chronicles_lib.build import CHRONICLES_JS, render_article_page, write_chronicles_js  # noqa: E402
from chronicles_lib.model import load_all_articles  # noqa: E402

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

    content = ROOT / "chronicles" / "_local_fixtures"
    if not content.is_dir():
        failures.append("missing chronicles/_local_fixtures")
        print("CHRONICLES GA4 FOUNDATION: FAIL")
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    articles = load_all_articles(content)
    by_slug = {a.slug: a for a in articles}
    slug = "when-stable-traffic-hides-a-conversion-problem"
    article = by_slug.get(slug)
    if not article:
        failures.append(f"missing fixture {slug}")
    else:
        html = render_article_page(article, articles)
        if 'data-chronicles-page="article"' not in html:
            failures.append("article HTML missing data-chronicles-page=article")
        if f'data-article-slug="{slug}"' not in html:
            failures.append("article HTML missing data-article-slug")
        if 'data-share-method="copy"' not in html:
            failures.append("share controls missing data-share-method")
        if "chronicles.js" not in html:
            failures.append("article HTML does not load chronicles.js")
        if article.sources and 'data-chronicles-outbound="source"' not in html:
            failures.append("sources links missing data-chronicles-outbound=source")

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
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("CHRONICLES GA4 FOUNDATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
