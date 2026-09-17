#!/usr/bin/env python3
"""Build Lonko Chronicles static output.

Usage (from lonko-digital-site/):
  python scripts/build_chronicles.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow `python scripts/build_chronicles.py` without installing the package.
SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from chronicles_lib.build import main

if __name__ == "__main__":
    main()
