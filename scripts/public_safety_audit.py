#!/usr/bin/env python3
"""Public safety audit for lonko-digital-site.

Scans the repository for patterns that must not appear in a public site.
Exit code 0 = pass, 1 = findings present.

Dotenv-style KEY=value scanning is file-aware: it applies only to dotenv-like
files. Universal credential patterns (named secret keys, Bearer, AWS, PEM, etc.)
still apply across the tree. Normal HTML/JS/Python (including official GTM)
must not trip dotenv detection.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Directories/files to skip
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".pytest_cache", "tests"}
SKIP_FILES = {"public_safety_audit.py"}

# Universal patterns (all scanned text files)
UNIVERSAL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("Google Ads customer ID (10 digits)", re.compile(r"\b\d{3}-\d{3}-\d{4}\b")),
    # Named secret keys — catches short and quoted values; key name is the signal.
    (
        "Likely API key / secret assignment",
        re.compile(
            r"(?i)\b("
            r"api[_-]?key|client[_-]?secret|access[_-]?token|refresh[_-]?token|"
            r"oauth(?:[_-]?token|[_-]?secret)|secret[_-]?key|private[_-]?key"
            r")\s*[:=]\s*['\"]?[^\s#'\"]+['\"]?"
        ),
    ),
    ("Bearer token", re.compile(r"Bearer\s+[A-Za-z0-9_\-\.]{20,}")),
    (
        "Private email (common personal domains)",
        re.compile(
            r"\b[A-Za-z0-9._%+-]+@(gmail|yahoo|hotmail|outlook|icloud|proton)\.(com|me|mail)\b",
            re.I,
        ),
    ),
    ("localhost private dev URL", re.compile(r"https?://localhost:\d+")),
    (
        "LinkedIn client ID pattern",
        re.compile(r"(?i)linkedin.*client[_-]?id\s*[:=]\s*['\"]?[A-Za-z0-9]{10,}"),
    ),
    ("Google client ID pattern", re.compile(r"\d+-[A-Za-z0-9_]+\.apps\.googleusercontent\.com")),
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Private key block", re.compile(r"-----BEGIN (RSA |EC )?PRIVATE KEY-----")),
]

# Applied only to dotenv-context files (not HTML/JS/Python source).
DOTENV_PATTERN: tuple[str, re.Pattern[str]] = (
    ".env-style assignment with value",
    re.compile(
        r"^[A-Za-z_][A-Za-z0-9_]*\s*=\s*(?:'[^']+'|\"[^\"]+\"|[^\s#]+)\s*$",
        re.MULTILINE,
    ),
)

# Allowed placeholders (not flagged)
ALLOWLIST_SUBSTRINGS = [
    "lonkodigital@gmail.com",
    "lonko-digital.github.io",
    "lonkodigital.com",
    "REQUIRES LEGAL REVIEW",
    "contact.example.json",
    "lonko-public-appearance",
    "your_key_here",
    "YOUR_SECRET",
    "changeme",
    "placeholder",
]

# File extensions to scan
SCAN_EXTENSIONS = {".html", ".css", ".js", ".json", ".md", ".txt", ".xml", ".py", ".example", ".env"}


def should_scan(path: Path) -> bool:
    if path.name in SKIP_FILES:
        return False
    if path.name.startswith(".env"):
        return True
    if path.suffix.lower() not in SCAN_EXTENSIONS and path.name not in ("robots.txt", "CNAME"):
        return False
    return True


def is_dotenv_context(path: Path) -> bool:
    """True when dotenv-style KEY=value scanning is appropriate for this file."""
    name = path.name
    if name.startswith(".env"):
        return True
    if name.endswith(".env"):
        return True
    if name in {"env.example", "dotenv.example"}:
        return True
    if name.endswith(".env.example"):
        return True
    # Bare *.example env templates (not JSON examples like contact.example.json)
    if path.suffix.lower() == ".example" and ".json" not in name.lower():
        return True
    return False


def is_allowlisted(line: str) -> bool:
    lower = line.lower()
    return any(token.lower() in lower for token in ALLOWLIST_SUBSTRINGS)


def _doc_names() -> set[str]:
    docs = ROOT / "docs"
    names = {"readme.md"}
    if docs.is_dir():
        names |= {p.name.lower() for p in docs.iterdir() if p.is_file()}
    return names


def scan_text(text: str, path: Path) -> list[str]:
    """Scan text as if it lived at path. Used by the CLI and regression tests."""
    findings: list[str] = []
    doc_paths = _doc_names()
    patterns = list(UNIVERSAL_PATTERNS)
    if is_dotenv_context(path):
        patterns.append(DOTENV_PATTERN)

    for name, pattern in patterns:
        for match in pattern.finditer(text):
            line_no = text.count("\n", 0, match.start()) + 1
            lines = text.splitlines()
            line = lines[line_no - 1] if line_no <= len(lines) else ""
            if is_allowlisted(line):
                continue
            if name == "Private email (common personal domains)" and match.group().lower() == "lonkodigital@gmail.com":
                continue
            if name == "localhost private dev URL" and (
                path.name.lower() in doc_paths or path.parent.name == "docs"
            ):
                continue
            findings.append(f"{path}:{line_no}: [{name}] {match.group()[:80]}")
    return findings


def scan_file(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [f"{path}: unreadable ({exc})"]
    return scan_text(text, path)


def collect_findings(root: Path | None = None) -> list[str]:
    root = root or ROOT
    findings: list[str] = []

    for env_name in (".env", ".env.local", ".env.production"):
        env_path = root / env_name
        if env_path.exists():
            findings.append(f"{env_path}: prohibited .env file present")

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not should_scan(path):
            continue
        findings.extend(scan_file(path))
    return findings


# Brittle Google Ads countdown copy must not survive on Home/About.
PRODUCT_STATUS_TARGETS = (
    Path("index.html"),
    Path("about") / "index.html",
)
PRODUCT_STATUS_BRITTLE: list[tuple[str, re.Pattern[str]]] = [
    ("one final live-account check", re.compile(r"one final live-account check", re.I)),
    ("final live-account", re.compile(r"final live-account", re.I)),
    ("internal testing complete", re.compile(r"internal testing complete", re.I)),
]


def collect_product_status_findings(root: Path | None = None) -> list[str]:
    root = root or ROOT
    findings: list[str] = []
    for rel in PRODUCT_STATUS_TARGETS:
        path = root / rel
        if not path.is_file():
            findings.append(f"{path}: missing Home/About product-status target")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in PRODUCT_STATUS_BRITTLE:
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                findings.append(
                    f"{path}:{line_no}: [brittle product-status copy] {label}"
                )
    return findings


# /notes/confirmed/ is a DOI landing page: noindex, unlisted, directly reachable.
NOTES_CONFIRMED_PAGE = Path("notes") / "confirmed" / "index.html"
NOTES_CONFIRMED_CANONICAL = "https://lonkodigital.com/notes/confirmed/"
NOTES_CONFIRMED_ROBOTS = '<meta name="robots" content="noindex, nofollow">'
# Catch /notes/confirmed destinations including query strings and fragments.
# Does not match bare path text outside an href attribute.
NOTES_CONFIRMED_HREF = re.compile(
    r"""href\s*=\s*(["'])(?:[^"']*?)notes/confirmed(?:/)?(?:[?#][^"']*)?\1""",
    re.I,
)
NOTES_CONFIRMED_SITEMAP_LOC = re.compile(
    r"notes/confirmed/?",
    re.I,
)
# Exact DOI path targets after comment-strip / trim / optional trailing $.
_NOTES_CONFIRMED_ROBOTS_PATH = re.compile(
    r"^/notes/confirmed(?:\*|/|/\*)?$",
    re.I,
)


def robots_disallows_notes_confirmed(robots_text: str) -> bool:
    """True when robots.txt clearly Disallows the DOI confirmation path.

    Uses normalized line parsing (strip inline comments, trim, case-insensitive
    Disallow) so trailing $, wildcards, and comments cannot bypass the check.
    Does not match unrelated paths like /notes/confirmed-archive.
    """
    for raw_line in robots_text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if not line.lower().startswith("disallow:"):
            continue
        path = line.split(":", 1)[1].strip()
        while path.endswith("$"):
            path = path[:-1]
        path = path.rstrip()
        if _NOTES_CONFIRMED_ROBOTS_PATH.fullmatch(path):
            return True
    return False


# Public discovery surfaces that must not promote the DOI landing page.
NOTES_CONFIRMED_DISCOVERY_SURFACES = (
    Path("index.html"),
    Path("about") / "index.html",
    Path("contact") / "index.html",
    Path("privacy") / "index.html",
    Path("terms") / "index.html",
    Path("insights") / "index.html",
    Path("chronicles") / "index.html",
)


def _notes_confirmed_discovery_html(root: Path) -> list[Path]:
    """Home/About/Insights/Chronicles/Contact/Privacy/Terms HTML surfaces."""
    paths: list[Path] = []
    for rel in NOTES_CONFIRMED_DISCOVERY_SURFACES:
        path = root / rel
        if path.is_file():
            paths.append(path)
    for section in ("insights", "chronicles"):
        section_root = root / section
        if not section_root.is_dir():
            continue
        for path in sorted(section_root.rglob("index.html")):
            if "content" in path.parts:
                continue
            if path.resolve() == (root / NOTES_CONFIRMED_PAGE).resolve():
                continue
            if path not in paths:
                paths.append(path)
    return paths


def collect_notes_confirmed_indexing_findings(root: Path | None = None) -> list[str]:
    """Fail if the DOI confirmation page becomes indexable or normally discoverable."""
    root = root or ROOT
    findings: list[str] = []
    page = root / NOTES_CONFIRMED_PAGE

    if not page.is_file():
        findings.append(
            f"{page}: missing — DOI confirmation page must remain a normal reachable HTML page"
        )
        return findings

    text = page.read_text(encoding="utf-8", errors="replace")
    if NOTES_CONFIRMED_ROBOTS not in text:
        findings.append(
            f"{page}: missing exact robots meta {NOTES_CONFIRMED_ROBOTS!r}"
        )
    if f'rel="canonical" href="{NOTES_CONFIRMED_CANONICAL}"' not in text:
        findings.append(
            f"{page}: canonical must be exactly {NOTES_CONFIRMED_CANONICAL}"
        )
    if "<!DOCTYPE html>" not in text and "<!doctype html>" not in text.lower():
        findings.append(f"{page}: must remain a normal HTML document")

    for sitemap_name in ("sitemap.xml", "sitemap-pages.xml", "sitemap-chronicles.xml"):
        sitemap = root / sitemap_name
        if not sitemap.is_file():
            continue
        sitemap_text = sitemap.read_text(encoding="utf-8", errors="replace")
        if NOTES_CONFIRMED_SITEMAP_LOC.search(sitemap_text):
            findings.append(
                f"{sitemap}: must not list /notes/confirmed/ (DOI landing is intentionally unlisted)"
            )

    robots = root / "robots.txt"
    if robots.is_file():
        robots_text = robots.read_text(encoding="utf-8", errors="replace")
        if robots_disallows_notes_confirmed(robots_text):
            findings.append(
                f"{robots}: must not Disallow /notes/confirmed/ "
                "(crawlers need to see the page noindex directive)"
            )

    for path in _notes_confirmed_discovery_html(root):
        html = path.read_text(encoding="utf-8", errors="replace")
        for match in NOTES_CONFIRMED_HREF.finditer(html):
            line_no = html.count("\n", 0, match.start()) + 1
            findings.append(
                f"{path}:{line_no}: [notes-confirmed discovery] "
                "DOI landing must not appear as a normal navigation/destination link"
            )

    return findings


def main() -> int:
    findings = collect_findings(ROOT)
    findings.extend(collect_product_status_findings(ROOT))
    findings.extend(collect_notes_confirmed_indexing_findings(ROOT))
    scanned = sum(
        1
        for p in ROOT.rglob("*")
        if p.is_file() and not any(part in SKIP_DIRS for part in p.parts) and should_scan(p)
    )

    print(f"Public safety audit — {ROOT.name}")
    print(f"Files scanned: {scanned}")

    if findings:
        print(f"\nFAIL — {len(findings)} finding(s):\n")
        for f in findings:
            print(f"  • {f}")
        return 1

    print("\nPASS — no prohibited patterns detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
