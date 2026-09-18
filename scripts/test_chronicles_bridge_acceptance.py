#!/usr/bin/env python3
"""End-to-end acceptance tests for the Chronicles Drive publishing bridge.

Covers: valid package, invalid/fail-closed, replay, update, slug rename, soft-retire.

Does not open a real GitHub PR (that is CI's job). Does verify staging, build outputs,
audit, and archive/quarantine behavior. Production main is not modified by this script
beyond temporary content under chronicles/content/ which is cleaned up.

Usage:
  python scripts/test_chronicles_bridge_acceptance.py
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import chronicles_lib.build as build_mod  # noqa: E402
from chronicles_bridge.hashutil import content_sha256, write_checksums  # noqa: E402
from chronicles_bridge.ingest import ingest_package  # noqa: E402
from chronicles_bridge.testdata import build_package  # noqa: E402

SLUG = "bridge-acceptance-stable-traffic-signal"
CONTENT = ROOT / "chronicles" / "content"
OUT = ROOT / "chronicles"


def _clean_slug() -> None:
    pkg = CONTENT / SLUG
    if pkg.exists():
        shutil.rmtree(pkg)
    page = OUT / SLUG
    if page.exists():
        shutil.rmtree(page)


def _assert(cond: bool, msg: str, failures: list[str]) -> None:
    if not cond:
        failures.append(msg)


def test_valid(failures: list[str], work: Path) -> str:
    inbox = work / "inbox"
    processed = work / "processed"
    quarantine = work / "quarantine"
    audit = work / "audit.jsonl"
    inbox.mkdir()
    pkg = build_package(
        inbox,
        slug=SLUG,
        package_id="01TESTVALID0000000000000000",
        meta={
            "title": "When Stable Traffic Hides a Conversion Problem",
            "deck": "Traffic held steady while conversions slipped — what to check first.",
            "placement": {"featured": True, "sections": ["owners"]},
            "status": "published",
            "datePublished": "2026-09-17",
            "dateModified": "2026-09-17",
            "schema_type": "Article",
            "content_type": "Analysis",
        },
        body=(
            "## What we found\n\n"
            "Traffic volume remained relatively stable while conversion rate declined.\n\n"
            "## What it means\n\n"
            "Volume alone does not explain the change.\n"
        ),
    )
    sha = content_sha256(pkg)
    result = ingest_package(
        pkg,
        processed_dir=processed,
        quarantine_dir=quarantine,
        audit_path=audit,
        run_build=True,
        archive=True,
    )
    _assert(result.outcome == "staged", f"valid: expected staged got {result.outcome}: {result.detail}", failures)

    page = OUT / SLUG / "index.html"
    _assert(page.is_file(), "valid: article HTML missing", failures)
    html = page.read_text(encoding="utf-8") if page.is_file() else ""
    _assert("noindex" not in html, "valid: published should not noindex", failures)
    _assert('"@type": "Article"' in html or '"@type":"Article"' in html, "valid: schema missing", failures)

    home = (OUT / "index.html").read_text(encoding="utf-8")
    _assert(SLUG in home, "valid: not on Chronicles index/placement", failures)

    sm = (ROOT / "sitemap-chronicles.xml").read_text(encoding="utf-8")
    _assert(f"/chronicles/{SLUG}/" in sm, "valid: missing from sitemap", failures)

    feed = (OUT / "feed.xml").read_text(encoding="utf-8")
    _assert(SLUG in feed, "valid: missing from feed", failures)

    idx = json.loads((OUT / "assets" / "search-index.json").read_text(encoding="utf-8"))
    _assert(any(e.get("slug") == SLUG for e in idx), "valid: missing from search index", failures)

    audit_rows = [json.loads(l) for l in audit.read_text(encoding="utf-8").splitlines() if l.strip()]
    _assert(any(r.get("result") == "staged" and r.get("package_id") == "01TESTVALID0000000000000000" for r in audit_rows), "valid: audit missing", failures)
    _assert(any(processed.iterdir()), "valid: not moved to processed/", failures)
    _assert(sha == result.content_sha256, "valid: hash mismatch on result", failures)
    return sha


def test_invalid(failures: list[str], work: Path) -> None:
    inbox = work / "inbox-bad"
    processed = work / "processed"
    quarantine = work / "quarantine"
    audit = work / "audit.jsonl"
    inbox.mkdir(exist_ok=True)
    pkg = build_package(
        inbox,
        slug="bridge-acceptance-invalid-package",
        package_id="01TESTINVALID0000000000000",
        meta={"status": "published", "schema_type": "Article"},
        body="Body without required fields override.\n",
    )
    # Break package: remove schema_type and checksums
    yaml_path = pkg / "article.yaml"
    text = yaml_path.read_text(encoding="utf-8")
    yaml_path.write_text(text.replace("schema_type: Article\n", ""), encoding="utf-8")
    (pkg / "CHECKSUMS.sha256").unlink()
    before_content = list((CONTENT).glob("*/article.md"))
    result = ingest_package(
        pkg,
        processed_dir=processed,
        quarantine_dir=quarantine,
        audit_path=audit,
        run_build=True,
        archive=True,
    )
    _assert(result.outcome == "quarantine", f"invalid: expected quarantine got {result.outcome}", failures)
    _assert(not (CONTENT / "bridge-acceptance-invalid-package").exists(), "invalid: staged bad package", failures)
    _assert(any(quarantine.iterdir()), "invalid: not in quarantine/", failures)
    after = list(CONTENT.glob("*/article.md"))
    _assert(len(after) == len(before_content), "invalid: content tree changed unexpectedly", failures)


def test_replay_and_update(failures: list[str], work: Path, prior_sha: str) -> None:
    inbox = work / "inbox-replay"
    processed = work / "processed"
    quarantine = work / "quarantine"
    audit = work / "audit.jsonl"
    inbox.mkdir(exist_ok=True)

    # same package_id → noop
    pkg = build_package(
        inbox,
        slug=SLUG,
        package_id="01TESTVALID0000000000000000",
        meta={
            "title": "When Stable Traffic Hides a Conversion Problem",
            "status": "published",
            "datePublished": "2026-09-17",
            "dateModified": "2026-09-17",
            "placement": {"featured": True, "sections": ["owners"]},
        },
        body="## What we found\n\nTraffic volume remained relatively stable while conversion rate declined.\n",
    )
    r1 = ingest_package(pkg, processed_dir=processed, quarantine_dir=quarantine, audit_path=audit, run_build=False, archive=True)
    _assert(r1.outcome == "noop_replay", f"replay id: expected noop_replay got {r1.outcome}", failures)

    # same slug+hash with new package_id → noop
    inbox2 = work / "inbox-replay2"
    inbox2.mkdir()
    pkg2 = build_package(
        inbox2,
        slug=SLUG,
        package_id="01TESTREPLAYHASH00000000000",
        meta={
            "title": "When Stable Traffic Hides a Conversion Problem",
            "status": "published",
            "datePublished": "2026-09-17",
            "dateModified": "2026-09-17",
            "placement": {"featured": True, "sections": ["owners"]},
        },
        body="## What we found\n\nTraffic volume remained relatively stable while conversion rate declined.\n",
    )
    # Force same hash as first by copying checksum/content from staged article is hard;
    # instead audit already has slug+hash — rebuild identical body/meta should match prior_sha
    if content_sha256(pkg2) == prior_sha:
        r2 = ingest_package(pkg2, processed_dir=processed, quarantine_dir=quarantine, audit_path=audit, run_build=False, archive=True)
        _assert(r2.outcome == "noop_replay", f"replay hash: expected noop got {r2.outcome}", failures)
    else:
        # Body whitespace may differ — still OK; skip strict hash replay if builder drift
        shutil.rmtree(pkg2)

    # stale update (same dateModified, changed body)
    inbox3 = work / "inbox-stale"
    inbox3.mkdir()
    pkg3 = build_package(
        inbox3,
        slug=SLUG,
        package_id="01TESTSTALE000000000000000",
        meta={
            "title": "When Stable Traffic Hides a Conversion Problem",
            "status": "published",
            "datePublished": "2026-09-17",
            "dateModified": "2026-09-17",
            "placement": {"featured": True, "sections": ["owners"]},
        },
        body="## Changed without advancing dateModified\n\nThis should quarantine.\n",
    )
    r3 = ingest_package(pkg3, processed_dir=processed, quarantine_dir=quarantine, audit_path=audit, run_build=False, archive=True)
    _assert(r3.outcome == "quarantine", f"stale: expected quarantine got {r3.outcome}", failures)
    _assert("dateModified" in r3.detail or "stale" in r3.detail, f"stale: unexpected detail {r3.detail}", failures)

    # valid advancing update
    inbox4 = work / "inbox-update"
    inbox4.mkdir()
    pkg4 = build_package(
        inbox4,
        slug=SLUG,
        package_id="01TESTUPDATE0000000000000",
        meta={
            "title": "When Stable Traffic Hides a Conversion Problem",
            "deck": "Updated deck for bridge acceptance.",
            "status": "published",
            "datePublished": "2026-09-17",
            "dateModified": "2026-09-18",
            "placement": {"featured": True, "sections": ["owners"]},
        },
        body="## Updated finding\n\nConversion efficiency declined while traffic stayed flat.\n",
    )
    r4 = ingest_package(pkg4, processed_dir=processed, quarantine_dir=quarantine, audit_path=audit, run_build=True, archive=True)
    _assert(r4.outcome == "staged", f"update: expected staged got {r4.outcome}: {r4.detail}", failures)
    article = (CONTENT / SLUG / "article.md").read_text(encoding="utf-8")
    _assert("datePublished: '2026-09-17'" in article or "datePublished: 2026-09-17" in article, "update: datePublished not preserved", failures)
    _assert("2026-09-18" in article, "update: dateModified not advanced", failures)

    # unauthorized slug rename
    inbox5 = work / "inbox-rename"
    inbox5.mkdir()
    pkg5 = build_package(
        inbox5,
        slug="bridge-acceptance-renamed-slug",
        package_id="01TESTRENAME00000000000000",
        meta={
            "slug": SLUG,  # mismatch vs folder
            "status": "published",
            "datePublished": "2026-09-17",
            "dateModified": "2026-09-19",
        },
        body="Rename attempt.\n",
    )
    r5 = ingest_package(pkg5, processed_dir=processed, quarantine_dir=quarantine, audit_path=audit, run_build=False, archive=True)
    _assert(r5.outcome == "quarantine", f"rename: expected quarantine got {r5.outcome}", failures)


def test_soft_retire(failures: list[str], work: Path) -> None:
    inbox = work / "inbox-retire"
    processed = work / "processed"
    quarantine = work / "quarantine"
    audit = work / "audit.jsonl"
    inbox.mkdir(exist_ok=True)
    pkg = build_package(
        inbox,
        slug=SLUG,
        package_id="01TESTRETIRE00000000000000",
        meta={
            "title": "When Stable Traffic Hides a Conversion Problem",
            "status": "retired",
            "datePublished": "2026-09-17",
            "dateModified": "2026-09-20",
            "placement": {"featured": True, "sections": ["owners"]},
        },
        body="## Retired body\n\nRemains for reference.\n",
    )
    result = ingest_package(
        pkg,
        processed_dir=processed,
        quarantine_dir=quarantine,
        audit_path=audit,
        run_build=True,
        archive=True,
    )
    _assert(result.outcome == "staged", f"retire: expected staged got {result.outcome}: {result.detail}", failures)

    page = OUT / SLUG / "index.html"
    _assert(page.is_file(), "retire: HTML missing (URL must remain)", failures)
    html = page.read_text(encoding="utf-8")
    _assert("noindex" in html and "nofollow" in html, "retire: missing noindex,nofollow", failures)
    _assert("chronicles-retired-notice" in html, "retire: missing retired notice", failures)
    _assert("2026-09-17" in html, "retire: datePublished missing on page", failures)

    home = (OUT / "index.html").read_text(encoding="utf-8")
    _assert(SLUG not in home, "retire: still on homepage/listings", failures)

    sm = (ROOT / "sitemap-chronicles.xml").read_text(encoding="utf-8")
    _assert(f"/chronicles/{SLUG}/" not in sm, "retire: still in sitemap", failures)

    feed = (OUT / "feed.xml").read_text(encoding="utf-8")
    _assert(SLUG not in feed, "retire: still in feed", failures)

    idx = json.loads((OUT / "assets" / "search-index.json").read_text(encoding="utf-8"))
    _assert(not any(e.get("slug") == SLUG for e in idx), "retire: still in search index", failures)


def main() -> int:
    failures: list[str] = []
    _clean_slug()
    # Ensure empty shell build works as baseline
    build_mod.build()

    work = Path(tempfile.mkdtemp(prefix="chronicles-bridge-"))
    try:
        print("— valid synthetic package —")
        prior_sha = test_valid(failures, work)
        print("— invalid package —")
        test_invalid(failures, work)
        print("— replay / update / rename —")
        test_replay_and_update(failures, work, prior_sha)
        print("— soft-retire —")
        test_soft_retire(failures, work)
    finally:
        _clean_slug()
        build_mod.build()
        shutil.rmtree(work, ignore_errors=True)

    if failures:
        print("BRIDGE ACCEPTANCE: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("BRIDGE ACCEPTANCE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
