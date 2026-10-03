#!/usr/bin/env python3
"""Regression: /notes/confirmed/ must stay noindex, unlisted, and directly reachable.

Protects the Brevo DOI landing page from accidental search indexing or
normal site discovery. Does not change page experience.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from public_safety_audit import (  # noqa: E402
    NOTES_CONFIRMED_HREF,
    NOTES_CONFIRMED_ROBOTS_DISALLOW,
    collect_notes_confirmed_indexing_findings,
)

# Explicit discovery href variants that must be caught.
DISCOVERY_HREF_CASES = (
    'href="/notes/confirmed/"',
    'href="/notes/confirmed/?utm_source=test"',
    'href="/notes/confirmed?foo=bar"',
    'href="/notes/confirmed/#test"',
    'href="/notes/confirmed#section"',
    'href="../notes/confirmed/"',
    'href="https://lonkodigital.com/notes/confirmed/?utm_source=test"',
)

# Plain text must not trip the href matcher.
NON_HREF_MENTIONS = (
    "Visit notes/confirmed/ after DOI.",
    "The path /notes/confirmed/?utm_source=test is email-only.",
)

ROBOTS_DISALLOW_CASES = (
    "Disallow: /notes/confirmed",
    "Disallow: /notes/confirmed/",
    "Disallow: /notes/confirmed/*",
    "Disallow: /notes/confirmed*",
    "  disallow: /notes/confirmed/  ",
)


def _rel(root: Path, finding: str) -> str:
    return finding.replace(str(root) + "/", "").replace(str(root) + chr(92), "")


def _write_minimal_page(root: Path) -> None:
    page = root / "notes" / "confirmed" / "index.html"
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(
        "<!DOCTYPE html><html><head>"
        '<meta name="robots" content="noindex, nofollow">'
        '<link rel="canonical" href="https://lonkodigital.com/notes/confirmed/">'
        "</head><body></body></html>",
        encoding="utf-8",
    )


def run_negative_fixtures() -> list[str]:
    """Prove query/fragment hrefs and robots Disallow variants fail closed."""
    failures: list[str] = []

    for case in DISCOVERY_HREF_CASES:
        if not NOTES_CONFIRMED_HREF.search(case):
            failures.append(f"href matcher missed: {case}")

    for case in NON_HREF_MENTIONS:
        if NOTES_CONFIRMED_HREF.search(case):
            failures.append(f"href matcher false-positive on non-href text: {case!r}")

    for case in ROBOTS_DISALLOW_CASES:
        if not NOTES_CONFIRMED_ROBOTS_DISALLOW.search(case):
            failures.append(f"robots matcher missed: {case!r}")

    root = Path(tempfile.mkdtemp(prefix="notes-idx-neg-"))
    try:
        _write_minimal_page(root)
        (root / "robots.txt").write_text(
            "User-agent: *\nAllow: /\nDisallow: /notes/confirmed/*\n",
            encoding="utf-8",
        )
        (root / "index.html").write_text(
            '<a href="/notes/confirmed/?utm_source=test">Confirmed</a>\n'
            '<a href="/notes/confirmed#section">Fragment</a>\n',
            encoding="utf-8",
        )
        findings = collect_notes_confirmed_indexing_findings(root)
        joined = "\n".join(findings)
        if "discovery" not in joined:
            failures.append("fixture missing discovery findings for query/fragment hrefs")
        if "Disallow" not in joined:
            failures.append("fixture missing robots Disallow finding for /* variant")
        if len([f for f in findings if "discovery" in f]) < 2:
            failures.append("fixture expected at least two discovery findings")
    finally:
        shutil.rmtree(root, ignore_errors=True)

    return failures


def main() -> int:
    findings = collect_notes_confirmed_indexing_findings(ROOT)
    print("Notes confirmed indexing regression — /notes/confirmed/")
    if findings:
        print(f"FAIL — {len(findings)} finding(s):\n")
        for item in findings:
            print(f"  • {_rel(ROOT, item)}")
        return 1

    print(
        "PASS — noindex + self-canonical + unlisted in sitemaps + "
        "not in discovery nav + robots.txt remains crawlable + page present."
    )

    neg = run_negative_fixtures()
    print("Notes confirmed indexing negative fixtures")
    if neg:
        print(f"FAIL — {len(neg)} negative fixture issue(s):\n")
        for item in neg:
            print(f"  • {item}")
        return 1

    print(
        "PASS — query/fragment href variants and robots Disallow wildcards fail closed; "
        "non-href path mentions ignored."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
