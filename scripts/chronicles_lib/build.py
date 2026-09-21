"""Build Lonko Chronicles static pages, feeds, sitemaps, and search indexes."""

from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import datetime, timezone
from email.utils import formatdate
from pathlib import Path
from typing import Iterable
from urllib.parse import quote
from xml.sax.saxutils import escape as xml_escape

from .image_dims import read_image_size
from .model import (
    TOPIC_PILLS,
    Article,
    fixture_articles,
    load_all_articles,
    public_articles,
    renderable_articles,
    site_visible_articles,
    sort_by_date,
)
from .render_md import escape_text, markdown_to_html
from .shell import (
    ROOT,
    asset_prefix,
    head_open,
    header_html,
    scripts_close,
)
from .validate import SITE_OG_FALLBACK, validate_articles

SITE = "https://lonkodigital.com"
# Default: production content tree. Local fixtures: CHRONICLES_CONTENT=chronicles/_local_fixtures
_content_env = __import__("os").environ.get("CHRONICLES_CONTENT", "").strip()
CONTENT = (ROOT / _content_env).resolve() if _content_env else (ROOT / "chronicles" / "content")
OUT = ROOT / "chronicles"
PAGE_SIZE = 10
FEED_RETENTION = 20

CORE_PAGES = [
    ("/", None),
    ("/about/", None),
    ("/insights/", None),
    ("/contact/", None),
    ("/privacy/", None),
    ("/terms/", None),
]


# —— Path / asset helpers ————————————————————————————————————————————————


def article_url(slug: str) -> str:
    return f"{SITE}/chronicles/{slug}/"


def abs_asset_url(rel: str) -> str:
    rel = rel.lstrip("/")
    return f"{SITE}/{rel}"


def resolve_social_image_url(article: Article) -> str:
    if article.social_image:
        # Package-relative → published under /chronicles/<slug>/
        if "://" in article.social_image:
            return article.social_image
        return abs_asset_url(f"chronicles/{article.slug}/{article.social_image}")
    return abs_asset_url(SITE_OG_FALLBACK)


def package_asset_path(article: Article, rel: str | None) -> Path | None:
    """Resolve a package-relative media path for dimension reads."""
    if not rel or not article.package_dir:
        return None
    if "://" in rel or rel.startswith("/"):
        return None
    candidate = Path(rel)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    path = (article.package_dir / candidate).resolve()
    try:
        path.relative_to(article.package_dir.resolve())
    except ValueError:
        return None
    return path if path.is_file() else None


def social_image_dims(article: Article) -> tuple[int, int] | None:
    """Intrinsic size of the finalized social/OG image (never assumed)."""
    if article.social_image:
        path = package_asset_path(article, article.social_image)
        if path:
            return read_image_size(path)
        return None
    fallback = ROOT / SITE_OG_FALLBACK
    return read_image_size(fallback)


def site_og_fallback_dims() -> tuple[int, int] | None:
    return read_image_size(ROOT / SITE_OG_FALLBACK)


def package_media_href(article: Article, rel: str | None, *, from_depth: int) -> str | None:
    if not rel:
        return None
    if "://" in rel or rel.startswith("/"):
        return rel
    # Article page (depth 2): media copied beside index.html → relative path as-authored
    if from_depth == 2:
        return rel
    # Chronicles index (depth 1): slug/images/...
    if from_depth <= 1:
        return f"{article.slug}/{rel}"
    # Deeper pages (e.g. page/N at depth 3): climb to chronicles/ then into slug/
    return f"{asset_prefix(from_depth - 1)}{article.slug}/{rel}"


def copy_package_assets(article: Article) -> None:
    """Copy non-markdown package files into chronicles/<slug>/."""
    if not article.package_dir or not article.package_dir.is_dir():
        return
    dest = OUT / article.slug
    dest.mkdir(parents=True, exist_ok=True)
    for path in article.package_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.name == "article.md":
            continue
        rel = path.relative_to(article.package_dir)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


# —— Card / section HTML ————————————————————————————————————————————————


def _meta_line(article: Article) -> str:
    parts = [
        escape_text(article.content_type),
        escape_text(article.topic),
        escape_text(article.datePublished),
        f"{article.reading_time} min read",
    ]
    return " · ".join(parts)


def story_card(
    article: Article,
    *,
    variant: str,
    depth: int,
) -> str:
    """variant: feature | standard | compact

    depth is filesystem depth from site root (chronicles/=1, slug/=2, page/N/=3).
    Cards always link to /chronicles/<slug>/ via a relative path from that depth.
    """
    # From chronicles/ (1) -> slug/; from slug/ (2) -> ../slug/; from page/N/ (3) -> ../../slug/
    if depth <= 0:
        href = f"chronicles/{article.slug}/"
    else:
        href = f"{asset_prefix(depth - 1)}{article.slug}/"

    img_rel = package_media_href(article, article.hero_image, from_depth=depth)
    img_html = ""
    if img_rel and variant != "compact":
        alt = escape_text(article.hero_alt or "")
        img_html = (
            f'<div class="chronicles-card-media">'
            f'<img src="{escape_text(img_rel)}" alt="{alt}" loading="lazy" decoding="async">'
            f"</div>"
        )
    elif img_rel and variant == "compact":
        alt = escape_text(article.hero_alt or "")
        img_html = (
            f'<div class="chronicles-card-media chronicles-card-media--compact">'
            f'<img src="{escape_text(img_rel)}" alt="{alt}" loading="lazy" decoding="async">'
            f"</div>"
        )

    cls = {
        "feature": "story-feature",
        "standard": "story-standard",
        "compact": "story-compact",
    }.get(variant, "story-compact")

    return f"""
<article class="chronicles-card {cls}" data-slug="{escape_text(article.slug)}" data-topic="{escape_text(article.topic)}" data-title="{escape_text(article.title)}" data-deck="{escape_text(article.deck)}" data-tags="{escape_text(','.join(article.tags))}">
  <a class="chronicles-card-link" href="{escape_text(href)}">
    {img_html}
    <div class="chronicles-card-body">
      <p class="chronicles-card-meta">{_meta_line(article)}</p>
      <h3 class="chronicles-card-title">{escape_text(article.title)}</h3>
      <p class="chronicles-card-deck">{escape_text(article.deck)}</p>
    </div>
  </a>
</article>
""".strip()


