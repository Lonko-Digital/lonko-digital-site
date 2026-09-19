#!/usr/bin/env python3
"""Technical asset-path validation for Chronicles packages.

Covers fail-closed checks only (path exists, no traversal). Does not judge
creative quality, aspect ratio aesthetics, or editorial diversity.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from chronicles_lib.model import load_all_articles, load_article  # noqa: E402
from chronicles_lib.validate import validate_articles  # noqa: E402

SLUG = "when-stable-traffic-hides-a-conversion-problem"
# Prefer production content tree; fall back to local fixtures for CI/dev machines
# without seeded editorial packages.
_ROOT_CANDIDATES = (
    ROOT / "chronicles" / "content",
    ROOT / "chronicles" / "_local_fixtures",
)
CONTENT_ROOT = next((p for p in _ROOT_CANDIDATES if (p / SLUG).is_dir()), _ROOT_CANDIDATES[0])
PKG = CONTENT_ROOT / SLUG


def main() -> int:
    failures: list[str] = []

    if not PKG.is_dir():
        print(f"FAIL: missing package {PKG}", file=sys.stderr)
        return 1

    corpus = load_all_articles(CONTENT_ROOT)
    errs = validate_articles(corpus)
    if errs:
        failures.append(f"fixture corpus unexpectedly invalid: {errs[:5]}")

    with tempfile.TemporaryDirectory() as tmp:
        broken = Path(tmp) / SLUG
        shutil.copytree(PKG, broken)
        article = load_article(broken)
        # Point social_image at a non-existent file
        md = (broken / "article.md").read_text(encoding="utf-8")
        md = md.replace(
            f"social_image: {article.social_image}",
            "social_image: missing-social-banner.png",
            1,
        )
        (broken / "article.md").write_text(md, encoding="utf-8")
        bad = load_article(broken)
        # Keep related empty so this test isolates asset-path failures
        bad.related = []
        bad_errs = validate_articles([bad])
        if not any("social_image file not found" in e for e in bad_errs):
            failures.append(
                f"expected missing social_image path error, got: {bad_errs}"
            )

        # Traversal must fail closed
        md2 = (broken / "article.md").read_text(encoding="utf-8")
        md2 = md2.replace(
            "social_image: missing-social-banner.png",
            "social_image: ../outside.png",
            1,
        )
        (broken / "article.md").write_text(md2, encoding="utf-8")
        trav = load_article(broken)
        trav.related = []
        trav_errs = validate_articles([trav])
        if not any("social_image path" in e for e in trav_errs):
            failures.append(f"expected traversal rejection, got: {trav_errs}")

    if failures:
        print("ASSET PATH VALIDATION: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("ASSET PATH VALIDATION: PASS")
    print(f"  Corpus root: {CONTENT_ROOT}")
    print("  Existing package paths resolve; missing/traversal paths fail closed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
