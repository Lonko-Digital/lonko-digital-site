"""Permanent lightweight ingest audit log."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AUDIT_PATH = ROOT / "chronicles" / "ingest-audit.jsonl"


@dataclass
class AuditRecord:
    package_id: str
    slug: str
    content_sha256: str
    producer: str
    ingested_at: str
    result: str
    detail: str = ""
    pr_url: str = ""
    commit_sha: str = ""
    branch: str = ""

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, sort_keys=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def append_audit(record: AuditRecord, path: Path | None = None) -> None:
    path = path or DEFAULT_AUDIT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(record.to_json() + "\n")


def load_audit(path: Path | None = None) -> list[dict[str, Any]]:
    path = path or DEFAULT_AUDIT_PATH
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def find_prior_success(
    *,
    package_id: str | None = None,
    slug: str | None = None,
    content_sha256: str | None = None,
    path: Path | None = None,
) -> dict[str, Any] | None:
    rows = load_audit(path)
    for row in reversed(rows):
        if row.get("result") not in {"staged", "pr_opened", "noop_replay", "merged"}:
            continue
        if package_id and row.get("package_id") == package_id:
            return row
        if (
            slug
            and content_sha256
            and row.get("slug") == slug
            and row.get("content_sha256") == content_sha256
        ):
            return row
    return None
