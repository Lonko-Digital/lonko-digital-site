"""One-off: download Source Serif 4 Display and subset to self-hosted WOFF2."""
from __future__ import annotations

import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT / "assets" / "fonts"
TMP = Path("/tmp/source-serif")
FONT_DIR.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)

DESK_URL = (
    "https://github.com/adobe-fonts/source-serif/releases/download/"
    "4.005R/source-serif-4.005_Desktop.zip"
)
WANTED = {
    600: "SourceSerif4Display-Semibold.otf",
    700: "SourceSerif4Display-Bold.otf",
}
OUT_NAMES = {
    600: "source-serif-4-semibold.woff2",
    700: "source-serif-4-bold.woff2",
}


def main() -> None:
    desk = TMP / "desktop.zip"
    if not desk.exists() or desk.stat().st_size < 1000:
        print("Downloading Desktop zip...")
        urllib.request.urlretrieve(DESK_URL, desk)
    print("desktop zip", desk.stat().st_size)

    extract = TMP / "desktop"
    extract.mkdir(exist_ok=True)
    sources: dict[int, Path] = {}
    with zipfile.ZipFile(desk) as z:
        for name in z.namelist():
            base = Path(name).name
            for weight, wanted in WANTED.items():
                if base == wanted:
                    target = extract / wanted
                    if not target.exists():
                        with z.open(name) as src, open(target, "wb") as dst:
                            dst.write(src.read())
                    sources[weight] = target
                    print("extracted", wanted, target.stat().st_size)

    if len(sources) != 2:
        raise SystemExit(f"Missing fonts: {sources}")

    # Standard Latin + apostrophe + basic punctuation (incl. curly quotes used live)
    unicodes = [f"U+{c:04X}" for c in range(0x20, 0x7F)]
    for c in (0x00A0, 0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2026):
        unicodes.append(f"U+{c:04X}")
    unicodes_arg = ",".join(unicodes)

    total = 0
    for weight, src in sources.items():
        out = FONT_DIR / OUT_NAMES[weight]
        cmd = [
            sys.executable,
            "-m",
            "fontTools.subset",
            str(src),
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
        print("subsetting", src.name, "->", out.name)
        subprocess.check_call(cmd)
        size = out.stat().st_size
        total += size
        print(f"  {out.name}: {size} bytes ({size / 1024:.1f} KiB)")

    print(f"TOTAL subsetted: {total} bytes ({total / 1024:.1f} KiB)")


if __name__ == "__main__":
    main()
