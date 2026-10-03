#!/usr/bin/env python3
"""Sync Google Tag Manager snippets from includes/ into all public HTML pages.

This static site has no shared layout engine. includes/gtm-*.html is the single
source of truth; this script keeps every page identical.

Usage (from lonko-digital-site/):
  python scripts/sync_gtm_snippets.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEAD_SNIPPET = (ROOT / "includes" / "gtm-head.html").read_text(encoding="utf-8").rstrip() + "\n"
BODY_SNIPPET = (ROOT / "includes" / "gtm-body.html").read_text(encoding="utf-8").rstrip() + "\n"

HEAD_MARK_START = "<!-- Google Tag Manager -->"
HEAD_MARK_END = "<!-- End Google Tag Manager -->"
BODY_MARK_START = "<!-- Google Tag Manager (noscript) -->"
BODY_MARK_END = "<!-- End Google Tag Manager (noscript) -->"

PAGES = [
    ROOT / "index.html",
    ROOT / "404.html",
    ROOT / "about" / "index.html",
    ROOT / "contact" / "index.html",
    ROOT / "privacy" / "index.html",
    ROOT / "terms" / "index.html",
    ROOT / "notes" / "confirmed" / "index.html",
]


def _replace_or_insert_head(html: str) -> str:
    if HEAD_MARK_START in html and HEAD_MARK_END in html:
        start = html.index(HEAD_MARK_START)
        end = html.index(HEAD_MARK_END) + len(HEAD_MARK_END)
        # consume trailing newline if present
        if end < len(html) and html[end] == "\n":
            end += 1
        return html[:start] + HEAD_SNIPPET + html[end:]

    # After charset + viewport when present; else immediately after <head>
    viewport = '<meta name="viewport" content="width=device-width, initial-scale=1">'
    if viewport in html:
        anchor = viewport
        idx = html.index(anchor) + len(anchor)
        if html[idx : idx + 1] == "\n":
            idx += 1
        return html[:idx] + HEAD_SNIPPET + html[idx:]

    head = "<head>"
    if head not in html:
        raise ValueError("No <head> found")
    idx = html.index(head) + len(head)
    if html[idx : idx + 1] == "\n":
        idx += 1
    return html[:idx] + HEAD_SNIPPET + html[idx:]


def _replace_or_insert_body(html: str) -> str:
    if BODY_MARK_START in html and BODY_MARK_END in html:
        start = html.index(BODY_MARK_START)
        end = html.index(BODY_MARK_END) + len(BODY_MARK_END)
        if end < len(html) and html[end] == "\n":
            end += 1
        return html[:start] + BODY_SNIPPET + html[end:]

    body = "<body>"
    if body not in html:
        raise ValueError("No <body> found")
    idx = html.index(body) + len(body)
    if html[idx : idx + 1] == "\n":
        idx += 1
    return html[:idx] + BODY_SNIPPET + html[idx:]


def main() -> int:
    for path in PAGES:
        original = path.read_text(encoding="utf-8")
        updated = _replace_or_insert_body(_replace_or_insert_head(original))
        if updated != original:
            path.write_text(updated, encoding="utf-8", newline="\n")
            print(f"updated {path.relative_to(ROOT)}")
        else:
            print(f"unchanged {path.relative_to(ROOT)}")

        # Exactly one head install + one body install. Body copy may mention the
        # container ID (e.g. Privacy), so do not count raw GTM-53DPJ88F occurrences.
        if updated.count(HEAD_MARK_START) != 1 or updated.count(BODY_MARK_START) != 1:
            raise SystemExit(f"{path}: expected exactly one GTM head and body install")
        if updated.count(HEAD_MARK_END) != 1 or updated.count(BODY_MARK_END) != 1:
            raise SystemExit(f"{path}: GTM install markers are mismatched")
        head_start = updated.index(HEAD_MARK_START)
        head_end = updated.index(HEAD_MARK_END) + len(HEAD_MARK_END)
        body_start = updated.index(BODY_MARK_START)
        body_end = updated.index(BODY_MARK_END) + len(BODY_MARK_END)
        if "GTM-53DPJ88F" not in updated[head_start:head_end]:
            raise SystemExit(f"{path}: GTM container missing from head install")
        if "GTM-53DPJ88F" not in updated[body_start:body_end]:
            raise SystemExit(f"{path}: GTM container missing from body install")
    print("OK — GTM-53DPJ88F synced to all public HTML pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
