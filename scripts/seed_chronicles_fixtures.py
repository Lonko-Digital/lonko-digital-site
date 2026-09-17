#!/usr/bin/env python3
"""Seed synthetic Chronicles fixture packages for local QA (not live editorial).

Creates chronicles/_local_fixtures/<slug>/ with article.md + SVG/PNG assets.
These are gitignored and never shipped. For a local fixture build:

  CHRONICLES_CONTENT=chronicles/_local_fixtures python scripts/build_chronicles.py

Safe to re-run; overwrites fixture packages only.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "chronicles" / "_local_fixtures"

# Minimal PNG (solid color) for social crawler compatibility tests
def write_png(path: Path, rgb: tuple[int, int, int], w: int = 1200, h: int = 630) -> None:
    r, g, b = rgb

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + bytes([r, g, b]) * w for _ in range(h))
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def svg_abstraction(path: Path, kind: str = "fragment") -> None:
    if kind == "fragment":
        marks = "".join(
            f'<line x1="{20 + i * 18}" y1="{30 + (i % 3) * 20}" x2="{40 + i * 14}" '
            f'y2="{70 + (i % 4) * 12}" stroke="#5c6370" stroke-width="2" '
            f'stroke-dasharray="4 3" transform="rotate({i * 17} 80 80)"/>'
            for i in range(8)
        )
        body = marks
    elif kind == "organize":
        body = (
            '<path d="M20 40 L70 80 L20 120" fill="none" stroke="#5c6370" '
            'stroke-width="2" stroke-dasharray="5 4"/>'
            '<path d="M20 80 L140 80" fill="none" stroke="#5c6370" '
            'stroke-width="2" stroke-dasharray="5 4"/>'
            '<path d="M20 120 L70 80" fill="none" stroke="#5c6370" '
            'stroke-width="2" stroke-dasharray="5 4"/>'
        )
    else:  # resolve / chart
        body = '<line x1="24" y1="80" x2="156" y2="80" stroke="#E10600" stroke-width="4"/>'
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 160" role="img">'
        f"<rect width='180' height='160' fill='#f0f2f5'/>{body}</svg>\n",
        encoding="utf-8",
    )


def svg_chart(path: Path) -> None:
    path.write_text(
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 360" role="img">
  <rect width="640" height="360" fill="#f7f8fa"/>
  <text x="32" y="40" font-family="Segoe UI,sans-serif" font-size="18" fill="#1a1d24">Illustrative conversion rate</text>
  <polyline fill="none" stroke="#5c6370" stroke-width="3" points="60,280 140,240 220,250 300,190 380,200 460,140 540,160"/>
  <line x1="60" y1="300" x2="580" y2="300" stroke="#dfe3ea"/>
  <line x1="60" y1="80" x2="60" y2="300" stroke="#dfe3ea"/>
</svg>
""",
        encoding="utf-8",
    )


