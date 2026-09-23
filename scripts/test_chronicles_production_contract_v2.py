#!/usr/bin/env python3
"""Production-contract certification for Lonko Chronicles (workflow v2).

Fail closed. Soft-pass on empty published corpus is NOT allowed.
Covers validation failure simulations + presentation/surface assertions.
"""

from __future__ import annotations

import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from chronicles_bridge.testdata import write_png  # noqa: E402
from chronicles_lib.build import (  # noqa: E402
    CHRONICLES_JS,
    render_article_page,
    write_chronicles_js,
)
from chronicles_lib.model import load_all_articles, load_article, public_articles  # noqa: E402
from chronicles_lib.validate import HERO_DIMS, SOCIAL_DIMS, validate_articles  # noqa: E402

ORG_ID = "https://lonkodigital.com/#organization"
CSS = ROOT / "assets" / "css" / "site.css"


def _fail(msg: str) -> None:
    print(f"  FAIL: {msg}", file=sys.stderr)


def _ok(msg: str) -> None:
    print(f"  PASS: {msg}")


def _write_md_package(dest: Path, *, slug: str, body: str, **meta_overrides) -> Path:
    """Create a content-tree package (article.md) with production-sized assets."""
    pkg = dest / slug
    if pkg.exists():
        shutil.rmtree(pkg)
    assets = pkg / "assets"
    assets.mkdir(parents=True)
    write_png(assets / "hero.png", (40, 40, 200), w=1600, h=900)
    write_png(assets / "social.png", (200, 40, 40), w=1200, h=628)
    meta = {
        "title": "Contract Simulation Article",
        "deck": "Deck for contract simulation.",
        "slug": slug,
        "topic": "Marketing",
        "tags": ["contract"],
        "content_type": "Analysis",
        "author": "Lonko Digital",
        "status": "published",
        "datePublished": "2026-09-22",
        "dateModified": "2026-09-22",
        "schema_type": "Article",
        "social_image": "assets/social.png",
        "hero_image": "assets/hero.png",
        "hero_alt": "Contract simulation hero",
        "imagery_family": "photography",
        "sources": [],
        "placement": {"featured": False, "sections": ["owners"]},
        "related": [],
    }
    meta.update(meta_overrides)
    import yaml

    fm = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True)
    (pkg / "article.md").write_text(
        f"---\n{fm}---\n\n{body.rstrip()}\n",
        encoding="utf-8",
    )
    return pkg


def case_validate(name: str, mutate, expect_substr: str) -> bool:
    """Build a valid temp published package, mutate, expect validate error."""
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp)
        pkg = _write_md_package(
            dest,
            slug="contract-sim-article",
            body="Healthy body for contract simulation.\n",
        )
        mutate(pkg)
        article = load_article(pkg)
        errs = validate_articles([article])
        joined = " | ".join(errs)
        if not errs:
            _fail(f"{name}: expected validation failure, got clean")
            return False
        if expect_substr.lower() not in joined.lower():
            _fail(f"{name}: expected error containing {expect_substr!r}, got: {errs}")
            return False
        _ok(f"{name}: {expect_substr}")
        return True


def run_failure_simulations() -> list[str]:
    failures: list[str] = []

    def miss_hero(pkg: Path) -> None:
        md = (pkg / "article.md").read_text(encoding="utf-8")
        md = re.sub(r"^hero_image:.*$", "hero_image:", md, flags=re.M)
        # clearer: remove hero
        md = re.sub(r"^hero_image:.*\n", "", md, flags=re.M)
        md = re.sub(r"^hero_alt:.*\n", "", md, flags=re.M)
        (pkg / "article.md").write_text(md, encoding="utf-8")

    if not case_validate("CASE1 missing hero", miss_hero, "hero_image"):
        failures.append("CASE1")

    def bad_hero_dims(pkg: Path) -> None:
        write_png(pkg / "assets" / "hero.png", (10, 10, 10), w=800, h=450)

    if not case_validate("CASE2 wrong hero dims", bad_hero_dims, "1600"):
        failures.append("CASE2")

    def bad_social_dims(pkg: Path) -> None:
        write_png(pkg / "assets" / "social.png", (10, 10, 10), w=600, h=314)

    if not case_validate("CASE3 wrong social dims", bad_social_dims, "1200"):
        failures.append("CASE3")

    def word_count(pkg: Path) -> None:
        md = (pkg / "article.md").read_text(encoding="utf-8")
        md = md.rstrip() + "\n\n*(~1,150 words)*\n"
        (pkg / "article.md").write_text(md, encoding="utf-8")

    if not case_validate("CASE4 word-count note", word_count, "word-count"):
        failures.append("CASE4")

    def missing_asset(pkg: Path) -> None:
        (pkg / "assets" / "hero.png").unlink()

    if not case_validate("CASE5 missing asset file", missing_asset, "not found"):
        failures.append("CASE5")

    def bad_placement(pkg: Path) -> None:
        md = (pkg / "article.md").read_text(encoding="utf-8")
        md = md.replace("sections:\n  - owners", "sections:\n  - not_a_real_section")
        (pkg / "article.md").write_text(md, encoding="utf-8")

    if not case_validate("CASE6 unsupported placement", bad_placement, "placement.sections"):
        failures.append("CASE6")

    def dup_sources(pkg: Path) -> None:
        md = (pkg / "article.md").read_text(encoding="utf-8")
        md = md.replace(
            "sources: []",
            "sources:\n  - url: https://example.com/a\n    description: Example source",
        )
        md = md.rstrip() + "\n\n## Sources & Further Reading\n\n- [Other](https://example.com/b)\n"
        (pkg / "article.md").write_text(md, encoding="utf-8")

    if not case_validate("CASE7 duplicate sources forms", dup_sources, "duplicate Sources"):
        failures.append("CASE7")

    return failures


