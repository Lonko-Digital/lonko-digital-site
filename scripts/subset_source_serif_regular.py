"""One-off: download Source Serif 4 Regular (Text/Roman) and subset to self-hosted WOFF2.

Body text uses the Text/Roman cut (SourceSerif4-Regular.otf), not Display.
Same Latin unicode subset as scripts/subset_source_serif.py (Display 600/700).
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT / "assets" / "fonts"
# Prefer /tmp when available; fall back to system temp (Windows-friendly).
TMP = Path("/tmp/source-serif") if Path("/tmp").exists() else Path(tempfile.gettempdir()) / "source-serif"
FONT_DIR.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)

DESK_URL = (
    "https://github.com/adobe-fonts/source-serif/releases/download/"
    "4.005R/source-serif-4.005_Desktop.zip"
)

# Prefer Text/Roman Regular; accept Variable Text Regular if only that is present.
WANTED_NAMES = (
    "SourceSerif4-Regular.otf",
    "SourceSerif4Text-Regular.otf",
)
OUT_NAME = "source-serif-4-regular.woff2"


def latin_unicodes_arg() -> str:
    # Standard Latin + apostrophe + basic punctuation (incl. curly quotes used live)
    unicodes = [f"U+{c:04X}" for c in range(0x20, 0x7F)]
    for c in (0x00A0, 0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2026):
        unicodes.append(f"U+{c:04X}")
    return ",".join(unicodes)


def main() -> None:
    desk = TMP / "desktop.zip"
    if not desk.exists() or desk.stat().st_size < 1000:
        print("Downloading Desktop zip...")
        urllib.request.urlretrieve(DESK_URL, desk)
    print("desktop zip", desk.stat().st_size)

    extract = TMP / "desktop"
    extract.mkdir(exist_ok=True)
    source: Path | None = None
    matched_name = ""

    with zipfile.ZipFile(desk) as z:
        namelist = z.namelist()
        for wanted in WANTED_NAMES:
            for name in namelist:
                if Path(name).name == wanted:
                    target = extract / wanted
                    if not target.exists():
                        with z.open(name) as src, open(target, "wb") as dst:
                            dst.write(src.read())
                    source = target
                    matched_name = wanted
                    print("extracted", wanted, target.stat().st_size)
                    break
            if source is not None:
                break

    if source is None:
        # Helpful dump of Regular candidates if zip layout changed
        with zipfile.ZipFile(desk) as z:
            candidates = [
                n for n in z.namelist()
                if "Regular" in Path(n).name and Path(n).suffix.lower() == ".otf"
            ]
        raise SystemExit(
            "Missing SourceSerif4 Regular OTF. Candidates in zip:\n  "
            + "\n  ".join(candidates[:40])
        )

    unicodes_arg = latin_unicodes_arg()
    out = FONT_DIR / OUT_NAME
    cmd = [
        sys.executable,
        "-m",
        "fontTools.subset",
        str(source),
        f"--unicodes={unicodes_arg}",
        "--layout-features=kern,liga,clig,calt",
        "--flavor=woff2",
        f"--output-file={out}",
        "--name-IDs=*",
        "--name-languages=*",
        "--notdef-outline",
        "--recommended-glyphs",
        "--no-hinting",
    ]
    print("subsetting", matched_name, "->", out.name)
    subprocess.check_call(cmd)
    size = out.stat().st_size
    print(f"  {out.name}: {size} bytes ({size / 1024:.1f} KiB)")


if __name__ == "__main__":
    main()