def svg_photo_standin(path: Path, label: str) -> None:
    """Purposeful non-stock stand-in: quiet storefront silhouette, not handshake/boardroom."""
    path.write_text(
        f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 675" role="img">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#d8dee8"/><stop offset="100%" stop-color="#eef1f5"/>
  </linearGradient></defs>
  <rect width="1200" height="675" fill="url(#g)"/>
  <rect x="180" y="220" width="420" height="280" fill="#9aa3b2"/>
  <rect x="220" y="280" width="90" height="140" fill="#c5cad3"/>
  <rect x="340" y="280" width="90" height="140" fill="#c5cad3"/>
  <rect x="460" y="300" width="100" height="200" fill="#7d8696"/>
  <circle cx="860" cy="200" r="48" fill="#b8c0cc"/>
  <text x="180" y="560" font-family="Georgia,serif" font-size="36" fill="#1a1d24">{label}</text>
</svg>
""",
        encoding="utf-8",
    )


def write_article(slug: str, front: dict, body: str, assets: dict[str, callable] | None = None) -> None:
    pkg = CONTENT / slug
    pkg.mkdir(parents=True, exist_ok=True)
    # YAML front matter (hand-written for clarity / stable ordering)
    lines = ["---"]
    order = [
        "title", "deck", "slug", "topic", "tags", "content_type", "author",
        "status", "datePublished", "dateModified", "schema_type",
        "seo_title", "meta_description", "og_title", "og_description",
        "social_image", "hero_image", "hero_alt", "imagery_family", "hero_caption",
        "sources", "placement", "related", "is_fixture",
    ]
    import yaml

    data = {k: front[k] for k in order if k in front}
    for k, v in front.items():
        if k not in data:
            data[k] = v
    yaml_text = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False)
    (pkg / "article.md").write_text(f"---\n{yaml_text}---\n\n{body.strip()}\n", encoding="utf-8")
    if assets:
        for name, fn in assets.items():
            fn(pkg / name)


def body_paragraphs(n: int, seed: str) -> str:
    base = (
        f"{seed} Marketing teams often collect more platform reports than they can interpret. "
        "The useful question is rarely what the dashboard shows first — it is which signal "
        "deserves attention before spend or creative changes. Lonko Chronicles fixtures use "
        "synthetic scenarios so the publishing system can be tested end-to-end."
    )
    parts = [f"## What this piece covers\n\n{base}"]
    for i in range(1, n):
        parts.append(
            f"## Section {i}\n\n"
            f"In scenario {i}, evidence from advertising, analytics, and on-site behavior "
            f"must be weighed together. A stable click volume with declining conversion rate "
            f"is a different problem than a sudden traffic drop. {base}"
        )
    return "\n\n".join(parts)


FIXTURES = []


def main() -> None:
    CONTENT.mkdir(parents=True, exist_ok=True)

    # —— E2E publishing-contract package (realistic, complete) ——————————
    write_article(
        "when-stable-traffic-hides-a-conversion-problem",
        {
            "title": "When stable traffic hides a conversion problem",
            "deck": "A practical way to separate volume from efficiency before you raise ad spend.",
            "slug": "when-stable-traffic-hides-a-conversion-problem",
            "topic": "Marketing",
            "tags": ["google ads", "conversion rate", "business owners", "measurement"],
            "content_type": "Analysis",
            "author": "Lonko Digital",
            "status": "fixture",
            "datePublished": "2026-09-12",
            "dateModified": "2026-09-14",
            "schema_type": "Article",
            "seo_title": "When stable traffic hides a conversion problem | Lonko Chronicles",
            "meta_description": "How to investigate declining conversions when advertising traffic still looks stable — without guessing.",
            "og_title": "When stable traffic hides a conversion problem",
            "og_description": "Separate volume from efficiency before you raise spend.",
            "social_image": "social.png",
            "hero_image": "hero.svg",
            "hero_alt": "Line chart showing stable traffic alongside a declining conversion rate",
            "imagery_family": "chart-diagram",
            "hero_caption": "Illustrative synthetic series — not a customer account.",
            "sources": [
                {
                    "url": "https://support.google.com/google-ads/answer/1722022",
                    "description": "Google Ads Help: About conversion tracking (verified reference for definitions).",
                }
            ],
            "placement": {"featured": 10, "sections": ["owners"]},
            "related": [
                "how-to-read-a-marketing-report-without-getting-lost",
                "ai-answers-are-not-the-same-as-business-evidence",
            ],
            "is_fixture": True,
        },
        """
## The question worth asking first

When clicks hold steady but leads fall, the instinct is often to change bids or creative. Sometimes that is right. Often it is premature.

::: callout
This article uses a synthetic scenario for publishing-system validation. It is not a customer case study.
:::

## What “stable traffic” can conceal

Traffic volume and conversion efficiency are related but not identical. A campaign can deliver a similar number of sessions while the share of visitors who complete a meaningful action declines.

That pattern usually points downstream: landing-page friction, tracking gaps, shifting audience quality, device mix, or a recent site change — not necessarily “not enough spend.”

## A disciplined first pass

1. Confirm conversion tracking still fires on the actions you care about.
2. Compare conversion rate and volume across the same windows — not vanity peaks.
3. Segment by device and campaign before rewriting the whole account.
4. Check whether site changes landed in the same window as the decline.

::: pullquote
Stable clicks are not proof that the customer journey still works.
:::

## What to do next

Investigate the journey before increasing budget. If tracking is broken, more spend amplifies noise. If a landing page regressed, creative tests will not fix it.

## How confident should you be?

Moderate — until website and analytics evidence are reviewed alongside the advertising data. Chronicles exists to make that sequencing obvious.
""",
        assets={
            "hero.svg": svg_chart,
            "social.png": lambda p: write_png(p, (30, 40, 55)),
            "inline-chart.svg": svg_chart,
        },
    )

    # Long article with pullquote + chart embed
    write_article(
        "how-to-read-a-marketing-report-without-getting-lost",
        {
            "title": "How to read a marketing report without getting lost",
            "deck": "A guide for business owners who need clarity, not another tab of charts.",
            "slug": "how-to-read-a-marketing-report-without-getting-lost",
            "topic": "Growth",
            "tags": ["reporting", "business owners", "dashboards"],
            "content_type": "Guide",
            "author": "Lonko Digital",
            "status": "fixture",
            "datePublished": "2026-09-10",
            "dateModified": "2026-09-10",
            "schema_type": "BlogPosting",
            "social_image": "social.png",
            "hero_image": "hero.svg",
            "hero_alt": "Abstract converging dashed lines representing organized marketing evidence",
            "imagery_family": "abstraction",
            "placement": {"featured": False, "sections": ["guides", "owners"]},
            "related": ["when-stable-traffic-hides-a-conversion-problem"],
            "sources": [
                {"url": "https://www.w3.org/WAI/standards-guidelines/wcag/", "description": "WCAG overview (accessibility discipline reference)."}
            ],
            "is_fixture": True,
        },
        body_paragraphs(8, "Report literacy.")
        + "\n\n::: pullquote\nIf a report does not change a decision, it is decoration.\n:::\n\n"
        + "![Illustrative trend](inline-chart.svg)\n\n"
        + body_paragraphs(4, "After the chart."),
        assets={
            "hero.svg": lambda p: svg_abstraction(p, "organize"),
            "social.png": lambda p: write_png(p, (55, 60, 70)),
            "inline-chart.svg": svg_chart,
        },
    )

    # Short article
    write_article(
        "three-questions-before-you-trust-an-ai-summary",
        {
            "title": "Three questions before you trust an AI summary",
            "deck": "Confidence is not the same thing as evidence.",
            "slug": "three-questions-before-you-trust-an-ai-summary",
            "topic": "AI & Technology",
            "tags": ["ai", "evidence", "trust"],
            "content_type": "Analysis",
            "author": "Lonko Digital",
            "status": "fixture",
            "datePublished": "2026-09-08",
            "dateModified": "2026-09-08",
            "schema_type": "Article",
            "social_image": "social.png",
            "hero_image": "hero.svg",
            "hero_alt": "Fragmented dashed line marks suggesting incomplete AI evidence",
            "imagery_family": "abstraction",
            "placement": {"featured": 5, "sections": ["owners"]},
            "related": ["ai-answers-are-not-the-same-as-business-evidence"],
            "is_fixture": True,
        },
        """
## Ask these first

1. What source material did the summary actually see?
2. What would falsify the conclusion?
3. Who is accountable if the recommendation is wrong?

Short piece by design — fixture for compact reading length.
""",
        assets={
            "hero.svg": lambda p: svg_abstraction(p, "fragment"),
            "social.png": lambda p: write_png(p, (70, 40, 40)),
        },
    )

    write_article(
        "ai-answers-are-not-the-same-as-business-evidence",
        {
            "title": "AI answers are not the same as business evidence",
            "deck": "Fluent language can hide thin sourcing. Here is how to tell the difference.",
            "slug": "ai-answers-are-not-the-same-as-business-evidence",
            "topic": "AI & Technology",
            "tags": ["ai", "evidence", "seo", "geo"],
            "content_type": "Analysis",
            "author": "Lonko Digital",
            "status": "fixture",
            "datePublished": "2026-09-01",
            "dateModified": "2026-09-05",
            "schema_type": "Article",
            "social_image": "social.png",
            "hero_image": "hero.svg",
            "hero_alt": "Resolved red decision line after organized evidence marks",
            "imagery_family": "abstraction",
            "placement": {"featured": False, "sections": ["owners"]},
            "related": ["three-questions-before-you-trust-an-ai-summary"],
            "is_fixture": True,
        },
        body_paragraphs(5, "Evidence standards for AI-assisted marketing."),
        assets={
            "hero.svg": lambda p: svg_abstraction(p, "resolve"),
            "social.png": lambda p: write_png(p, (40, 40, 48)),
        },
    )

    # Photography family stand-in
    write_article(
        "what-a-local-shop-needs-from-marketing-data",
        {
            "title": "What a local shop needs from marketing data",
            "deck": "Owners do not need another platform login — they need a next step.",
            "slug": "what-a-local-shop-needs-from-marketing-data",
            "topic": "Growth",
            "tags": ["local", "retail", "business owners"],
            "content_type": "News",
            "author": "Lonko Digital",
            "status": "fixture",
            "datePublished": "2026-08-28",
            "dateModified": "2026-08-28",
            "schema_type": "NewsArticle",
            "social_image": "social.png",
            "hero_image": "hero.svg",
            "hero_alt": "Quiet storefront silhouette representing a local retail business",
            "imagery_family": "photography",
            "hero_caption": "Synthetic editorial stand-in — not stock photography.",
            "placement": {"featured": False, "sections": ["owners", "from_lonko"]},
            "related": ["when-stable-traffic-hides-a-conversion-problem"],
            "is_fixture": True,
        },
        body_paragraphs(3, "Local retail context.")
        + "\n\nThis piece also exercises a rare NewsArticle schema_type for timely framing — still a fixture.",
        assets={
            "hero.svg": lambda p: svg_photo_standin(p, "Local retail — synthetic"),
            "social.png": lambda p: write_png(p, (90, 95, 100)),
        },
    )

    # SEO topic + How-To content_type (dormant UI field)
    write_article(
        "a-practical-checklist-for-seo-changes-that-might-hurt-leads",
        {
            "title": "A practical checklist for SEO changes that might hurt leads",
            "deck": "Before you rewrite the site, know which edits can quietly damage conversion paths.",
            "slug": "a-practical-checklist-for-seo-changes-that-might-hurt-leads",
            "topic": "SEO",
            "tags": ["seo", "conversion", "checklist"],
            "content_type": "How-To",
            "author": "Lonko Digital",
            "status": "fixture",
            "datePublished": "2026-08-20",
            "dateModified": "2026-08-22",
            "schema_type": "BlogPosting",
            "social_image": "social.png",
            "hero_image": "hero.svg",
            "hero_alt": "Simple diagram of a checklist path for SEO risk review",
            "imagery_family": "chart-diagram",
            "placement": {"featured": False, "sections": ["guides"]},
            "related": ["how-to-read-a-marketing-report-without-getting-lost"],
            "is_fixture": True,
        },
        body_paragraphs(4, "SEO change risk.")
        + "\n\n`content_type: How-To` is stored for forward-compatibility; launch UI does not filter on it.",
        assets={
            "hero.svg": svg_chart,
            "social.png": lambda p: write_png(p, (45, 55, 65)),
        },
    )

    # Compact / no image
    write_article(
        "a-note-on-updating-stories-in-place",
        {
            "title": "A note on updating stories in place",
            "deck": "Same URL, honest dateModified — when the intent has not changed.",
            "slug": "a-note-on-updating-stories-in-place",
            "topic": "Marketing",
            "tags": ["publishing", "seo"],
            "content_type": "News",
            "author": "Lonko Digital",
            "status": "fixture",
            "datePublished": "2026-08-15",
            "dateModified": "2026-09-01",
            "schema_type": "Article",
            "social_image": "social.png",
            # no hero_image — compact edge case; hero_alt omitted intentionally when no hero
            "imagery_family": "abstraction",
            "placement": {"featured": False, "sections": ["from_lonko"]},
            "is_fixture": True,
        },
        "When the story intent stays the same, update the existing URL and `dateModified`. New URLs are for new stories.",
        assets={"social.png": lambda p: write_png(p, (50, 50, 50))},
    )

    # Very long headline edge case
    write_article(
        "why-business-owners-should-treat-platform-metrics-as-evidence-not-instructions",
        {
            "title": "Why business owners should treat platform metrics as evidence, not instructions — and what to ask instead when the numbers disagree",
            "deck": "Long-headline fixture for layout stress testing.",
            "slug": "why-business-owners-should-treat-platform-metrics-as-evidence-not-instructions",
            "topic": "Marketing",
            "tags": ["metrics", "evidence"],
            "content_type": "Analysis",
            "author": "Lonko Digital",
            "status": "fixture",
            "datePublished": "2026-08-12",
            "dateModified": "2026-08-12",
            "schema_type": "Article",
            "social_image": "social.png",
            "hero_image": "hero.svg",
            "hero_alt": "Abstract marks representing conflicting platform metrics",
            "imagery_family": "abstraction",
            "placement": {"featured": False, "sections": ["owners"]},
            "is_fixture": True,
        },
        body_paragraphs(2, "Long headline stress."),
        assets={
            "hero.svg": lambda p: svg_abstraction(p, "fragment"),
            "social.png": lambda p: write_png(p, (60, 55, 50)),
        },
    )

    # Short headline
    write_article(
        "spend-less-guesswork",
        {
            "title": "Spend less guesswork",
            "deck": "Tiny title fixture.",
            "slug": "spend-less-guesswork",
            "topic": "Growth",
            "tags": ["growth"],
            "content_type": "Research",
            "author": "Lonko Digital",
            "status": "fixture",
            "datePublished": "2026-08-10",
            "dateModified": "2026-08-10",
            "schema_type": "Article",
            "social_image": "social.png",
            "hero_image": "hero.svg",
            "hero_alt": "Single resolved decision line",
            "imagery_family": "abstraction",
            "placement": {"featured": False, "sections": ["guides"]},
            "is_fixture": True,
        },
        "Research-typed fixture with a deliberately short title for card layout QA.",
        assets={
            "hero.svg": lambda p: svg_abstraction(p, "resolve"),
            "social.png": lambda p: write_png(p, (35, 35, 40)),
        },
    )

    # Hero vs social different creatives (already true for chart vs png; reinforce)
    write_article(
        "linkedin-preview-images-are-not-your-hero-crop",
        {
            "title": "LinkedIn preview images are not your hero crop",
            "deck": "Social crawlers and on-site heroes are two delivery jobs — treat them that way.",
            "slug": "linkedin-preview-images-are-not-your-hero-crop",
            "topic": "Marketing",
            "tags": ["linkedin", "open graph", "creative"],
            "content_type": "How-To",
            "author": "Lonko Digital",
            "status": "fixture",
            "datePublished": "2026-08-05",
            "dateModified": "2026-08-05",
            "schema_type": "BlogPosting",
            "social_image": "social.png",
            "hero_image": "hero.svg",
            "hero_alt": "Wide editorial diagram distinct from the solid social card color field",
            "imagery_family": "chart-diagram",
            "placement": {"featured": False, "sections": ["guides"]},
            "is_fixture": True,
        },
        body_paragraphs(3, "Social vs hero delivery.")
        + "\n\nThis package uses a PNG social card and an SVG hero on purpose.",
        assets={
            "hero.svg": svg_chart,
            "social.png": lambda p: write_png(p, (225, 30, 20)),  # distinct red-ish social field
        },
    )

    # Volume fillers for pagination + search suite (body-only hit target)
    fillers = [
        ("google-ads-budget-pacing-for-busy-owners", "Marketing", "google ads", "2026-07-28", "Budgets"),
        ("search-queries-that-look-useful-but-waste-spend", "SEO", "search queries", "2026-07-20", "Queries"),
        ("measuring-landing-page-friction-without-vanity-charts", "Growth", "landing page", "2026-07-12", "Friction"),
        ("when-brand-search-rises-and-leads-do-not", "SEO", "brand search", "2026-07-04", "Brand"),
        ("a-calmer-way-to-review-weekly-ad-performance", "Marketing", "weekly review", "2026-06-26", "Weekly"),
        ("entity-clarity-for-local-service-businesses", "SEO", "local seo", "2026-06-18", "Entities"),
        ("why-dashboard-green-is-not-a-strategy", "Growth", "dashboards", "2026-06-10", "Green"),
        ("platform-outages-and-what-to-check-first", "AI & Technology", "platform outage", "2026-06-02", "Outages"),
        ("creative-fatigue-signals-worth-believing", "Marketing", "creative fatigue", "2026-05-25", "Creative"),
        ("attribution-confidence-in-plain-language", "Growth", "attribution", "2026-05-17", "Attribution"),
        ("the-hidden-cost-of-unverified-tracking", "Marketing", "conversion tracking", "2026-05-09", "Tracking"),
        ("systems-habits-worth-keeping-as-you-scale", "AI & Technology", "systems", "2026-05-01", "Systems"),
    ]
    for i, (slug, topic, tag, date, seed) in enumerate(fillers):
        # Special body-only search target
        extra = ""
        if slug == "systems-habits-worth-keeping-as-you-scale":
            extra = (
                "\n\nDeep in this article sits the unique phrase **xylophone funnel audit**, "
                "which should be discoverable in full-text search Option B but not metadata-only Option A.\n"
            )
        kind = "fragment" if i % 2 == 0 else "organize"
        rgb = ((40 + i * 8) % 200, 45, 50)

        def make_hero(p: Path, _kind: str = kind) -> None:
            svg_abstraction(p, _kind)

        def make_social(p: Path, _rgb: tuple[int, int, int] = rgb) -> None:
            write_png(p, _rgb)

        write_article(
            slug,
            {
                "title": slug.replace("-", " ").capitalize(),
                "deck": f"Synthetic fixture on {tag} for pagination and search benchmarks.",
                "slug": slug,
                "topic": topic,
                "tags": [tag, "fixture"],
                "content_type": "Analysis",
                "author": "Lonko Digital",
                "status": "fixture",
                "datePublished": date,
                "dateModified": date,
                "schema_type": "Article",
                "social_image": "social.png",
                "hero_image": "hero.svg",
                "hero_alt": f"Synthetic hero graphic for {slug}",
                "imagery_family": "abstraction" if i % 2 == 0 else "chart-diagram",
                "placement": {"featured": False, "sections": ["guides"] if i % 3 == 0 else []},
                "is_fixture": True,
            },
            body_paragraphs(3, f"{seed}.") + extra,
            assets={"hero.svg": make_hero, "social.png": make_social},
        )

    # Draft (must not appear in public output)
    write_article(
        "draft-should-never-ship",
        {
            "title": "Draft should never ship",
            "deck": "Validator / build exclusion test.",
            "slug": "draft-should-never-ship",
            "topic": "Marketing",
            "tags": ["draft"],
            "content_type": "Analysis",
            "author": "Lonko Digital",
            "status": "draft",
            "datePublished": "2026-09-16",
            "dateModified": "2026-09-16",
            "schema_type": "Article",
            "is_fixture": False,
        },
        "If this page is publicly listed, the build contract failed.",
    )

    print(f"Seeded fixtures under {CONTENT}")
    print("Packages:", len([p for p in CONTENT.iterdir() if p.is_dir()]))


if __name__ == "__main__":
    main()