def run_healthy_and_presentation() -> list[str]:
    failures: list[str] = []
    content = ROOT / "chronicles" / "content"
    articles = load_all_articles(content)
    published = public_articles(articles)
    if not published:
        failures.append("no published articles in chronicles/content — production contract cannot soft-pass")
        _fail("empty published corpus")
        return failures
    _ok(f"published corpus size={len(published)}")

    errs = validate_articles(published, forbid_drafts=True)
    if errs:
        failures.append("published corpus validation")
        for e in errs[:12]:
            _fail(e)
        return failures
    _ok("published corpus validates (hero/social/dims/lint)")

    # CASE8 schema/org on rendered page
    sample = published[0]
    html = render_article_page(sample, articles)
    if ORG_ID not in html:
        failures.append("CASE8 Organization @id")
        _fail("missing Organization @id")
    else:
        _ok("CASE8 Organization @id present")
    if f'"@type": "{sample.schema_type}"' not in html and f'"@type":"{sample.schema_type}"' not in html:
        # pretty-printed JSON
        if f'"@type": "{sample.schema_type}"' not in html:
            if sample.schema_type not in html:
                failures.append("CASE8 schema_type")
                _fail("schema_type missing from page")
            else:
                _ok("CASE8 schema_type present")
        else:
            _ok("CASE8 schema_type present")
    else:
        _ok("CASE8 schema_type present")
    if f'rel="canonical"' not in html and "rel='canonical'" not in html:
        failures.append("CASE8 canonical")
        _fail("canonical missing")
    else:
        _ok("CASE8 canonical present")

    # Share / presentation markers
    for needle in (
        'data-chronicles-page="article"',
        'data-share-method="facebook"',
        'data-share-method="instagram"',
        'class="visually-hidden"',
        "chronicles-hero-figure",
    ):
        if needle not in html:
            failures.append(f"presentation:{needle}")
            _fail(f"missing {needle}")
        else:
            _ok(f"marker {needle}")

    if re.search(r'<h2[^>]*class="visually-quiet"[^>]*>\s*Share', html, re.I):
        failures.append("duplicate visible Share label")
        _fail("visible SHARE label should be visually-hidden only")
    else:
        _ok("no duplicate visible Share heading")

    # Source outbound new tab when sources exist in HTML
    for m in re.finditer(r"<a[^>]*data-chronicles-outbound=\"source\"[^>]*>", html):
        if 'target="_blank"' not in m.group(0):
            failures.append("source target=_blank")
            _fail(f"source link missing target=_blank: {m.group(0)}")
            break
    else:
        _ok("source links target=_blank (or none present)")

    # CASE10 CSS hero contract
    css = CSS.read_text(encoding="utf-8")
    if "chronicles-hero-figure" not in css or "42rem" not in css:
        failures.append("CASE10 hero CSS")
        _fail("hero figure 42rem rule missing from site.css")
    else:
        _ok("CASE10 hero max-width 42rem present in CSS")
    if "min(42rem" not in css and "max-width: 42rem" not in css and "width: min(42rem" not in css:
        failures.append("CASE10 hero width rule shape")
        _fail("expected width: min(42rem, ...) on hero figure")
    else:
        _ok("CASE10 hero width rule shape")

    # CASE9 surfaces
    sitemap = (ROOT / "sitemap-chronicles.xml").read_text(encoding="utf-8")
    feed = (ROOT / "chronicles" / "feed.xml").read_text(encoding="utf-8")
    search = (ROOT / "chronicles" / "assets" / "search-index.json").read_text(encoding="utf-8")
    for a in published:
        loc = f"https://lonkodigital.com/chronicles/{a.slug}/"
        if loc not in sitemap:
            failures.append(f"CASE9 sitemap:{a.slug}")
            _fail(f"sitemap missing {loc}")
        if a.slug not in feed:
            failures.append(f"CASE9 feed:{a.slug}")
            _fail(f"feed missing {a.slug}")
        if a.slug not in search:
            failures.append(f"CASE9 search:{a.slug}")
            _fail(f"search-index missing {a.slug}")
    if not any(f.startswith("CASE9") for f in failures):
        _ok("CASE9 sitemap/feed/search include all published slugs")

    # GA4 JS events
    write_chronicles_js()
    js = (ROOT / "chronicles" / "assets" / "chronicles.js").read_text(encoding="utf-8")
    for ev in (
        "chronicles_scroll_depth",
        "chronicles_share",
        "chronicles_outbound_source_click",
        "chronicles_internal_link_click",
        "chronicles_to_site_nav",
    ):
        if ev not in js or ev not in CHRONICLES_JS:
            failures.append(f"ga4:{ev}")
            _fail(f"missing event {ev}")
        else:
            _ok(f"ga4 event {ev}")

    return failures


def main() -> int:
    print("CHRONICLES PRODUCTION CONTRACT v2")
    print("--- failure simulations ---")
    failures = run_failure_simulations()
    print("--- healthy corpus + presentation ---")
    failures.extend(run_healthy_and_presentation())
    if failures:
        print("PRODUCTION CONTRACT: FAIL")
        print("Failed cases:", ", ".join(failures))
        return 1
    print("PRODUCTION CONTRACT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
