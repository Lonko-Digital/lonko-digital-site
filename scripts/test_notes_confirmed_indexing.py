#!/usr/bin/env python3
"""Regression: /notes/confirmed/ must stay noindex, unlisted, and directly reachable.

Protects the Brevo DOI landing page from accidental search indexing or
normal site discovery. Does not change page experience.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from public_safety_audit import collect_notes_confirmed_indexing_findings  # noqa: E402


def main() -> int:
    findings = collect_notes_confirmed_indexing_findings(ROOT)
    print("Notes confirmed indexing regression — /notes/confirmed/")
    if findings:
        print(f"FAIL — {len(findings)} finding(s):\n")
        for item in findings:
            # Prefer repo-relative paths in focused test output.
            print(f"  • {item.replace(str(ROOT) + '/', '').replace(str(ROOT) + chr(92), '')}")
        return 1

    print(
        "PASS — noindex + self-canonical + unlisted in sitemaps + "
        "not in discovery nav + robots.txt remains crawlable + page present."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
