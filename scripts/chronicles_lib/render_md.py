"""Markdown → HTML conversion for Chronicles article bodies."""

from __future__ import annotations

import html
import re

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


def strip_word_count_leaks(text: str) -> str:
    """Remove public-facing word-count metadata lines from markdown or HTML."""
    if not text:
        return ""
    cleaned = _WORD_COUNT_LEAK_MD_RE.sub("", text)
    cleaned = _WORD_COUNT_LEAK_HTML_RE.sub("", cleaned)
    return cleaned


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
    """Convert article markdown body to HTML with Chronicles custom blocks."""
    if not text:
        return ""
    prepared = strip_word_count_leaks(preprocess_containers(text))
    _MD.reset()
    return strip_word_count_leaks(_MD.convert(prepared))


def escape_text(value: str) -> str:
    return html.escape(value or "", quote=True)
