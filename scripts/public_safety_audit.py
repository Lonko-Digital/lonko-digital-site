#!/usr/bin/env python3
"""Public safety audit for lonko-digital-site.

Scans the repository for patterns that must not appear in a public site.
Exit code 0 = pass, 1 = findings present.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Directories/files to skip
SKIP_DIRS = {".git", "__pycache__", "node_modules"}
SKIP_FILES = {"public_safety_audit.py"}

# Patterns that indicate sensitive or prohibited content
PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("Google Ads customer ID (10 digits)", re.compile(r"\b\d{3}-\d{3}-\d{4}\b")),
    ("Likely API key / secret assignment", re.compile(r"(?i)(api[_-]?key|client[_-]?secret|access[_-]?token|refresh[_-]?token|oauth)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{20,}")),
    ("Bearer token", re.compile(r"Bearer\s+[A-Za-z0-9_\-\.]{20,}")),
    (".env file reference with values", re.compile(r"(?i)^[A-Z0-9_]+\s*=\s*[^\s#]+", re.MULTILINE)),
    ("Private email (common personal domains)", re.compile(r"\b[A-Za-z0-9._%+-]+@(gmail|yahoo|hotmail|outlook|icloud|proton)\.(com|me|mail)\b", re.I)),
    ("localhost private dev URL", re.compile(r"https?://localhost:\d+")),  # allowed in README/docs — see scan_file
    ("LinkedIn client ID pattern", re.compile(r"(?i)linkedin.*client[_-]?id\s*[:=]\s*['\"]?[A-Za-z0-9]{10,}")),
    ("Google client ID pattern", re.compile(r"\d+-[A-Za-z0-9_]+\.apps\.googleusercontent\.com")),
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Private key block", re.compile(r"-----BEGIN (RSA |EC )?PRIVATE KEY-----")),
]

# Allowed placeholders (not flagged)
ALLOWLIST_SUBSTRINGS = [
    "lonkodigital@gmail.com",
    "lonko-digital.github.io",
    "REQUIRES LEGAL REVIEW",
    "contact.example.json",
    "lonko-public-appearance",
]

# File extensions to scan
SCAN_EXTENSIONS = {".html", ".css", ".js", ".json", ".md", ".txt", ".xml", ".py", ".example"}


def should_scan(path: Path) -> bool:
    if path.name in SKIP_FILES:
        return False
    if path.suffix.lower() not in SCAN_EXTENSIONS and path.name not in ("robots.txt", "CNAME"):
        return False
    return True


def is_allowlisted(line: str) -> bool:
    return any(token in line for token in ALLOWLIST_SUBSTRINGS)


def scan_file(path: Path) -> list[str]:
    findings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [f"{path}: unreadable ({exc})"]

    doc_paths = {"readme.md"} | {p.name for p in (ROOT / "docs").glob("*") if p.is_file()}

    for name, pattern in PATTERNS:
        for match in pattern.finditer(text):
            line_no = text.count("\n", 0, match.start()) + 1
            line = text.splitlines()[line_no - 1] if line_no <= len(text.splitlines()) else ""
            if is_allowlisted(line):
                continue
            if name == "Private email (common personal domains)" and match.group().lower() == "lonkodigital@gmail.com":
                continue
            if name == "localhost private dev URL" and (
                path.name.lower() in doc_paths or path.parent.name == "docs"
            ):
                continue
            findings.append(f"{path}:{line_no}: [{name}] {match.group()[:80]}")

    # Extra: .env files must not exist
    return findings


def main() -> int:
    findings: list[str] = []

    for env_name in (".env", ".env.local", ".env.production"):
        env_path = ROOT / env_name
        if env_path.exists():
            findings.append(f"{env_path}: prohibited .env file present")

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not should_scan(path):
            continue
        findings.extend(scan_file(path))

    print(f"Public safety audit — {ROOT.name}")
    print(f"Files scanned: {sum(1 for p in ROOT.rglob('*') if p.is_file() and should_scan(p))}")

    if findings:
        print(f"\nFAIL — {len(findings)} finding(s):\n")
        for f in findings:
            print(f"  • {f}")
        return 1

    print("\nPASS — no prohibited patterns detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