def pick_featured(articles: list[Article]) -> Article | None:
    candidates = [a for a in articles if a.featured_priority() is not None]
    if not candidates:
        return None
    return max(candidates, key=lambda a: (a.featured_priority() or 0, a.datePublished, a.slug))


def section_articles(articles: list[Article], section: str) -> list[Article]:
    matched = [a for a in articles if section in a.sections]
    return sort_by_date(matched)


def related_for(article: Article, corpus: list[Article], *, limit: int = 3) -> list[Article]:
    by_slug = {a.slug: a for a in corpus}
    if article.related:
        return [by_slug[s] for s in article.related if s in by_slug and s != article.slug][:limit]
    # Automatic: same topic, then shared tags
    others = [a for a in corpus if a.slug != article.slug]
    same_topic = [a for a in others if a.topic == article.topic]
    if same_topic:
        return sort_by_date(same_topic)[:limit]
    tag_set = set(article.tags)
    scored = []
    for a in others:
        overlap = len(tag_set & set(a.tags))
        if overlap:
            scored.append((overlap, a.datePublished, a))
    scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
    return [t[2] for t in scored[:limit]]


# —— Page builders ——————————————————————————————————————————————————————


def render_article_page(article: Article, corpus: list[Article]) -> str:
    depth = 2
    body_html = markdown_to_html(article.body)
    canonical = article_url(article.slug)
    og_image = resolve_social_image_url(article)
    if article.is_retired():
        robots = "noindex, nofollow"
    elif article.is_fixture or article.status == "fixture":
        robots = "noindex, nofollow"
    else:
        robots = None

    schema = {
        "@context": "https://schema.org",
        "@type": article.schema_type,
        "headline": article.title,
        "description": article.display_description,
        "datePublished": article.datePublished,
        "dateModified": article.dateModified,
        "author": {
            "@type": "Organization",
            "name": article.author,
            "url": SITE,
        },
        "publisher": {
            "@type": "Organization",
            "name": "Lonko Digital",
            "url": SITE,
            "logo": {
                "@type": "ImageObject",
                "url": f"{SITE}/assets/images/lonko-logo.png",
            },
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
        "url": canonical,
        "inLanguage": "en-US",
        "isPartOf": {"@id": f"{SITE}/#website"},
    }
    if article.hero_image:
        images = [abs_asset_url(f"chronicles/{article.slug}/{article.hero_image}")]
        social = resolve_social_image_url(article)
        if social not in images:
            images.append(social)
        schema["image"] = images

    breadcrumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Chronicles", "item": f"{SITE}/chronicles/"},
            {"@type": "ListItem", "position": 3, "name": article.title, "item": canonical},
        ],
    }

    hero_html = ""
    if article.hero_image:
        src = package_media_href(article, article.hero_image, from_depth=2) or ""
        caption = (
            f'<figcaption class="chronicles-hero-caption">{escape_text(article.hero_caption)}</figcaption>'
            if article.hero_caption
            else ""
        )
        # Intrinsic dims from the asset (hero may differ from social 1.91:1).
        # Omit attrs when unknown rather than claiming a wrong aspect ratio.
        size_attrs = ""
        hero_path = package_asset_path(article, article.hero_image)
        if hero_path:
            dims = read_image_size(hero_path)
            if dims:
                size_attrs = f' width="{dims[0]}" height="{dims[1]}"'
        hero_html = f"""
        <figure class="chronicles-hero-figure chronicles-imagery-{escape_text(article.imagery_family or 'abstraction')}">
          <img src="{escape_text(src)}" alt="{escape_text(article.hero_alt or '')}"{size_attrs} decoding="async">
          {caption}
        </figure>
"""

    sources_html = ""
    if article.sources:
        items = "\n".join(
            f'          <li><a href="{escape_text(s["url"])}" rel="noopener noreferrer" data-chronicles-outbound="source">{escape_text(s["description"])}</a></li>'
            for s in article.sources
        )
        sources_html = f"""
      <section class="chronicles-sources" aria-labelledby="sources-heading">
        <h2 id="sources-heading">Sources &amp; Further Reading</h2>
        <ul>
{items}
        </ul>
      </section>
"""

    related = related_for(article, [a for a in corpus if a.is_site_visible()])
    related_html = ""
    if related:
        cards = "\n".join(story_card(a, variant="compact", depth=2) for a in related)
        related_html = f"""
      <section class="chronicles-related" aria-labelledby="related-heading">
        <h2 id="related-heading">Related Stories</h2>
        <div class="chronicles-card-grid chronicles-card-grid--related">
{cards}
        </div>
      </section>
"""

    share_url = quote(canonical, safe="")
    share_title = quote(article.title, safe="")
    share_html = f"""
      <section class="chronicles-share" aria-labelledby="share-heading">
        <h2 id="share-heading" class="visually-quiet">Share</h2>
        <div class="chronicles-share-controls" data-share-url="{escape_text(canonical)}" data-share-title="{escape_text(article.title)}">
          <button type="button" class="chronicles-share-btn" data-share-native data-share-method="native">Share</button>
          <button type="button" class="chronicles-share-btn" data-share-copy data-share-method="copy">Copy link</button>
          <a class="chronicles-share-btn" href="mailto:?subject={share_title}&amp;body={share_url}" data-share-method="email">Email</a>
          <a class="chronicles-share-btn" href="https://www.linkedin.com/sharing/share-offsite/?url={share_url}" rel="noopener noreferrer" target="_blank" data-share-method="linkedin">LinkedIn</a>
          <a class="chronicles-share-btn" href="https://twitter.com/intent/tweet?url={share_url}&amp;text={share_title}" rel="noopener noreferrer" target="_blank" data-share-method="x">X</a>
        </div>
        <p class="chronicles-share-status" aria-live="polite"></p>
      </section>
"""

    modified = ""
    if article.dateModified and article.dateModified != article.datePublished:
        modified = f' · Updated <time datetime="{escape_text(article.dateModified)}">{escape_text(article.dateModified)}</time>'

    # Temporary/test retired notice — final public wording routes through Claude Web.
    retired_notice = ""
    if article.is_retired():
        retired_notice = """
      <div class="chronicles-retired-notice" role="status">
        <p>This article has been retired from Lonko Chronicles. It remains available at this URL for reference.</p>
      </div>
"""

    main = f"""
  <main id="main" class="chronicles-article-page" data-chronicles-page="article" data-article-slug="{escape_text(article.slug)}">
    <article class="chronicles-article">
      <header class="chronicles-article-header container">
        <nav class="breadcrumbs" aria-label="Breadcrumb">
          <ol>
            <li><a href="../../">Home</a></li>
            <li><a href="../">Chronicles</a></li>
            <li aria-current="page">{escape_text(article.title)}</li>
          </ol>
        </nav>
{retired_notice}
        <p class="chronicles-kicker">{escape_text(article.content_type)} · {escape_text(article.topic)}</p>
        <h1>{escape_text(article.title)}</h1>
        <p class="chronicles-deck">{escape_text(article.deck)}</p>
        <p class="chronicles-byline">
          <span class="chronicles-author">{escape_text(article.author)}</span>
          · <time datetime="{escape_text(article.datePublished)}">{escape_text(article.datePublished)}</time>{modified}
          · <span class="chronicles-reading-time">{article.reading_time} min read</span>
        </p>
      </header>
{hero_html}
      <div class="container narrow">
        <div class="chronicles-article-body">
{body_html}
        </div>
{sources_html}
{related_html}
{share_html}
      </div>
    </article>
  </main>
"""

    og_dims = social_image_dims(article)
    head = head_open(
        depth=depth,
        title=f"{article.display_title} — Lonko Chronicles",
        description=article.display_description,
        canonical=canonical,
        og_title=article.display_og_title,
        og_description=article.display_og_description,
        og_image=og_image,
        og_image_width=og_dims[0] if og_dims else None,
        og_image_height=og_dims[1] if og_dims else None,
        og_type="article",
        robots=robots,
        include_regular_font=True,
        json_ld_blocks=[
            json.dumps(schema, ensure_ascii=False, indent=2),
            json.dumps(breadcrumbs, ensure_ascii=False, indent=2),
        ],
        extra_head=f'  <meta property="article:published_time" content="{escape_text(article.datePublished)}">\n'
        f'  <meta property="article:modified_time" content="{escape_text(article.dateModified)}">\n',
    )
    return (
        head
        + header_html(depth, current="Chronicles")
        + main
        + scripts_close(depth, extra_scripts=["../assets/chronicles.js"])
    )


