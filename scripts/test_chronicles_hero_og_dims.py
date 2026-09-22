#!/usr/bin/env python3
"""Verify hero/OG intrinsic dimensions are derived from current article assets."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from chronicles_lib.image_dims import read_image_size  # noqa: E402
from chronicles_lib.build import render_article_page  # noqa: E402
from chronicles_lib.model import load_all_articles, public_articles  # noqa: E402

CONTENT = ROOT / "chronicles" / "content"


def main() -> int:
    articles = load_all_articles(CONTENT)
    published = public_articles(articles)
    failures: list[str] = []

    for article in published:
        html = render_article_page(article, articles)

        if article.hero_image:
            hero_path = article.package_dir / article.hero_image
            hero_dims = read_image_size(hero_path)
            if not hero_dims:
                failures.append(f"{article.slug}: could not read hero intrinsic size")
            else:
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
                    got = (
                        (int(reverse.group(2)), int(reverse.group(1)))
                        if reverse
                        else None
                    )
                if got != hero_dims:
                    failures.append(
                        f"{article.slug}: hero img attrs {got} != asset {hero_dims}"
                    )

        if article.social_image:
            social_path = article.package_dir / article.social_image
            social_dims = read_image_size(social_path)
            if not social_dims:
                failures.append(f"{article.slug}: could not read social intrinsic size")
            else:
                ow = re.search(r'property="og:image:width" content="(\d+)"', html)
                oh = re.search(r'property="og:image:height" content="(\d+)"', html)
                if not ow or not oh:
                    failures.append(f"{article.slug}: missing og:image dimensions")
                elif (int(ow.group(1)), int(oh.group(1))) != social_dims:
                    failures.append(
                        f"{article.slug}: OG dims {(ow.group(1), oh.group(1))} "
                        f"!= social asset {social_dims}"
                    )

    if failures:
        print("HERO/OG DIMS: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("HERO/OG DIMS: PASS")
    if published:
        for article in published:
            hero = (
                read_image_size(article.package_dir / article.hero_image)
                if article.hero_image
                else None
            )
            social = (
                read_image_size(article.package_dir / article.social_image)
                if article.social_image
                else None
            )
            print(f"  {article.slug}: hero={hero} social/og={social}")
    else:
        print("  No published articles in current corpus; renderer contract unchanged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
