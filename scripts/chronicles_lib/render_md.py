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
    prepared = preprocess_containers(text)
    _MD.reset()
    return _MD.convert(prepared)


def escape_text(value: str) -> str:
    return html.escape(value or "", quote=True)
