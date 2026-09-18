#!/usr/bin/env python3
"""Build a synthetic Drive package for the real cloud smoke test.

Writes to bridge/smoke-package/<slug>/ — upload that folder into Drive Inbox.

  python scripts/build_bridge_smoke_package.py
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

from chronicles_bridge.testdata import build_package  # noqa: E402

SLUG = "bridge-cloud-smoke-synthetic-signal"


def main() -> int:
    out = ROOT / "bridge" / "smoke-package"
    out.mkdir(parents=True, exist_ok=True)
    pkg = build_package(
        out,
        slug=SLUG,
        package_id="01SMOKECLOUD000000000000000",
        producer="cursor-web-smoke",
        meta={
            "title": "Bridge Cloud Smoke — Synthetic Signal (Do Not Publish)",
            "deck": "Synthetic package for Drive → Actions → PR verification. Close the PR without merging.",
            "status": "published",
            "datePublished": "2026-09-18",
            "dateModified": "2026-09-18",
            "schema_type": "Article",
            "content_type": "News",
            "topic": "Marketing",
            "placement": {"featured": False, "sections": []},
            "tags": ["smoke-test", "do-not-publish"],
        },
        body=(
            "## Smoke test only\n\n"
            "This article exists solely to verify the Chronicles Drive publishing bridge.\n\n"
            "Do **not** merge the ingest PR to production. Close/delete after verification.\n"
        ),
    )
    print(f"Smoke package ready: {pkg}")
    print("Upload this entire folder into Google Drive > Lonko Chronicles > Inbox")
    print(f"Folder name must remain exactly: {SLUG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