def _topic_pills_html() -> str:
    buttons = []
    for label, topic in TOPIC_PILLS:
        value = topic or "all"
        pressed = "true" if value == "all" else "false"
        buttons.append(
            f'<button type="button" class="chronicles-topic-pill" data-topic-filter="{escape_text(value)}" aria-pressed="{pressed}">{escape_text(label)}</button>'
        )
    return "\n          ".join(buttons)


def render_index(
    visible: list[Article],
    *,
    latest_page: list[Article],
    page_num: int,
    total_pages: int,
    is_home: bool,
) -> str:
    depth = 1 if is_home or page_num == 1 else 3  # chronicles/page/N/
    if not is_home:
        depth = 3

    featured = pick_featured(visible) if is_home else None
    standards: list[Article] = []
    if is_home and featured:
        rest = [a for a in sort_by_date(visible) if a.slug != featured.slug]
        standards = rest[:2]
    elif is_home:
        standards = sort_by_date(visible)[:2]

    # Hero featured block (index only)
    featured_block = ""
    if is_home:
        feature_html = story_card(featured, variant="feature", depth=1) if featured else ""
        std_html = "\n".join(story_card(a, variant="standard", depth=1) for a in standards)
        featured_block = f"""
    <section class="chronicles-featured-hero" aria-label="Featured stories">
      <div class="container chronicles-featured-grid">
        <div class="chronicles-featured-primary">
          {feature_html or '<p class="chronicles-empty">No featured story yet.</p>'}
        </div>
        <div class="chronicles-featured-standards">
          {std_html}
        </div>
      </div>
    </section>
"""

    latest_cards = "\n".join(story_card(a, variant="compact", depth=depth) for a in latest_page)

    # Pagination links
    pag_html = ""
    if total_pages > 1:
        links = []
        if page_num > 1:
            prev_href = "../" if page_num == 2 else f"../{page_num - 1}/"
            if is_home:
                prev_href = "#"  # no prev on page 1
            else:
                if page_num == 2:
                    prev_href = "../../"
                else:
                    prev_href = f"../{page_num - 1}/"
                links.append(f'<a class="chronicles-page-link" rel="prev" href="{prev_href}">Previous</a>')
        if is_home and total_pages > 1:
            links.append('<a class="chronicles-page-link" rel="next" href="page/2/">Next</a>')
        elif not is_home and page_num < total_pages:
            links.append(
                f'<a class="chronicles-page-link" rel="next" href="../{page_num + 1}/">Next</a>'
            )
        if links:
            pag_html = f'<nav class="chronicles-pagination" aria-label="Pagination">{" ".join(links)}</nav>'

    curated = ""
    if is_home:
        for section_key, heading, section_id in (
            ("owners", "What Business Owners Should Know", "owners"),
            ("guides", "Learn / Guides", "guides"),
            ("from_lonko", "From Lonko", "from-lonko"),
        ):
            items = section_articles(visible, section_key)
            if section_key == "from_lonko" and not items:
                continue
            cards = "\n".join(story_card(a, variant="compact", depth=1) for a in items) if items else (
                '<p class="chronicles-empty">Nothing in this section yet.</p>'
            )
            curated += f"""
    <section class="chronicles-section chronicles-section--{section_id}" aria-labelledby="{section_id}-heading">
      <div class="container">
        <h2 id="{section_id}-heading">{escape_text(heading)}</h2>
        <div class="chronicles-card-grid" data-section="{section_key}">
{cards}
        </div>
      </div>
    </section>
"""

        curated += """
    <section class="chronicles-editorial-close" aria-labelledby="close-heading">
      <div class="container narrow">
        <p id="close-heading" class="chronicles-close-line">Understand more. Guess less.</p>
      </div>
    </section>
"""

    title = "Lonko Chronicles — Marketing Intelligence Editorial"
    if not is_home:
        title = f"Lonko Chronicles — Page {page_num}"

    canonical = f"{SITE}/chronicles/" if is_home else f"{SITE}/chronicles/page/{page_num}/"
    collection_schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": title,
        "url": canonical,
        "isPartOf": {"@id": f"{SITE}/#website"},
        "inLanguage": "en-US",
    }
    crumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Chronicles", "item": f"{SITE}/chronicles/"},
        ],
    }
    if not is_home:
        crumbs["itemListElement"].append(
            {"@type": "ListItem", "position": 3, "name": f"Page {page_num}", "item": canonical}
        )

    home_prefix = "../../" if not is_home else "../"
    chron_prefix = "../../" if not is_home else "./"

    hero = f"""
    <section class="chronicles-intro" aria-labelledby="chronicles-heading">
      <div class="container">
        <nav class="breadcrumbs" aria-label="Breadcrumb">
          <ol>
            <li><a href="{home_prefix}">Home</a></li>
            <li aria-current="page">Chronicles</li>
          </ol>
        </nav>
        <p class="hero-kicker">Lonko Digital</p>
        <h1 id="chronicles-heading">LONKO CHRONICLES</h1>
        <p class="hero-lead">Evidence-led editorial on marketing, AI, SEO, and growth — so businesses understand more and guess less.</p>
        <form class="chronicles-search" action="{chron_prefix}search/" method="get" role="search">
          <label class="visually-hidden" for="chronicles-q">Search Chronicles</label>
          <input id="chronicles-q" class="chronicles-search-input" type="search" name="q" placeholder="Search Chronicles" autocomplete="off">
          <button type="submit" class="btn btn-primary">Search</button>
        </form>
        <div class="chronicles-topic-pills" role="toolbar" aria-label="Filter by topic">
          {_topic_pills_html()}
        </div>
        <p class="chronicles-filter-status" aria-live="polite"></p>
      </div>
    </section>
"""

    latest_section = f"""
    <section class="chronicles-section chronicles-section--latest" aria-labelledby="latest-heading" data-chronicles-latest>
      <div class="container">
        <h2 id="latest-heading">{"Latest" if is_home else f"Latest — Page {page_num}"}</h2>
        <div class="chronicles-card-grid" data-filterable-cards>
{latest_cards}
        </div>
        {pag_html}
      </div>
    </section>
"""

    main = f"""
  <main id="main" class="chronicles-index">
{hero}
{featured_block}
{latest_section}
{curated if is_home else ""}
  </main>
"""

    js_path = "assets/chronicles.js" if is_home else "../../assets/chronicles.js"
    fb_dims = site_og_fallback_dims()
    head = head_open(
        depth=depth,
        title=title,
        description="Lonko Chronicles — evidence-led editorial on marketing intelligence, AI, SEO, and growth.",
        canonical=canonical,
        og_image_width=fb_dims[0] if fb_dims else None,
        og_image_height=fb_dims[1] if fb_dims else None,
        json_ld_blocks=[
            json.dumps(collection_schema, ensure_ascii=False, indent=2),
            json.dumps(crumbs, ensure_ascii=False, indent=2),
        ],
    )
    return (
        head
        + header_html(depth, current="Chronicles")
        + main
        + scripts_close(depth, extra_scripts=[js_path])
    )


