"""Ingest orchestration: validate → stage → build check → audit → archive."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from chronicles_lib.build import build as chronicles_build
from chronicles_lib.model import load_article

from .audit import (
    DEFAULT_AUDIT_PATH,
    AuditRecord,
    append_audit,
    find_prior_success,
    now_iso,
)
from .package import inspect_drive_package, stage_article_md

ROOT = Path(__file__).resolve().parents[2]
CONTENT_ROOT = ROOT / "chronicles" / "content"
DEFAULT_INBOX = ROOT / "bridge" / "inbox"
DEFAULT_PROCESSED = ROOT / "bridge" / "processed"
DEFAULT_QUARANTINE = ROOT / "bridge" / "quarantine"
PROCESSED_RETENTION_DAYS = 90
QUARANTINE_RETENTION_DAYS = 30


@dataclass
class IngestResult:
    slug: str
    package_id: str
    content_sha256: str
    outcome: str
    detail: str = ""
    staged_path: str = ""
    errors: list[str] = field(default_factory=list)


def _parse_iso_day(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _existing_article(slug: str) -> Path | None:
    path = CONTENT_ROOT / slug / "article.md"
    return path if path.is_file() else None


def detect_slug_rename_attempt(insp) -> list[str]:
    errors: list[str] = []
    if insp.article.slug and insp.article.slug != insp.manifest.slug:
        errors.append("unauthorized slug rename: article.slug != manifest.slug")
    return errors


def _move_to(dest_root: Path, package_dir: Path) -> Path:
    dest_root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = dest_root / f"{package_dir.name}__{stamp}"
    if target.exists():
        shutil.rmtree(target)
    shutil.move(str(package_dir), str(target))
    return target


def prune_retention(root: Path, days: int) -> int:
    if not root.is_dir():
        return 0
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    removed = 0
    for child in root.iterdir():
        if not child.is_dir():
            continue
        mtime = datetime.fromtimestamp(child.stat().st_mtime, tz=timezone.utc)
        if mtime < cutoff:
            shutil.rmtree(child, ignore_errors=True)
            removed += 1
    return removed


def ingest_package(
    package_dir: Path,
    *,
    processed_dir: Path = DEFAULT_PROCESSED,
    quarantine_dir: Path = DEFAULT_QUARANTINE,
    audit_path: Path = DEFAULT_AUDIT_PATH,
    run_build: bool = True,
    archive: bool = True,
    content_root: Path | None = None,
) -> IngestResult:
    package_dir = Path(package_dir)
    dest_content = Path(content_root) if content_root else CONTENT_ROOT

    insp = inspect_drive_package(package_dir)
    mid = insp.manifest.package_id
    slug = insp.manifest.slug or package_dir.name
    sha = insp.computed_sha256 or insp.manifest.content_sha256

    prior_id = find_prior_success(package_id=mid, path=audit_path) if mid else None
    if prior_id and not insp.errors:
        detail = f"replay package_id={mid} previously {prior_id.get('result')}"
        append_audit(
            AuditRecord(
                package_id=mid,
                slug=slug,
                content_sha256=sha,
                producer=insp.manifest.producer,
                ingested_at=now_iso(),
                result="noop_replay",
                detail=detail,
            ),
            audit_path,
        )
        if archive and package_dir.exists():
            _move_to(processed_dir, package_dir)
        return IngestResult(slug, mid, sha, "noop_replay", detail)

    prior_hash = (
        find_prior_success(slug=slug, content_sha256=sha, path=audit_path) if sha else None
    )
    if prior_hash and not insp.errors:
        detail = f"replay slug+hash previously {prior_hash.get('result')}"
        append_audit(
            AuditRecord(
                package_id=mid,
                slug=slug,
                content_sha256=sha,
                producer=insp.manifest.producer,
                ingested_at=now_iso(),
                result="noop_replay",
                detail=detail,
            ),
            audit_path,
        )
        if archive and package_dir.exists():
            _move_to(processed_dir, package_dir)
        return IngestResult(slug, mid, sha, "noop_replay", detail)

    errors = list(insp.errors)
    if not errors:
        errors.extend(detect_slug_rename_attempt(insp))

    existing = dest_content / slug / "article.md"
    if not errors and existing.is_file():
        prior = load_article(existing.parent)
        if insp.article.datePublished != prior.datePublished:
            errors.append(
                f"datePublished must be preserved on update "
                f"(existing {prior.datePublished}, package {insp.article.datePublished})"
            )
        prior_mod = _parse_iso_day(prior.dateModified)
        new_mod = _parse_iso_day(insp.article.dateModified)
        if prior_mod and new_mod and new_mod <= prior_mod:
            errors.append(
                f"stale update: dateModified must advance "
                f"(existing {prior.dateModified}, package {insp.article.dateModified})"
            )

    if errors:
        detail = "; ".join(errors)
        append_audit(
            AuditRecord(
                package_id=mid,
                slug=slug,
                content_sha256=sha,
                producer=insp.manifest.producer or "unknown",
                ingested_at=now_iso(),
                result="quarantine",
                detail=detail[:2000],
            ),
            audit_path,
        )
        if archive and package_dir.exists():
            _move_to(quarantine_dir, package_dir)
        return IngestResult(slug, mid, sha, "quarantine", detail, errors=errors)

    dest = dest_content / slug
    stage_article_md(package_dir, dest)

    if run_build:
        code = chronicles_build()
        if code != 0:
            detail = "chronicles build failed after staging"
            if dest.exists():
                shutil.rmtree(dest)
            append_audit(
                AuditRecord(
                    package_id=mid,
                    slug=slug,
                    content_sha256=sha,
                    producer=insp.manifest.producer,
                    ingested_at=now_iso(),
                    result="quarantine",
                    detail=detail,
                ),
                audit_path,
            )
            if archive and package_dir.exists():
                _move_to(quarantine_dir, package_dir)
            return IngestResult(slug, mid, sha, "quarantine", detail, errors=[detail])

    append_audit(
        AuditRecord(
            package_id=mid,
            slug=slug,
            content_sha256=sha,
            producer=insp.manifest.producer,
            ingested_at=now_iso(),
            result="staged",
            detail="staged into chronicles/content; awaiting PR",
        ),
        audit_path,
    )
    staged = str(dest)
    if archive and package_dir.exists():
        _move_to(processed_dir, package_dir)

    return IngestResult(slug, mid, sha, "staged", "ok", staged_path=staged)


def ingest_inbox(
    inbox: Path = DEFAULT_INBOX,
    *,
    processed_dir: Path = DEFAULT_PROCESSED,
    quarantine_dir: Path = DEFAULT_QUARANTINE,
    audit_path: Path = DEFAULT_AUDIT_PATH,
    run_build: bool = True,
    archive: bool = True,
    content_root: Path | None = None,
) -> list[IngestResult]:
    inbox = Path(inbox)
    inbox.mkdir(parents=True, exist_ok=True)
    results: list[IngestResult] = []
    for child in sorted(p for p in inbox.iterdir() if p.is_dir() and not p.name.startswith(".")):
        results.append(
            ingest_package(
                child,
                processed_dir=processed_dir,
                quarantine_dir=quarantine_dir,
                audit_path=audit_path,
                run_build=run_build,
                archive=archive,
                content_root=content_root,
            )
        )
    prune_retention(processed_dir, PROCESSED_RETENTION_DAYS)
    prune_retention(quarantine_dir, QUARANTINE_RETENTION_DAYS)
    return results
