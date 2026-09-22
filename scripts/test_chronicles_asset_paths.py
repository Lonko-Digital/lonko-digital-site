#!/usr/bin/env python3
"""Technical asset-path validation for Chronicles packages.

Validates the current content corpus and proves missing/traversal media paths
fail closed without depending on a hard-coded fixture article.
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

CONTENT_ROOT = ROOT / "chronicles" / "content"


def main() -> int:
    failures: list[str] = []
    corpus = load_all_articles(CONTENT_ROOT)
    errs = validate_articles(corpus)
    if errs:
        failures.append(f"current corpus unexpectedly invalid: {errs[:5]}")

    candidates = [a for a in corpus if a.package_dir and (a.hero_image or a.social_image)]
    if candidates:
        article = candidates[0]
        with tempfile.TemporaryDirectory() as tmp:
            broken = Path(tmp) / article.slug
            shutil.copytree(article.package_dir, broken)
            raw = (broken / "article.md").read_text(encoding="utf-8")

            field = "social_image" if article.social_image else "hero_image"
            current = article.social_image if article.social_image else article.hero_image
            assert current

            missing = raw.replace(
                f"{field}: {current}",
                f"{field}: missing-publication-asset.png",
                1,
            )
            (broken / "article.md").write_text(missing, encoding="utf-8")
            bad = load_article(broken)
            bad.related = []
            bad_errs = validate_articles([bad])
            if not any(f"{field} file not found" in e for e in bad_errs):
                failures.append(
                    f"expected missing {field} path error, got: {bad_errs}"
                )

            traversal = missing.replace(
                f"{field}: missing-publication-asset.png",
                f"{field}: ../outside.png",
                1,
            )
            (broken / "article.md").write_text(traversal, encoding="utf-8")
            trav = load_article(broken)
            trav.related = []
            trav_errs = validate_articles([trav])
            if not any(f"{field} path" in e for e in trav_errs):
                failures.append(
                    f"expected traversal rejection for {field}, got: {trav_errs}"
                )

    if failures:
        print("ASSET PATH VALIDATION: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("ASSET PATH VALIDATION: PASS")
    print(f"  Corpus root: {CONTENT_ROOT}")
    print("  Current paths resolve; missing/traversal paths fail closed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