def render_search_page() -> str:
    depth = 2
    fb_dims = site_og_fallback_dims()
    head = head_open(
        depth=depth,
        title="Search Chronicles — Lonko Digital",
        description="Search Lonko Chronicles.",
        canonical=f"{SITE}/chronicles/search/",
        robots="noindex, nofollow",
        og_image_width=fb_dims[0] if fb_dims else None,
        og_image_height=fb_dims[1] if fb_dims else None,
    )
    main = """
  <main id="main" class="chronicles-search-page">
    <section class="chronicles-intro chronicles-intro--search" aria-labelledby="search-heading">
      <div class="container">
        <nav class="breadcrumbs" aria-label="Breadcrumb">
          <ol>
            <li><a href="../../">Home</a></li>
            <li><a href="../">Chronicles</a></li>
            <li aria-current="page">Search</li>
          </ol>
        </nav>
        <h1 id="search-heading">Search Chronicles</h1>
        <form class="chronicles-search" action="./" method="get" role="search">
          <label class="visually-hidden" for="chronicles-q">Search Chronicles</label>
          <input id="chronicles-q" class="chronicles-search-input" type="search" name="q" placeholder="Search Chronicles" autocomplete="off">
          <button type="submit" class="btn btn-primary">Search</button>
        </form>
        <p class="chronicles-filter-status" aria-live="polite"></p>
        <div id="chronicles-search-results" class="chronicles-card-grid" data-search-results></div>
      </div>
    </section>
  </main>
"""
    return (
        head
        + header_html(depth, current="Chronicles")
        + main
        + scripts_close(depth, extra_scripts=["../assets/chronicles.js"])
    )


