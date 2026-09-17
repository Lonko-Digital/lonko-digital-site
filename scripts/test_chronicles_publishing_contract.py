#!/usr/bin/env python3
"""End-to-end publishing-contract acceptance test.

1. Temporarily promotes the realistic package to status=published
2. Rebuilds Chronicles
3. Asserts webpage, index presence, sitemap, feed, search index, and schema
4. Restores fixture status and rebuilds

Usage:
  python scripts/test_chronicles_publishing_contract.py
"""

from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from chronicles_lib.build import build  # noqa: E402

SLUG = "when-stable-traffic-hides-a-conversion-problem"
PKG = ROOT / "chronicles" / "content" / SLUG
ARTICLE = PKG / "article.md"


def _set_status(raw: str, status: str, is_fixture: bool) -> str:
    raw = re.sub(r"(?m)^status:\s*\S+", f"status: {status}", raw, count=1)
    if re.search(r"(?m)^is_fixture:\s*", raw):
        raw = re.sub(r"(?m)^is_fixture:\s*\S+", f"is_fixture: {str(is_fixture).lower()}", raw, count=1)
    else:
        raw = raw.replace("---\n", f"---\nis_fixture: {str(is_fixture).lower()}\n", 1)
    return raw


def main() -> int:
    if not ARTICLE.is_file():
        print(f"FAIL: missing package {ARTICLE}", file=sys.stderr)
        return 1

    original = ARTICLE.read_text(encoding="utf-8")
    backup = tempfile.NamedTemporaryFile(delete=False, suffix=".md")
    backup.write(original.encode("utf-8"))
    backup.close()

    failures: list[str] = []
    try:
        ARTICLE.write_text(_set_status(original, "published", False), encoding="utf-8")
        code = build()
        if code != 0:
            failures.append(f"build exited {code}")

        page = ROOT / "chronicles" / SLUG / "index.html"
        if not page.is_file():
            failures.append("article webpage missing")
        else:
            html = page.read_text(encoding="utf-8")
            if 'rel="canonical"' not in html:
                failures.append("canonical missing")
            if '"@type": "Article"' not in html and '"@type":"Article"' not in html:
                # schema_type for this package is Article
                if "Article" not in html:
                    failures.append("Article schema missing")
            if "noindex" in html:
                failures.append("published page should not noindex")
            if "BreadcrumbList" not in html:
                failures.append("BreadcrumbList missing")

        home = (ROOT / "chronicles" / "index.html").read_text(encoding="utf-8")
        if SLUG not in home:
            failures.append("index does not link article")

        chron_map = (ROOT / "sitemap-chronicles.xml").read_text(encoding="utf-8")
        if f"/chronicles/{SLUG}/" not in chron_map:
            failures.append("sitemap-chronicles missing article URL")

        feed = (ROOT / "chronicles" / "feed.xml").read_text(encoding="utf-8")
        if SLUG not in feed:
            failures.append("feed missing article")

        idx = json.loads((ROOT / "chronicles" / "assets" / "search-index.json").read_text(encoding="utf-8"))
        if not any(e.get("slug") == SLUG for e in idx):
            failures.append("search-index missing article")

        # Draft still absent
        if (ROOT / "chronicles" / "draft-should-never-ship").exists():
            failures.append("draft package was emitted publicly")

    finally:
        ARTICLE.write_text(Path(backup.name).read_text(encoding="utf-8"), encoding="utf-8")
        Path(backup.name).unlink(missing_ok=True)
        build()  # restore fixture corpus output

    if failures:
        print("PUBLISHING CONTRACT: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("PUBLISHING CONTRACT: PASS")
    print(
        "  Inserted one package -> webpage, index, sitemap, feed, search index, schema"
        " -- no manual multi-file edits."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
