#!/usr/bin/env python3
"""Verify hero/OG intrinsic dimensions are derived from assets (not hard-coded)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from chronicles_lib.image_dims import read_image_size  # noqa: E402
from chronicles_lib.build import render_article_page  # noqa: E402
from chronicles_lib.model import load_all_articles  # noqa: E402


def main() -> int:
    content = ROOT / "chronicles" / "_local_fixtures"
    if not content.is_dir():
        print("FAIL: missing local fixtures; run seed_chronicles_fixtures.py", file=sys.stderr)
        return 1

    articles = load_all_articles(content)
    by_slug = {a.slug: a for a in articles}
    slug = "when-stable-traffic-hides-a-conversion-problem"
    article = by_slug.get(slug)
    if not article:
        print(f"FAIL: missing fixture {slug}", file=sys.stderr)
        return 1

    failures: list[str] = []
    hero_path = article.package_dir / article.hero_image  # type: ignore[operator]
    social_path = article.package_dir / article.social_image  # type: ignore[operator]
    hero_dims = read_image_size(hero_path)
    social_dims = read_image_size(social_path)
    if not hero_dims:
        failures.append("could not read hero intrinsic size")
    if not social_dims:
        failures.append("could not read social intrinsic size")
    if hero_dims and social_dims and hero_dims == (1200, 630) and social_dims == (1200, 630):
        # Fixture should demonstrate separation — hero is 16:9 SVG, social is 1200x630 PNG
        failures.append("fixture hero unexpectedly matches social 1200x630 (test setup broken)")

    html = render_article_page(article, articles)
    hm = re.search(
        r'chronicles-hero-figure[\s\S]*?<img[^>]*\swidth="(\d+)"[^>]*\sheight="(\d+)"',
        html,
    )
    if not hm:
        # also allow height before width
        hm = re.search(
            r'chronicles-hero-figure[\s\S]*?<img[^>]*\sheight="(\d+)"[^>]*\swidth="(\d+)"',
            html,
        )
        if hm and hero_dims:
            got = (int(hm.group(2)), int(hm.group(1)))
        else:
            got = None
    else:
        got = (int(hm.group(1)), int(hm.group(2)))

    if hero_dims and got != hero_dims:
        failures.append(f"hero img attrs {got} != asset {hero_dims}")

    # Must not hard-code social ratio onto a non-matching hero
    if hero_dims and hero_dims != (1200, 630) and got == (1200, 630):
        failures.append("hero still hard-coded to 1200x630")

    ow = re.search(r'property="og:image:width" content="(\d+)"', html)
    oh = re.search(r'property="og:image:height" content="(\d+)"', html)
    if not ow or not oh:
        failures.append("missing og:image width/height metas")
    elif social_dims and (int(ow.group(1)), int(oh.group(1))) != social_dims:
        failures.append(
            f"og dims {(ow.group(1), oh.group(1))} != social asset {social_dims}"
        )

    if failures:
        print("HERO/OG DIMS: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("HERO/OG DIMS: PASS")
    print(f"  hero asset/attrs {hero_dims}")
    print(f"  social/og {social_dims}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