# —— Feeds / sitemaps / indexes / robots / JS ————————————————————————————


def _rfc822_date(iso_day: str) -> str:
    """Convert YYYY-MM-DD to an RSS 2.0 pubDate (midnight UTC)."""
    try:
        dt = datetime.strptime(iso_day, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return iso_day
    return formatdate(dt.timestamp(), usegmt=True)


def write_rss(published: list[Article]) -> None:
    items = sort_by_date(published)[:FEED_RETENTION]
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0">',
        "<channel>",
        "<title>Lonko Chronicles</title>",
        f"<link>{SITE}/chronicles/</link>",
        "<description>Evidence-led editorial from Lonko Digital.</description>",
    ]
    for a in items:
        parts.append("<item>")
        parts.append(f"<title>{xml_escape(a.title)}</title>")
        parts.append(f"<link>{article_url(a.slug)}</link>")
        parts.append(f'<guid isPermaLink="true">{article_url(a.slug)}</guid>')
        parts.append(f"<pubDate>{xml_escape(_rfc822_date(a.datePublished))}</pubDate>")
        parts.append(f"<description>{xml_escape(a.deck)}</description>")
        parts.append("</item>")
    parts.extend(["</channel>", "</rss>", ""])
    (OUT / "feed.xml").write_text("\n".join(parts), encoding="utf-8")


def _discover_insight_urls() -> list[str]:
    """Collect insight article URLs from the filesystem (read-only; never writes insights/)."""
    insights_root = ROOT / "insights"
    urls: list[str] = []
    if not insights_root.is_dir():
        return urls
    for child in sorted(insights_root.iterdir()):
        if child.is_dir() and (child / "index.html").is_file():
            urls.append(f"{SITE}/insights/{child.name}/")
    return urls


def write_sitemaps(published: list[Article], total_pages: int) -> None:
    # Core pages sitemap
    pages_urls = [
        f"{SITE}/",
        f"{SITE}/about/",
        f"{SITE}/insights/",
        f"{SITE}/chronicles/",
        f"{SITE}/contact/",
        f"{SITE}/privacy/",
        f"{SITE}/terms/",
    ]
    # Prefer filesystem discovery so rebuilds stay correct after sitemap.xml
    # becomes a sitemap index (do not mutate anything under insights/).
    for loc in _discover_insight_urls():
        if loc not in pages_urls:
            pages_urls.append(loc)
    # Fallback: also scrape sitemap-pages.xml if present from a prior build
    pages_map = ROOT / "sitemap-pages.xml"
    if pages_map.is_file():
        for m in re.finditer(r"<loc>(.*?)</loc>", pages_map.read_text(encoding="utf-8")):
            loc = m.group(1).strip()
            if "/insights/" in loc and loc not in pages_urls:
                pages_urls.append(loc)

    def urlset(urls: Iterable[tuple[str, str | None]]) -> str:
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        ]
        for loc, lastmod in urls:
            lines.append("  <url>")
            lines.append(f"    <loc>{xml_escape(loc)}</loc>")
            if lastmod:
                lines.append(f"    <lastmod>{xml_escape(lastmod)}</lastmod>")
            lines.append("  </url>")
        lines.append("</urlset>")
        lines.append("")
        return "\n".join(lines)

    (ROOT / "sitemap-pages.xml").write_text(
        urlset((u, None) for u in pages_urls),
        encoding="utf-8",
    )

    chron_entries: list[tuple[str, str | None]] = [(f"{SITE}/chronicles/", None)]
    for a in sort_by_date(published):
        chron_entries.append((article_url(a.slug), a.dateModified or a.datePublished))
    for n in range(2, total_pages + 1):
        chron_entries.append((f"{SITE}/chronicles/page/{n}/", None))

    (ROOT / "sitemap-chronicles.xml").write_text(urlset(chron_entries), encoding="utf-8")

    index = f"""<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>{SITE}/sitemap-pages.xml</loc>
  </sitemap>
  <sitemap>
    <loc>{SITE}/sitemap-chronicles.xml</loc>
  </sitemap>
</sitemapindex>
"""
    (ROOT / "sitemap.xml").write_text(index, encoding="utf-8")


