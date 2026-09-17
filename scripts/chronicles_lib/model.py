"""Article data model and loaders for Lonko Chronicles."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

WORDS_PER_MINUTE = 220

CONTENT_TYPES = frozenset({"News", "Analysis", "Guide", "How-To", "Research"})
STATUSES = frozenset({"draft", "published", "retired", "fixture"})
SCHEMA_TYPES = frozenset({"Article", "BlogPosting", "NewsArticle"})
IMAGERY_FAMILIES = frozenset({"abstraction", "photography", "chart-diagram"})
PLACEMENT_SECTIONS = frozenset({"owners", "guides", "from_lonko"})

# Topic field values → pill label (Latest is "all", not a topic value)
TOPIC_PILL_MAP = {
    "ai & technology": "AI & Technology",
    "ai and technology": "AI & Technology",
    "ai": "AI & Technology",
    "technology": "AI & Technology",
    "marketing": "Marketing",
    "seo": "SEO",
    "growth": "Growth",
}

TOPIC_PILLS = (
    ("Latest", None),
    ("AI & Technology", "AI & Technology"),
    ("Marketing", "Marketing"),
    ("SEO", "SEO"),
    ("Growth", "Growth"),
)


def estimate_reading_time(markdown_body: str, wpm: int = WORDS_PER_MINUTE) -> int:
    """Estimate reading time in whole minutes from markdown word count (~220 wpm)."""
    text = re.sub(r"[`*_>#\-\[\]\(\)!|]", " ", markdown_body or "")
    words = re.findall(r"\w+", text)
    if not words:
        return 1
    return max(1, round(len(words) / wpm))


def normalize_topic(topic: str) -> str:
    """Map free-form topic strings onto pill labels when possible."""
    if not topic:
        return topic
    key = topic.strip().lower()
    return TOPIC_PILL_MAP.get(key, topic.strip())


@dataclass
class Article:
    title: str
    deck: str
    slug: str
    topic: str
    content_type: str
    status: str
    datePublished: str
    dateModified: str
    schema_type: str
    body: str = ""
    tags: list[str] = field(default_factory=list)
    author: str = "Lonko Digital"
    reading_time: int | None = None
    seo_title: str | None = None
    meta_description: str | None = None
    og_title: str | None = None
    og_description: str | None = None
    social_image: str | None = None
    hero_image: str | None = None
    hero_alt: str | None = None
    imagery_family: str | None = None
    hero_caption: str | None = None
    sources: list[dict[str, str]] = field(default_factory=list)
    placement: dict[str, Any] = field(default_factory=dict)
    related: list[str] = field(default_factory=list)
    is_fixture: bool = False
    package_dir: Path | None = None

    def __post_init__(self) -> None:
        if self.reading_time is None:
            self.reading_time = estimate_reading_time(self.body)
        explicit_fixture = self.is_fixture
        self.is_fixture = explicit_fixture or self.status == "fixture"
        if self.topic:
            self.topic = normalize_topic(self.topic)
        if not isinstance(self.tags, list):
            self.tags = list(self.tags) if self.tags else []
        if not isinstance(self.sources, list):
            self.sources = list(self.sources) if self.sources else []
        if not isinstance(self.related, list):
            self.related = list(self.related) if self.related else []
        if not isinstance(self.placement, dict):
            self.placement = dict(self.placement) if self.placement else {}
        self.placement.setdefault("featured", False)
        self.placement.setdefault("sections", [])

    @property
    def display_title(self) -> str:
        return self.seo_title or self.title

    @property
    def display_description(self) -> str:
        return self.meta_description or self.deck

    @property
    def display_og_title(self) -> str:
        return self.og_title or self.display_title

    @property
    def display_og_description(self) -> str:
        return self.og_description or self.display_description

    @property
    def sections(self) -> list[str]:
        raw = self.placement.get("sections") or []
        return [str(s) for s in raw]

    @property
    def featured_value(self) -> bool | int:
        return self.placement.get("featured", False)

    def featured_priority(self) -> int | None:
        """Return sort priority when featured is truthy; higher int wins. True → 1."""
        f = self.featured_value
        if f is True:
            return 1
        if isinstance(f, int) and f > 0:
            return f
        return None

    def is_site_visible(self) -> bool:
        """Published and fixture articles appear on the local/site UX."""
        return self.status in {"published", "fixture"}

    def is_indexable(self) -> bool:
        """Only truly published articles enter sitemap/feed/indexation."""
        return self.status == "published" and not self.is_fixture


def _parse_front_matter(raw: str) -> tuple[dict[str, Any], str]:
    text = raw.lstrip("\ufeff")
    if not text.startswith("---"):
        return {}, text
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, flags=re.DOTALL)
    if not match:
        # Allow closing --- at EOF with empty body
        match = re.match(r"^---\s*\n(.*?)\n---\s*$", text, flags=re.DOTALL)
        if not match:
            raise ValueError("Malformed YAML front matter (expected --- ... ---)")
        meta_raw, body = match.group(1), ""
    else:
        meta_raw, body = match.group(1), match.group(2)
    meta = yaml.safe_load(meta_raw) or {}
    if not isinstance(meta, dict):
        raise ValueError("Front matter must be a YAML mapping")
    return meta, body.strip("\n")


def load_article(package_dir: Path) -> Article:
    """Load one article package directory containing article.md."""
    package_dir = Path(package_dir)
    path = package_dir / "article.md"
    if not path.is_file():
        raise FileNotFoundError(f"Missing article.md in {package_dir}")
    raw = path.read_text(encoding="utf-8")
    meta, body = _parse_front_matter(raw)

    reading_time = meta.get("reading_time")
    if reading_time is None:
        reading_time = estimate_reading_time(body)
    else:
        reading_time = int(reading_time)

    is_fixture_meta = bool(meta.get("is_fixture", False))
    status = str(meta.get("status", "draft")).strip()

    article = Article(
        title=str(meta.get("title", "")).strip(),
        deck=str(meta.get("deck", "")).strip(),
        slug=str(meta.get("slug", "")).strip() or package_dir.name,
        topic=str(meta.get("topic", "")).strip(),
        tags=[str(t).strip() for t in (meta.get("tags") or []) if str(t).strip()],
        content_type=str(meta.get("content_type", "")).strip(),
        author=str(meta.get("author") or "Lonko Digital").strip(),
        reading_time=reading_time,
        status=status,
        datePublished=str(meta.get("datePublished", "")).strip(),
        dateModified=str(meta.get("dateModified", "")).strip(),
        schema_type=str(meta.get("schema_type", "")).strip(),
        seo_title=_opt_str(meta.get("seo_title")),
        meta_description=_opt_str(meta.get("meta_description")),
        og_title=_opt_str(meta.get("og_title")),
        og_description=_opt_str(meta.get("og_description")),
        social_image=_opt_str(meta.get("social_image")),
        hero_image=_opt_str(meta.get("hero_image")),
        hero_alt=_opt_str(meta.get("hero_alt")),
        imagery_family=_opt_str(meta.get("imagery_family")),
        hero_caption=_opt_str(meta.get("hero_caption")),
        sources=_normalize_sources(meta.get("sources") or []),
        placement=_normalize_placement(meta.get("placement") or {}),
        related=[str(s).strip() for s in (meta.get("related") or []) if str(s).strip()],
        is_fixture=is_fixture_meta,
        body=body,
        package_dir=package_dir.resolve(),
    )
    return article


def _opt_str(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    return s or None


def _normalize_sources(raw: Any) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    if not raw:
        return out
    for item in raw:
        if isinstance(item, dict):
            out.append(
                {
                    "url": str(item.get("url", "")).strip(),
                    "description": str(item.get("description", "")).strip(),
                }
            )
        else:
            out.append({"url": "", "description": str(item)})
    return out


def _normalize_placement(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {"featured": False, "sections": []}
    featured = raw.get("featured", False)
    sections = raw.get("sections") or []
    if not isinstance(sections, list):
        sections = [sections]
    return {
        "featured": featured,
        "sections": [str(s).strip() for s in sections if str(s).strip()],
    }


def load_all_articles(content_root: Path) -> list[Article]:
    """Load every article package under content_root (each subdir with article.md)."""
    content_root = Path(content_root)
    if not content_root.is_dir():
        return []
    articles: list[Article] = []
    for child in sorted(content_root.iterdir()):
        if not child.is_dir():
            continue
        if not (child / "article.md").is_file():
            continue
        articles.append(load_article(child))
    return articles


def public_articles(articles: list[Article]) -> list[Article]:
    """Truly published, indexable articles (excludes fixtures and drafts)."""
    return [a for a in articles if a.is_indexable()]


def fixture_articles(articles: list[Article]) -> list[Article]:
    """Fixture articles (local UX, noindex, excluded from sitemap/feed)."""
    return [a for a in articles if a.is_fixture or a.status == "fixture"]


def site_visible_articles(articles: list[Article]) -> list[Article]:
    """Articles rendered on the site UX: published + fixture."""
    return [a for a in articles if a.is_site_visible()]


def sort_by_date(articles: list[Article], *, reverse: bool = True) -> list[Article]:
    return sorted(articles, key=lambda a: (a.datePublished, a.slug), reverse=reverse)
