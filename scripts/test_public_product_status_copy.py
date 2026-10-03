#!/usr/bin/env python3
"""Regression: Home/About must not use brittle Google Ads countdown copy.

Fails if public product-status wording on index.html or about/index.html
still claims a one-final-check / internal-testing-complete countdown.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TARGETS = (
    ROOT / "index.html",
    ROOT / "about" / "index.html",
)

BRITTLE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("one final live-account check", re.compile(r"one final live-account check", re.I)),
    ("final live-account", re.compile(r"final live-account", re.I)),
    ("internal testing complete", re.compile(r"internal testing complete", re.I)),
]


def main() -> int:
    findings: list[str] = []
    for path in TARGETS:
        if not path.is_file():
            findings.append(f"{path.relative_to(ROOT)}: missing")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in BRITTLE_PATTERNS:
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                findings.append(
                    f"{path.relative_to(ROOT)}:{line_no}: brittle product-status phrase [{label}]"
                )

    print("Public product-status copy regression — Home/About")
    if findings:
        print(f"FAIL — {len(findings)} finding(s):\n")
        for item in findings:
            print(f"  • {item}")
        return 1

    print("PASS — no brittle Google Ads countdown language on Home/About.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