def _plain_body(article: Article) -> str:
    text = re.sub(r"```.*?```", " ", article.body or "", flags=re.DOTALL)
    text = re.sub(r"[#>*_`\[\]\(\)!|]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def write_search_indexes(visible: list[Article]) -> None:
    assets = OUT / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    index_a = []
    index_b = []
    for a in sort_by_date(visible):
        # Fixtures included in on-site search UX; published+fixture
        meta = {
            "slug": a.slug,
            "title": a.title,
            "deck": a.deck,
            "topic": a.topic,
            "tags": a.tags,
            "content_type": a.content_type,
            "datePublished": a.datePublished,
            "url": f"/chronicles/{a.slug}/",
            "is_fixture": a.is_fixture,
        }
        index_a.append(meta)
        body = _plain_body(a)
        index_b.append({**meta, "body": body, "excerpt": body[:400]})

    (assets / "search-index-a.json").write_text(
        json.dumps(index_a, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (assets / "search-index-b.json").write_text(
        json.dumps(index_b, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    # Default = B (full editorial); benchmark script compares A vs B
    shutil.copy2(assets / "search-index-b.json", assets / "search-index.json")


def write_robots(fixture_slugs: list[str]) -> None:
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /chronicles/search",
        "Disallow: /chronicles/content/",
    ]
    for slug in fixture_slugs:
        lines.append(f"Disallow: /chronicles/{slug}/")
    lines.append("")
    lines.append(f"Sitemap: {SITE}/sitemap.xml")
    lines.append("")
    (ROOT / "robots.txt").write_text("\n".join(lines), encoding="utf-8")


CHRONICLES_JS = r"""(function () {
  "use strict";

  var statusEl = document.querySelector(".chronicles-filter-status");
  var pills = Array.prototype.slice.call(document.querySelectorAll("[data-topic-filter]"));
  var cards = Array.prototype.slice.call(document.querySelectorAll("[data-filterable-cards] .chronicles-card"));
  var searchInput = document.querySelector(".chronicles-search-input");
  var activeTopic = "all";
  var indexCache = null;

  function announce(msg) {
    if (statusEl) statusEl.textContent = msg || "";
  }

  function cardMatches(card, topic, q) {
    var t = (card.getAttribute("data-topic") || "").toLowerCase();
    if (topic && topic !== "all" && t !== topic.toLowerCase()) return false;
    if (!q) return true;
    var hay = [
      card.getAttribute("data-title") || "",
      card.getAttribute("data-deck") || "",
      card.getAttribute("data-tags") || "",
      t
    ].join(" ").toLowerCase();
    return hay.indexOf(q) !== -1;
  }

  function applyFilters() {
    var q = (searchInput && searchInput.value ? searchInput.value : "").trim().toLowerCase();
    var shown = 0;
    cards.forEach(function (card) {
      var ok = cardMatches(card, activeTopic, q);
      card.hidden = !ok;
      if (ok) shown += 1;
    });
    if (!cards.length) return;
    if (shown === 0) {
      announce("No stories match your filters. Try another topic or clear search.");
    } else {
      announce(shown + " stor" + (shown === 1 ? "y" : "ies") + " shown.");
    }
  }

  pills.forEach(function (btn) {
    btn.addEventListener("click", function () {
      activeTopic = btn.getAttribute("data-topic-filter") || "all";
      pills.forEach(function (b) {
        b.setAttribute("aria-pressed", b === btn ? "true" : "false");
      });
      applyFilters();
    });
  });

  if (searchInput && cards.length) {
    searchInput.addEventListener("input", applyFilters);
  }

  /* —— Search results page —— */
  var resultsRoot = document.querySelector("[data-search-results]");
  function indexUrl() {
    var scripts = document.getElementsByTagName("script");
    for (var i = 0; i < scripts.length; i++) {
      var src = scripts[i].src || "";
      if (src.indexOf("chronicles.js") !== -1) {
        return src.replace(/chronicles\.js(?:\?.*)?$/, "search-index.json");
      }
    }
    return "../assets/search-index.json";
  }

  function scoreEntry(entry, tokens) {
    var title = (entry.title || "").toLowerCase();
    var deck = (entry.deck || "").toLowerCase();
    var topic = (entry.topic || "").toLowerCase();
    var tags = (entry.tags || []).join(" ").toLowerCase();
    var body = (entry.body || entry.excerpt || "").toLowerCase();
    var score = 0;
    tokens.forEach(function (tok) {
      if (!tok) return;
      if (title === tok) score += 50;
      if (title.indexOf(tok) !== -1) score += 20;
      if (topic.indexOf(tok) !== -1) score += 12;
      if (tags.indexOf(tok) !== -1) score += 10;
      if (deck.indexOf(tok) !== -1) score += 8;
      if (body.indexOf(tok) !== -1) score += 2;
    });
    return score;
  }

  function renderResults(entries, q) {
    if (!resultsRoot) return;
    resultsRoot.innerHTML = "";
    if (!q) {
      announce("Enter a search to find stories.");
      return;
    }
    var tokens = q.toLowerCase().split(/\s+/).filter(Boolean);
    var ranked = entries
      .map(function (e) { return { e: e, s: scoreEntry(e, tokens) }; })
      .filter(function (x) { return x.s > 0; })
      .sort(function (a, b) { return b.s - a.s; });
    if (!ranked.length) {
      announce("No results for “" + q + "”.");
      resultsRoot.innerHTML = '<p class="chronicles-empty">No matching stories. Try a broader topic or different wording.</p>';
      return;
    }
    announce(ranked.length + " result" + (ranked.length === 1 ? "" : "s") + " for “" + q + "”.");
    ranked.forEach(function (row) {
      var e = row.e;
      var a = document.createElement("article");
      a.className = "chronicles-card story-compact";
      a.innerHTML =
        '<a class="chronicles-card-link" href="' + (e.url || ("../" + e.slug + "/")) + '">' +
        '<div class="chronicles-card-body">' +
        '<p class="chronicles-card-meta">' + (e.content_type || "") + " · " + (e.topic || "") + " · " + (e.datePublished || "") + "</p>" +
        "<h3 class=\"chronicles-card-title\">" + escapeHtml(e.title || "") + "</h3>" +
        "<p class=\"chronicles-card-deck\">" + escapeHtml(e.deck || "") + "</p>" +
        "</div></a>";
      resultsRoot.appendChild(a);
    });
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function loadIndex(cb) {
    if (indexCache) return cb(indexCache);
    var req = new XMLHttpRequest();
    req.open("GET", indexUrl(), true);
    req.onload = function () {
      try {
        indexCache = JSON.parse(req.responseText);
      } catch (err) {
        indexCache = [];
      }
      cb(indexCache);
    };
    req.onerror = function () { cb([]); };
    req.send();
  }

  if (resultsRoot) {
    var params = new URLSearchParams(window.location.search);
    var q = params.get("q") || "";
    if (searchInput) searchInput.value = q;
    loadIndex(function (data) { renderResults(data, q); });
    var form = document.querySelector(".chronicles-search");
    if (form) {
      form.addEventListener("submit", function (ev) {
        ev.preventDefault();
        var next = (searchInput && searchInput.value) || "";
        var url = new URL(window.location.href);
        if (next) url.searchParams.set("q", next);
        else url.searchParams.delete("q");
        history.replaceState(null, "", url.toString());
        loadIndex(function (data) { renderResults(data, next.trim()); });
      });
    }
  }

  /* —— Share controls ——
     Keep click handlers minimal. Event Timing on this long article showed
     presentation delay (next paint), not handler cost, dominates INP — so
     avoid any synchronous DOM writes in the click turn (incl. aria-live status). */
  function afterNextPaint(fn) {
    if (typeof requestAnimationFrame !== "function") {
      setTimeout(fn, 0);
      return;
    }
    requestAnimationFrame(function () {
      requestAnimationFrame(fn);
    });
  }

  function pushChroniclesEvent(name, params) {
    window.dataLayer = window.dataLayer || [];
    var payload = { event: name };
    if (params) {
      Object.keys(params).forEach(function (k) {
        if (params[k] != null && params[k] !== "") payload[k] = params[k];
      });
    }
    window.dataLayer.push(payload);
  }

  document.querySelectorAll(".chronicles-share-controls").forEach(function (root) {
    var url = root.getAttribute("data-share-url") || window.location.href;
    var title = root.getAttribute("data-share-title") || document.title;
    var status = root.parentElement && root.parentElement.querySelector(".chronicles-share-status");
    var articlePage = document.querySelector("[data-chronicles-page='article']");
    var articleSlug = articlePage ? (articlePage.getAttribute("data-article-slug") || "") : "";

    function setStatus(msg) {
      if (!status) return;
      afterNextPaint(function () {
        status.textContent = msg || "";
      });
    }

    function trackShare(method) {
      if (!articlePage) return;
      pushChroniclesEvent("chronicles_share", {
        article_slug: articleSlug,
        content_group: "chronicles",
        share_method: method
      });
    }

    var nativeBtn = root.querySelector("[data-share-native]");
    if (nativeBtn) {
      if (!navigator.share) {
        nativeBtn.hidden = true;
      } else {
        nativeBtn.addEventListener("click", function () {
          trackShare(nativeBtn.getAttribute("data-share-method") || "native");
          // Invoke share as the only sync work (preserves user activation).
          navigator.share({ title: title, url: url }).catch(function () {});
        });
      }
    }
    var copyBtn = root.querySelector("[data-share-copy]");
    if (copyBtn) {
      copyBtn.addEventListener("click", function () {
        trackShare(copyBtn.getAttribute("data-share-method") || "copy");
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(url).then(function () {
            setStatus("Link copied.");
          }).catch(function () {
            setStatus("Could not copy link.");
          });
        } else {
          setStatus("Copy not available in this browser.");
        }
      });
    }
    root.querySelectorAll("a[data-share-method]").forEach(function (a) {
      a.addEventListener("click", function () {
        trackShare(a.getAttribute("data-share-method") || "unknown");
      });
    });
  });

  /* —— Chronicles measurement (article pages only) ——
     Shared GA4/dataLayer foundation — see docs/chronicles/lonko-chronicles-ga4-foundation.md */
  (function initChroniclesMeasure() {
    var page = document.querySelector("[data-chronicles-page='article']");
    if (!page) return;

    var slug = page.getAttribute("data-article-slug") || "";
    function measure(name, params) {
      var base = {
        article_slug: slug,
        content_group: "chronicles"
      };
      if (params) {
        Object.keys(params).forEach(function (k) {
          base[k] = params[k];
        });
      }
      pushChroniclesEvent(name, base);
    }

    var thresholds = [25, 50, 75, 90];
    var fired = {};
    function scrollPercent() {
      var doc = document.documentElement;
      var body = document.body;
      var scrollTop = window.pageYOffset || doc.scrollTop || (body && body.scrollTop) || 0;
      var height =
        Math.max(doc.scrollHeight, (body && body.scrollHeight) || 0) - window.innerHeight;
      if (height <= 0) return 100;
      return Math.min(100, Math.round((scrollTop / height) * 100));
    }
    function checkScroll() {
      var pct = scrollPercent();
      thresholds.forEach(function (t) {
        if (pct >= t && !fired[t]) {
          fired[t] = true;
          measure("chronicles_scroll_depth", { scroll_percent: t });
        }
      });
    }
    window.addEventListener("scroll", checkScroll, { passive: true });
    checkScroll();

    document.querySelectorAll('a[data-chronicles-outbound="source"]').forEach(function (a) {
      a.addEventListener("click", function () {
        measure("chronicles_outbound_source_click", {
          link_url: a.href,
          link_text: (a.textContent || "").trim().slice(0, 120)
        });
      });
    });

    function isSameOrigin(href) {
      try {
        return new URL(href, window.location.href).origin === window.location.origin;
      } catch (err) {
        return false;
      }
    }

    document
      .querySelectorAll(".chronicles-article-body a[href], .chronicles-related a[href]")
      .forEach(function (a) {
        a.addEventListener("click", function () {
          if (!isSameOrigin(a.href)) return;
          measure("chronicles_internal_link_click", {
            link_url: a.href,
            link_text: (a.textContent || "").trim().slice(0, 120)
          });
        });
      });

    document.querySelectorAll("#site-nav a[href], a.brand[href]").forEach(function (a) {
      a.addEventListener("click", function () {
        var label = (a.textContent || "").trim();
        if (a.classList.contains("brand")) label = "Home";
        measure("chronicles_to_site_nav", {
          nav_label: label.slice(0, 60),
          link_url: a.href
        });
      });
    });
  })();
})();
"""


def write_chronicles_js() -> None:
    assets = OUT / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    (assets / "chronicles.js").write_text(CHRONICLES_JS, encoding="utf-8")


# —— Orchestration ——————————————————————————————————————————————————————


def build() -> int:
    CONTENT.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    articles = load_all_articles(CONTENT)
    if articles:
        errors = validate_articles(articles)
        visible = site_visible_articles(articles)
        renderable = renderable_articles(articles)
        errors.extend(validate_articles(visible, forbid_drafts=True))
        # Deduplicate while preserving order
        seen: set[str] = set()
        uniq: list[str] = []
        for e in errors:
            if e not in seen:
                seen.add(e)
                uniq.append(e)
        if uniq:
            print("Chronicles validation failed:", file=sys.stderr)
            for e in uniq:
                print(f"  - {e}", file=sys.stderr)
            return 1
    else:
        visible = []
        renderable = []
        print("Chronicles build: no article packages yet — emitting empty publication shell.")

    published = public_articles(articles)
    fixtures = fixture_articles(articles)
    retired = [a for a in articles if a.is_retired()]

    # Clean generated article dirs (keep content/, assets/, and local-only fixtures)
    for child in list(OUT.iterdir()):
        if child.name in {"content", "assets", "_local_fixtures"}:
            continue
        if child.is_dir():
            shutil.rmtree(child)
        elif child.name in {"feed.xml", "index.html"}:
            child.unlink(missing_ok=True)

    # Article pages: published + fixture + soft-retired (canonical URL preserved)
    for article in renderable:
        copy_package_assets(article)
        html = render_article_page(article, visible)
        dest = OUT / article.slug / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")

    # Latest/Featured/sections use listing-visible only (retired excluded)
    latest_all = sort_by_date(visible)
    total_pages = max(1, (len(latest_all) + PAGE_SIZE - 1) // PAGE_SIZE)

    # Sitemap pagination reflects indexable published corpus only (never fixture/retired)
    published_latest = sort_by_date(published)
    published_pages = (
        max(1, (len(published_latest) + PAGE_SIZE - 1) // PAGE_SIZE) if published else 1
    )

    page1 = latest_all[:PAGE_SIZE]
    (OUT / "index.html").write_text(
        render_index(visible, latest_page=page1, page_num=1, total_pages=total_pages, is_home=True),
        encoding="utf-8",
    )

    for n in range(2, total_pages + 1):
        chunk = latest_all[(n - 1) * PAGE_SIZE : n * PAGE_SIZE]
        page_dir = OUT / "page" / str(n)
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.html").write_text(
            render_index(visible, latest_page=chunk, page_num=n, total_pages=total_pages, is_home=False),
            encoding="utf-8",
        )

    search_dir = OUT / "search"
    search_dir.mkdir(parents=True, exist_ok=True)
    (search_dir / "index.html").write_text(render_search_page(), encoding="utf-8")

    write_rss(published)
    write_sitemaps(published, published_pages)
    write_search_indexes(visible)
    write_chronicles_js()
    write_robots([a.slug for a in fixtures])

    print(
        f"Chronicles build OK: {len(published)} published, {len(fixtures)} fixture, "
        f"{len(retired)} retired, {total_pages} latest page(s)."
    )
    return 0


def main() -> None:
    raise SystemExit(build())


if __name__ == "__main__":
    main()
