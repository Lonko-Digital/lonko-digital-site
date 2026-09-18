#!/usr/bin/env python3
"""Run Chronicles Drive inbox ingest (local filesystem and/or Google Drive).

Examples:
  python scripts/run_chronicles_ingest.py --inbox bridge/inbox
  python scripts/run_chronicles_ingest.py --sync-drive --inbox bridge/inbox

Never pushes to main. CI opens a PR after staging.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from chronicles_bridge.drive import drive_configured, sync_inbox_to_local  # noqa: E402
from chronicles_bridge.ingest import (  # noqa: E402
    DEFAULT_INBOX,
    DEFAULT_PROCESSED,
    DEFAULT_QUARANTINE,
    ingest_inbox,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inbox", type=Path, default=DEFAULT_INBOX)
    parser.add_argument("--processed", type=Path, default=DEFAULT_PROCESSED)
    parser.add_argument("--quarantine", type=Path, default=DEFAULT_QUARANTINE)
    parser.add_argument(
        "--audit",
        type=Path,
        default=ROOT / "chronicles" / "ingest-audit.jsonl",
    )
    parser.add_argument("--sync-drive", action="store_true", help="Pull Drive inbox first")
    parser.add_argument("--no-build", action="store_true", help="Stage only; skip Chronicles build")
    parser.add_argument("--no-archive", action="store_true", help="Leave packages in inbox")
    args = parser.parse_args()

    if args.sync_drive:
        if not drive_configured():
            print(
                "Drive secrets not configured; skipping Drive sync "
                "(local inbox only).",
                file=sys.stderr,
            )
        else:
            paths = sync_inbox_to_local(args.inbox)
            print(f"Downloaded {len(paths)} package folder(s) from Drive.")

    results = ingest_inbox(
        args.inbox,
        processed_dir=args.processed,
        quarantine_dir=args.quarantine,
        audit_path=args.audit,
        run_build=not args.no_build,
        archive=not args.no_archive,
    )

    payload = [
        {
            "slug": r.slug,
            "package_id": r.package_id,
            "content_sha256": r.content_sha256,
            "outcome": r.outcome,
            "detail": r.detail,
            "staged_path": r.staged_path,
            "errors": r.errors,
        }
        for r in results
    ]
    print(json.dumps(payload, indent=2))

    # Exit non-zero only when quarantine occurred and nothing staged
    if any(r.outcome == "quarantine" for r in results) and not any(
        r.outcome == "staged" for r in results
    ):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
