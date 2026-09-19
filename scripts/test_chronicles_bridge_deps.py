#!/usr/bin/env python3
"""Import-level guard for Chronicles Drive bridge runtime dependencies.

Fails fast if google-auth / google-api-python-client (or other required
packages) are missing from the environment. Run after:
  pip install -r requirements-chronicles-bridge.txt

Usage:
  python scripts/test_chronicles_bridge_deps.py
"""

from __future__ import annotations

import importlib
import sys


REQUIRED = (
    ("yaml", "pyyaml"),
    ("markdown", "markdown"),
    ("google.oauth2.service_account", "google-auth"),
    ("googleapiclient.discovery", "google-api-python-client"),
)


def main() -> int:
    failures: list[str] = []
    for module, package in REQUIRED:
        try:
            importlib.import_module(module)
        except ModuleNotFoundError as exc:
            failures.append(f"missing import {module!r} (package {package!r}): {exc}")
    if failures:
        print("FAIL: Chronicles bridge dependency check")
        for line in failures:
            print(f"  - {line}")
        print(
            "Install with: pip install -r requirements-chronicles-bridge.txt",
            file=sys.stderr,
        )
        return 1
    print("PASS: Chronicles bridge deps importable")
    for module, package in REQUIRED:
        print(f"  ok {module} ({package})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
