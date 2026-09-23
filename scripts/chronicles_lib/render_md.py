"""Markdown → HTML conversion for Chronicles article bodies."""

from __future__ import annotations

import html
import re
from urllib.parse import urlparse

import markdown

# nl2br is intentionally OFF — authors control breaks via markdown.
_MD = markdown.Markdown(
    extensions=[
        "markdown.extensions.tables",
        "markdown.extensions.fenced_code",
        "markdown.extensions.toc",
        "markdown.extensions.sane_lists",
    ],
    output_format="html5",
)

_CONTAINER_RE = re.compile(
    r":::[\t ]*(pullquote|callout)[\t ]*\n(.*?)(?:\n)?:::[\t ]*(?:\n|$)",
    re.DOTALL | re.IGNORECASE,
)

# Internal editorial word-count notes sometimes leak into package bodies
# (e.g. "*(~1,150 words)*"). Never render those publicly.
_WORD_COUNT_LEAK_MD_RE = re.compile(
    r"(?m)^\s*(?:\*|_){0,2}\(\s*~\s*[\d,]+\s*words?\s*\)(?:\*|_){0,2}\s*$"
)
_WORD_COUNT_LEAK_HTML_RE = re.compile(
    r"<p>\s*(?:<em>)?\s*\(\s*~\s*[\d,]+\s*words?\s*\)\s*(?:</em>)?\s*</p>\s*",
    re.IGNORECASE,
)

_A_TAG_RE = re.compile(r"<a\s+([^>]*?)>", re.IGNORECASE)
_HREF_RE = re.compile(r"""href\s*=\s*["']([^"']+)["']""", re.IGNORECASE)
_SITE_HOSTS = frozenset({"lonkodigital.com", "www.lonkodigital.com"})


def strip_word_count_leaks(text: str) -> str:
    """Remove public-facing word-count metadata lines from markdown or HTML."""
    if not text:
        return ""
    cleaned = _WORD_COUNT_LEAK_MD_RE.sub("", text)
    cleaned = _WORD_COUNT_LEAK_HTML_RE.sub("", cleaned)
    return cleaned


def _is_external_href(href: str) -> bool:
    """True for absolute http(s) links that leave lonkodigital.com."""
    if not href:
        return False
    raw = href.strip()
    if not raw or raw.startswith(("#", "/", "./", "../", "mailto:", "tel:", "sms:")):
        return False
    if not (raw.startswith("http://") or raw.startswith("https://")):
        return False
    host = (urlparse(raw).hostname or "").lower()
    return bool(host) and host not in _SITE_HOSTS


def ensure_outbound_new_tab(html_text: str) -> str:
    """Force external http(s) anchors to open in a new tab with safe rel."""

    def repl(match: re.Match[str]) -> str:
        attrs = match.group(1)
        href_m = _HREF_RE.search(attrs)
        if not href_m or not _is_external_href(href_m.group(1)):
            return match.group(0)
        if not re.search(r"\btarget\s*=", attrs, flags=re.IGNORECASE):
            attrs += ' target="_blank"'
        rel_m = re.search(r"""\brel\s*=\s*["']([^"']*)["']""", attrs, flags=re.IGNORECASE)
        if rel_m:
            parts = {p.lower() for p in rel_m.group(1).split() if p}
            parts.update({"noopener", "noreferrer"})
            new_rel = " ".join(sorted(parts))
            attrs = attrs[: rel_m.start()] + f'rel="{new_rel}"' + attrs[rel_m.end() :]
        else:
            attrs += ' rel="noopener noreferrer"'
        return f"<a {attrs}>"

    return _A_TAG_RE.sub(repl, html_text)


def _render_container(kind: str, inner_md: str) -> str:
    _MD.reset()
    inner_html = _MD.convert(inner_md.strip())
    if kind.lower() == "pullquote":
        return f'<blockquote class="chronicles-pullquote">{inner_html}</blockquote>\n'
    return f'<aside class="chronicles-callout">{inner_html}</aside>\n'


def preprocess_containers(text: str) -> str:
    """Replace ::: pullquote / ::: callout fences with HTML placeholders.

    Uses a simple pre-pass so the stock markdown package does not need
    a container extension.
    """

    def repl(match: re.Match[str]) -> str:
        kind = match.group(1).lower()
        inner = match.group(2)
        return _render_container(kind, inner)

    return _CONTAINER_RE.sub(repl, text)


def markdown_to_html(text: str) -> str:
    """Convert article markdown body to HTML with Chronicles custom blocks.

    Does not silently rewrite editorial copy. Non-public artifacts must fail
    validation (see validate.py) rather than being stripped at render time.
    """
    if not text:
        return ""
    prepared = preprocess_containers(text)
    _MD.reset()
    return ensure_outbound_new_tab(_MD.convert(prepared))


def escape_text(value: str) -> str:
    return html.escape(value or "", quote=True)
