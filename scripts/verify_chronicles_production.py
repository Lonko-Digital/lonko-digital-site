#!/usr/bin/env python3
"""Check a live Chronicles article URL and write an evidence record.

PASS means every required check in this script passed.
FAIL means one or more of those checks failed.
The record does not instruct any reader how to reconcile other observations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://lonkodigital.com"
ORG_ID = "https://lonkodigital.com/#organization"
GTM_ID = "GTM-53DPJ88F"
SITEMAP = f"{SITE}/sitemap-chronicles.xml"

USER_AGENTS = (
    "LonkoChroniclesVerifier/1.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
)

HYGIENE = (
    re.compile(r"(?i)\(\s*~\s*[\d,]+\s*words?\s*\)"),
    re.compile(r"(?i)\b(?:WORKING\s+NOTE|INTERNAL\s+NOTE)\b"),
    re.compile(r"(?m)^\s*(?:TODO|FIXME)\b"),
    re.compile(r"(?i)\b(?:DRAFT\s+ONLY|DO\s+NOT\s+PUBLISH|PRODUCTION\s+NOTE|PRE-PUBLICATION PREVIEW)\b"),
)


class _Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.h1: list[str] = []
        self._in_h1 = False
        self._h1_buf: list[str] = []
        self.canonical = ""
        self.robots = ""
        self.og: dict[str, str] = {}
        self.imgs: list[str] = []
        self.hero_src = ""
        self._in_hero = False
        self.jsonld: list[object] = []
        self._in_jsonld = False
        self._jsonld_buf: list[str] = []
        self.sources_headings = 0
        self._in_sources_heading = False
        self.attrs_ok = False
        self.slug_attr = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        ad = {k.lower(): (v or "") for k, v in attrs}
        if tag == "h1":
            self._in_h1 = True
            self._h1_buf = []
        if tag == "link" and ad.get("rel") == "canonical":
            self.canonical = ad.get("href", "")
        if tag == "meta":
            name = (ad.get("name") or ad.get("property") or "").lower()
            if name == "robots":
                self.robots = ad.get("content", "")
            if name.startswith("og:"):
                self.og[name] = ad.get("content", "")
        if tag == "img":
            src = ad.get("src", "")
            self.imgs.append(src)
            if self._in_hero and not self.hero_src:
                self.hero_src = src
        if tag == "figure" and "chronicles-hero-figure" in ad.get("class", ""):
            self._in_hero = True
        if tag == "script" and "ld+json" in ad.get("type", ""):
            self._in_jsonld = True
            self._jsonld_buf = []
        if tag == "main" and ad.get("data-chronicles-page") == "article":
            self.attrs_ok = True
            self.slug_attr = ad.get("data-article-slug", "")
        if tag in {"h2", "h3"}:
            self._in_sources_heading = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "h1" and self._in_h1:
            self.h1.append("".join(self._h1_buf).strip())
            self._in_h1 = False
        if tag == "figure":
            self._in_hero = False
        if tag == "script" and self._in_jsonld:
            raw = "".join(self._jsonld_buf).strip()
            self._in_jsonld = False
            try:
                self.jsonld.append(json.loads(raw))
            except json.JSONDecodeError:
                self.jsonld.append({"_parse_error": True})
        if tag in {"h2", "h3"}:
            self._in_sources_heading = False

    def handle_data(self, data: str) -> None:
        if self._in_h1:
            self._h1_buf.append(data)
        if self._in_jsonld:
            self._jsonld_buf.append(data)
        if self._in_sources_heading and re.search(r"sources", data, re.I):
            self.sources_headings += 1


_HEADER_KEYS = ("content-type", "cache-control", "server", "x-cache", "age", "via")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def _selected_headers(headers: dict[str, str]) -> dict[str, str]:
    return {key: headers[key] for key in _HEADER_KEYS if headers.get(key)}


def _fetch(url: str, ua: str, timeout: int = 30) -> tuple[int, str, str, dict[str, str]]:
    sep = "&" if "?" in url else "?"
    bust = f"{url}{sep}_verify={int(time.time())}"
    req = urllib.request.Request(bust, headers={"User-Agent": ua, "Accept": "text/html,application/xml,image/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            headers = {k.lower(): v for k, v in resp.headers.items()}
            return resp.status, resp.geturl().split("?")[0], raw.decode("utf-8", errors="replace"), headers
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        headers = {k.lower(): v for k, v in exc.headers.items()} if exc.headers else {}
        final = getattr(exc, "url", url) or url
        return exc.code, str(final).split("?")[0], raw.decode("utf-8", errors="replace"), headers


def _fetch_with_retry(url: str, attempts: int = 4, pause: float = 12.0) -> dict:
    last: dict = {}
    for i in range(1, attempts + 1):
        per_ua = []
        chosen: dict | None = None
        for ua in USER_AGENTS:
            status, final, body, headers = _fetch(url, ua)
            per_ua.append(
                {
                    "user_agent": ua,
                    "http_status": status,
                    "final_url": final,
                    "bytes": len(body.encode("utf-8", errors="replace")),
                    "body_sha256": _sha256(body),
                    "headers": _selected_headers(headers),
                }
            )
            if chosen is None and status == 200 and body:
                chosen = {"http_status": status, "final_url": final, "body": body}
        if chosen is not None:
            return {**chosen, "attempts": per_ua, "attempt": i}
        last = {"http_status": None, "final_url": url, "body": "", "attempts": per_ua, "attempt": i}
        if i < attempts:
            time.sleep(pause)
    return last


def _absolute(src: str, page_url: str) -> str:
    if src.startswith("http://") or src.startswith("https://"):
        return src
    return urljoin(page_url, src)


def _asset_check(src: str, page_url: str) -> dict:
    absolute = _absolute(src, page_url)
    status, final, _, headers = _fetch(absolute, USER_AGENTS[1])
    ctype = headers.get("content-type", "")
    ok = status == 200 and "image/" in ctype
    return {
        "url": absolute,
        "final_url": final,
        "http_status": status,
        "content_type": ctype,
        "pass": ok,
    }


def _git_file_sha(path: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "log", "-1", "--format=%H", "--", path],
            cwd=ROOT,
            text=True,
        ).strip()
    except Exception:
        return ""


def _expected_title(slug: str, explicit: str) -> str:
    if explicit:
        return explicit
    path = ROOT / "chronicles" / "content" / slug / "article.md"
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    match = re.search(r'(?m)^title:\s*"?([^"\n]+)"?\s*$', text)
    return match.group(1).strip().strip('"') if match else ""


def _commit_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return ""


def verify(slug: str, title: str = "") -> dict:
    expected = _expected_title(slug, title)
    url = f"{SITE}/chronicles/{slug}/"
    fetched = _fetch_with_retry(url)
    body = fetched.get("body") or ""
    page = _Page()
    if body:
        page.feed(body)

    h1_pass = bool(expected) and any(expected in h for h in page.h1)
    slug_pass = page.slug_attr == slug
    canonical_pass = page.canonical.rstrip("/") == url.rstrip("/")
    robots = page.robots.lower()
    indexable_pass = "noindex" not in robots and "nofollow" not in robots and "noindex" not in body.lower()[:4000]
    # noindex must not appear as a robots directive. Searching the whole body can
    # false-fail if the article discusses noindex. Check the robots meta only,
    # plus the head snippet before <body>.
    head = body.split("<body", 1)[0].lower() if body else ""
    indexable_pass = "noindex" not in head and "nofollow" not in head
    preview_hygiene_pass = "pre-publication preview" not in body.lower() and "chronicles-preview-notice" not in body
    hygiene_hits = [p.pattern for p in HYGIENE if p.search(body)]
    # PRE-PUBLICATION is already in preview_hygiene; don't double-count that pattern inside content_hygiene
    content_hygiene_pass = not any(
        p.search(body) for p in HYGIENE if "PRE-PUBLICATION" not in p.pattern
    )

    schema_pass = False
    breadcrumb_pass = False
    for block in page.jsonld:
        if not isinstance(block, dict):
            continue
        kind = block.get("@type")
        if kind in {"Article", "BlogPosting", "NewsArticle"}:
            headline_ok = expected in str(block.get("headline", ""))
            author = block.get("author") or {}
            publisher = block.get("publisher") or {}
            org_ok = ORG_ID in json.dumps(author) and (
                publisher.get("@id") == ORG_ID or ORG_ID in json.dumps(publisher)
            )
            schema_pass = headline_ok and org_ok
        if kind == "BreadcrumbList":
            names = [str(i.get("name", "")) for i in block.get("itemListElement") or [] if isinstance(i, dict)]
            breadcrumb_pass = names[:2] == ["Home", "Chronicles"] and (not expected or expected in names)

    hero_src = page.hero_src
    hero = _asset_check(hero_src, url) if hero_src else {
        "url": "",
        "final_url": "",
        "http_status": None,
        "content_type": "",
        "pass": False,
    }
    hero_pass = bool(hero["pass"])
    supporting = []
    for src in page.imgs:
        if not src or src == hero_src:
            continue
        if "lonko-logo" in src or "favicon" in src:
            continue
        if src.startswith("../../assets/"):
            continue
        supporting.append(_asset_check(src, url))
    supporting_pass = all(item["pass"] for item in supporting) if supporting else True

    og_title = page.og.get("og:title", "")
    og_desc = page.og.get("og:description", "")
    og_image = page.og.get("og:image", "")
    og_metadata_pass = bool(og_title and og_desc and og_image)
    og_image_result = _asset_check(og_image, url) if og_image else {
        "url": "",
        "final_url": "",
        "http_status": None,
        "content_type": "",
        "pass": False,
    }
    og_image_pass = bool(og_image_result["pass"])

    sm_status, _, sm_body, _ = _fetch(SITEMAP, USER_AGENTS[0])
    sitemap_pass = sm_status == 200 and url in sm_body

    sources_pass = page.sources_headings == 1
    tracking_pass = GTM_ID in body and page.attrs_ok and slug_pass

    checks = {
        "h1_pass": h1_pass,
        "canonical_pass": canonical_pass,
        "indexable_pass": indexable_pass,
        "preview_hygiene_pass": preview_hygiene_pass,
        "schema_pass": schema_pass,
        "breadcrumb_schema_pass": breadcrumb_pass,
        "hero_pass": hero_pass,
        "supporting_assets_pass": supporting_pass,
        "og_metadata_pass": og_metadata_pass,
        "og_image_pass": og_image_pass,
        "sitemap_pass": sitemap_pass,
        "content_hygiene_pass": content_hygiene_pass and sources_pass,
        "tracking_foundation_pass": tracking_pass,
    }
    overall = "PASS" if all(checks.values()) and fetched.get("http_status") == 200 else "FAIL"
    result = {
        "slug": slug,
        "url": url,
        "expected_title": expected,
        "observed_h1": page.h1,
        "verified_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "github_actions_run_id": os.environ.get("GITHUB_RUN_ID", ""),
        "production_commit": os.environ.get("GITHUB_SHA") or _commit_sha(),
        "verifier_script_commit": _git_file_sha("scripts/verify_chronicles_production.py"),
        "workflow_commit": _git_file_sha(".github/workflows/chronicles-production-verify.yml"),
        "http_status": fetched.get("http_status"),
        "final_url": fetched.get("final_url", ""),
        "response_bytes": len(body.encode("utf-8", errors="replace")),
        "response_body_sha256": _sha256(body),
        "fetch_attempt": fetched.get("attempt"),
        "fetch_attempts": fetched.get("attempts", []),
        "hero": hero,
        "supporting_assets": supporting,
        "og_image": og_image_result,
        "sitemap_url": SITEMAP,
        "sources_heading_count": page.sources_headings,
        "hygiene_hits": hygiene_hits,
        "checks_performed": list(checks.keys()),
        "overall_definition": (
            "PASS means every required automated test in this verifier passed. "
            "FAIL means one or more of those tests failed. "
            "The result is scoped to the checks listed in checks_performed."
        ),
        **checks,
        "overall": overall,
    }
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--title", default="")
    ap.add_argument("--output", default="")
    args = ap.parse_args()
    result = verify(args.slug, args.title)
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        dest = Path(args.output)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if result["overall"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
