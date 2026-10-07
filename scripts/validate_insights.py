#!/usr/bin/env python3
"""Read-only Insight metadata, sitemap, semantic HTML, and local-path checks.

Usage: python -B scripts/validate_insights.py [--pending-publication SLUG]
Pending publication is explicit: that article must omit both dates and lastmod.
Without the flag, every article must have ISO publication/modification dates.
Uses only the Python standard library; never generates or publishes content.
"""
from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://lonkodigital.com"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class Page(HTMLParser):
    def __init__(self, text: str):
        super().__init__(convert_charrefs=True)
        self.root = ET.Element("document")
        self.stack = [self.root]
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        node = ET.SubElement(self.stack[-1], tag, {k: v or "" for k, v in attrs})
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        node = self.stack[-1]
        if len(node):
            node[-1].tail = (node[-1].tail or "") + data
        else:
            node.text = (node.text or "") + data


def text(node):
    return " ".join("".join(node.itertext()).split()) if node is not None else ""


def validate(root: Path, pending: str | None = None) -> list[str]:
    errors = []
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap = ET.parse(root / "sitemap-pages.xml")
    entries = {n.findtext("s:loc", namespaces=ns): n for n in sitemap.findall("s:url", ns)}
    articles = sorted((root / "insights").glob("*/index.html"))
    if pending and pending not in {p.parent.name for p in articles}:
        errors.append("pending publication slug does not exist")
    for path in [root / "insights/index.html", *articles]:
        prefix = str(path.relative_to(root))
        page = Page(path.read_text(encoding="utf-8")).root
        def check(ok, message):
            if not ok:
                errors.append(f"{prefix}: {message}")
        canonical_node = page.find(".//link[@rel='canonical']")
        canonical = canonical_node.get("href", "") if canonical_node is not None else ""
        expected = SITE + "/" + path.parent.relative_to(root).as_posix() + "/"
        check(canonical == expected, "canonical does not match route")
        check(canonical in entries, "canonical absent from pages sitemap")
        check(len(page.findall(".//h1")) == 1, "must have exactly one H1")
        metas = {n.get("name") or n.get("property"): n.get("content") for n in page.findall(".//meta")}
        for key in ["description", "og:title", "og:description", "og:image", "twitter:title", "twitter:description", "twitter:image"]:
            check(bool(metas.get(key)), f"missing {key}")
        check(metas.get("og:url") == canonical, "og:url differs from canonical")
        schemas = []
        for node in page.findall(".//script[@type='application/ld+json']"):
            try:
                schemas.append(json.loads("".join(node.itertext())))
            except ValueError:
                check(False, "invalid JSON-LD")
        for node in page.iter():
            attr = "src" if node.tag in {"img", "script"} else "href"
            href = node.get(attr)
            if not href or node.tag not in {"a", "img", "script", "link", "source"}:
                continue
            url = urlsplit(href)
            if url.scheme or url.netloc or not url.path:
                continue
            target = root / unquote(url.path.lstrip("/")) if url.path.startswith("/") else path.parent / unquote(url.path)
            check(target.exists(), f"missing local path {url.path}")
            if target.is_dir():
                check((target / "index.html").is_file(), f"directory link has no index {url.path}")
        if path.parent == root / "insights":
            continue
        article = next((s for s in schemas if s.get("@type") == "Article"), {})
        breadcrumb = next((s for s in schemas if s.get("@type") == "BreadcrumbList"), {})
        check(bool(article) and bool(breadcrumb), "Article and BreadcrumbList required")
        check(article.get("headline") == text(page.find(".//h1")), "schema headline differs from H1")
        check(article.get("mainEntityOfPage") == canonical, "schema mainEntityOfPage differs")
        check(article.get("image") == metas.get("og:image") == metas.get("twitter:image"), "social/schema images differ")
        check(article.get("inLanguage") == "en-US", "schema language differs")
        check(article.get("isPartOf") == {"@id": SITE + "/#website"}, "schema website entity differs")
        for role in ["author", "publisher"]:
            check(article.get(role, {}).get("@id") == SITE + "/#organization", f"{role} organization entity differs")
        items = breadcrumb.get("itemListElement", [])
        check([i.get("position") for i in items] == [1, 2, 3], "breadcrumb positions differ")
        check([i.get("item") for i in items] == [SITE + "/", SITE + "/insights/", canonical], "breadcrumb URLs differ")
        if path.parent.name == pending:
            check("datePublished" not in article and "dateModified" not in article, "pending article must omit publication dates")
            check(entries.get(canonical) is not None and entries[canonical].find("s:lastmod", ns) is None, "pending article must omit lastmod")
        else:
            for key in ["datePublished", "dateModified"]:
                check(bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:T.*)?", str(article.get(key, "")))), f"missing/invalid {key}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pending-publication", metavar="SLUG")
    args = parser.parse_args()
    errors = validate(ROOT, args.pending_publication)
    for error in errors:
        print(error)
    print(f"INSIGHTS VALIDATION: {'FAIL' if errors else 'PASS'} ({len(errors)} findings)")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
