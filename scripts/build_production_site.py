#!/usr/bin/env python3
"""Write a production copy of the public pages with preview-only regions removed.

GitHub Pages publishes the files in this repository directly. The homepage and
About preview keep fenced preview-only blocks so founder review can see the
preview banner. Those blocks are not part of the production release.

    python scripts/build_production_site.py --out build/production

This writes the production pages and stylesheet. It does not deploy, merge, or
modify the source files used for the preview.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PREVIEW_SOURCES = (
    Path("index.html"),
    Path("about/index.html"),
    Path("assets/css/site.css"),
)

HTML_PREVIEW_BLOCK = re.compile(
    r"[ \t]*<!-- preview-only:start -->.*?<!-- preview-only:end -->\r?\n?",
    re.DOTALL,
)
CSS_PREVIEW_BLOCK = re.compile(
    r"[ \t]*/\* preview-only:start \*/.*?/\* preview-only:end \*/\r?\n?",
    re.DOTALL,
)

FORBIDDEN_IN_PRODUCTION = (
    "preview-only:",
    "preview-banner",
    "For founder review only",
)


def strip_preview(text: str, suffix: str) -> str:
    pattern = CSS_PREVIEW_BLOCK if suffix == ".css" else HTML_PREVIEW_BLOCK
    stripped, count = pattern.subn("", text)
    if count != 1:
        raise ValueError(f"expected exactly one preview-only block, found {count}")
    return stripped


def build(out_dir: Path) -> list[Path]:
    written: list[Path] = []
    for relative in PREVIEW_SOURCES:
        source = ROOT / relative
        text = source.read_text(encoding="utf-8")
        production = strip_preview(text, relative.suffix)
        for phrase in FORBIDDEN_IN_PRODUCTION:
            if phrase in production:
                raise ValueError(f"{relative} production copy still contains {phrase!r}")
        destination = out_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(production, encoding="utf-8", newline="\n")
        written.append(destination)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "build" / "production",
        help="Directory for the production pages (not deployed)",
    )
    args = parser.parse_args(argv)
    written = build(args.out)
    print("Production build contains no preview banner code.")
    for path in written:
        print(f"  {path}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValueError as exc:
        print(f"FAIL — {exc}", file=sys.stderr)
        sys.exit(1)
