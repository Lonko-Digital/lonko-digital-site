#!/usr/bin/env python3
"""Verify hero/OG dimensions match production contract for published articles."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from chronicles_lib.image_dims import read_image_size  # noqa: E402
from chronicles_lib.build import render_article_page  # noqa: E402
from chronicles_lib.model import load_all_articles, public_articles  # noqa: E402
from chronicles_lib.validate import HERO_DIMS, SOCIAL_DIMS  # noqa: E402

CONTENT = ROOT / "chronicles" / "content"


def main() -> int:
    articles = load_all_articles(CONTENT)
    published = public_articles(articles)
    failures: list[str] = []

    if not published:
        print("HERO/OG DIMS: FAIL")
        print("  - no published articles; production-contract mode cannot soft-pass")
        return 1

    for article in published:
        if not article.hero_image:
            failures.append(f"{article.slug}: missing hero_image")
            continue
        if not article.social_image:
            failures.append(f"{article.slug}: missing social_image")
            continue

        html = render_article_page(article, articles)
        hero_path = article.package_dir / article.hero_image
        social_path = article.package_dir / article.social_image
        hero_dims = read_image_size(hero_path)
        social_dims = read_image_size(social_path)

        if hero_dims != HERO_DIMS:
            failures.append(
                f"{article.slug}: hero asset {hero_dims} != required {HERO_DIMS}"
            )
        if social_dims != SOCIAL_DIMS:
            failures.append(
                f"{article.slug}: social asset {social_dims} != required {SOCIAL_DIMS}"
            )

        match = re.search(
            r'chronicles-hero-figure[\s\S]*?<img[^>]*\swidth="(\d+)"[^>]*\sheight="(\d+)"',
            html,
        )
        if match:
            got = (int(match.group(1)), int(match.group(2)))
        else:
            reverse = re.search(
                r'chronicles-hero-figure[\s\S]*?<img[^>]*\sheight="(\d+)"[^>]*\swidth="(\d+)"',
                html,
            )
            got = (int(reverse.group(2)), int(reverse.group(1))) if reverse else None
        if got != hero_dims:
            failures.append(f"{article.slug}: hero img attrs {got} != asset {hero_dims}")

        ow = re.search(r'property="og:image:width" content="(\d+)"', html)
        oh = re.search(r'property="og:image:height" content="(\d+)"', html)
        if not ow or not oh:
            failures.append(f"{article.slug}: missing og:image dimensions")
        elif (int(ow.group(1)), int(oh.group(1))) != social_dims:
            failures.append(
                f"{article.slug}: OG dims {(ow.group(1), oh.group(1))} != social {social_dims}"
            )

    if failures:
        print("HERO/OG DIMS: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("HERO/OG DIMS: PASS")
    for article in published:
        print(
            f"  {article.slug}: hero={HERO_DIMS} social/og={SOCIAL_DIMS}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
