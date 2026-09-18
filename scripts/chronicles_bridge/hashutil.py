"""Deterministic package hashing for Chronicles Drive intake."""

from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

# Files that identify the package / verify integrity — excluded from content_sha256.
EXCLUDED_FROM_CONTENT_HASH = frozenset({"manifest.json", "CHECKSUMS.sha256"})

TEXT_SUFFIXES = frozenset({".md", ".yaml", ".yml", ".json", ".txt", ".csv"})


def _normalize_newlines(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def normalize_yaml_bytes(raw: bytes) -> bytes:
    """Parse YAML and re-dump with sorted keys for stable hashing."""
    text = _normalize_newlines(raw).decode("utf-8-sig")
    data = yaml.safe_load(text) or {}
    if not isinstance(data, dict):
        raise ValueError("article.yaml must be a YAML mapping")
    dumped = yaml.safe_dump(
        data,
        sort_keys=True,
        default_flow_style=False,
        allow_unicode=True,
        width=1000,
    )
    return dumped.encode("utf-8")


def file_bytes_for_hash(path: Path, *, relative: str) -> bytes:
    raw = path.read_bytes()
    name = Path(relative).name.lower()
    if name in {"article.yaml", "article.yml"}:
        return normalize_yaml_bytes(raw)
    if path.suffix.lower() in TEXT_SUFFIXES:
        return _normalize_newlines(raw)
    return raw


def iter_content_files(package_dir: Path) -> list[tuple[str, Path]]:
    """Return (posix_relpath, path) for hashable package files, sorted."""
    package_dir = Path(package_dir)
    out: list[tuple[str, Path]] = []
    for path in package_dir.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(package_dir).as_posix()
        if Path(rel).name in EXCLUDED_FROM_CONTENT_HASH:
            continue
        # Skip hidden / OS junk
        if any(part.startswith(".") for part in Path(rel).parts):
            continue
        out.append((rel, path))
    out.sort(key=lambda t: t[0])
    return out


def per_file_digests(package_dir: Path) -> dict[str, str]:
    digests: dict[str, str] = {}
    for rel, path in iter_content_files(package_dir):
        data = file_bytes_for_hash(path, relative=rel)
        digests[rel] = hashlib.sha256(data).hexdigest()
    return digests


def content_sha256(package_dir: Path) -> str:
    """Package-level digest over sorted `{sha256}  {relpath}\\n` lines."""
    digests = per_file_digests(package_dir)
    lines = "".join(f"{sha}  {rel}\n" for rel, sha in digests.items())
    return hashlib.sha256(lines.encode("utf-8")).hexdigest()


def write_checksums(package_dir: Path) -> Path:
    digests = per_file_digests(package_dir)
    lines = [f"{sha}  {rel}\n" for rel, sha in digests.items()]
    path = Path(package_dir) / "CHECKSUMS.sha256"
    path.write_text("".join(lines), encoding="utf-8")
    return path


def parse_checksums_file(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            raise ValueError(f"Malformed CHECKSUMS line: {line!r}")
        result[parts[1].lstrip("*")] = parts[0].lower()
    return result


def verify_checksums(package_dir: Path) -> list[str]:
    """Return error strings; empty means OK."""
    package_dir = Path(package_dir)
    checksums_path = package_dir / "CHECKSUMS.sha256"
    if not checksums_path.is_file():
        return ["missing required CHECKSUMS.sha256"]
    try:
        declared = parse_checksums_file(checksums_path)
    except ValueError as exc:
        return [str(exc)]
    actual = per_file_digests(package_dir)
    errors: list[str] = []
    for rel, sha in sorted(actual.items()):
        if rel not in declared:
            errors.append(f"CHECKSUMS.sha256 missing entry for {rel}")
        elif declared[rel] != sha:
            errors.append(f"checksum mismatch for {rel}")
    for rel in sorted(declared):
        if rel not in actual:
            errors.append(f"CHECKSUMS.sha256 lists missing file {rel}")
    return errors
