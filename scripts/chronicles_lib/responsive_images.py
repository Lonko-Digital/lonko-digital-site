"""Build delivery derivatives without changing approved package masters."""
from pathlib import Path
import re
from PIL import Image

HERO_WIDTHS = (480, 800, 1200, 1600)
HERO_BYTE_BUDGET = 200_000


def derivative_path(rel: str, width: int) -> str:
    path = Path(rel)
    return (path.parent / f"{path.stem}-{width}.webp").as_posix()


def generate_images(package: Path, destination: Path, hero: str | None) -> None:
    for source in package.rglob("*"):
        if not source.is_file() or source.suffix.lower() not in (".png", ".jpg", ".jpeg"):
            continue
        rel = source.relative_to(package).as_posix()
        with Image.open(source) as image:
            width, height = image.size
            # Editorial charts and social masters get a lossless, full-size delivery
            # variant. Only the hero needs multiple display-density candidates.
            widths = sorted({min(w, width) for w in HERO_WIDTHS} | {width}) if rel == hero else [width]
            for candidate in widths:
                rendered = image if candidate == width else image.resize(
                    (candidate, round(height * candidate / width)), Image.Resampling.LANCZOS
                )
                target = destination / derivative_path(rel, candidate)
                target.parent.mkdir(parents=True, exist_ok=True)
                rendered.save(target, "WEBP", quality=82, method=6, lossless=rel != hero)
                if rel == hero and target.stat().st_size >= HERO_BYTE_BUDGET:
                    raise ValueError(f"Hero WebP exceeds 200 KB delivery budget: {target.name}")


def picture(img: str, rel: str, destination: Path, href, sizes: str) -> str:
    path = Path(rel)
    if "://" in rel or rel.startswith("/") or path.is_absolute() or ".." in path.parts:
        return img
    candidates = []
    for derivative in sorted((destination / path.parent).glob(f"{path.stem}-*.webp")):
        suffix = derivative.stem.removeprefix(f"{path.stem}-")
        if suffix.isdigit():
            candidates.append((int(suffix), derivative.relative_to(destination).as_posix()))
    # Reserve layout space for cards and older inline visuals as well as heroes.
    # Read real dimensions; never guess or change approved image bytes/alt text.
    intrinsic = destination / rel
    if not intrinsic.is_file() and candidates:
        intrinsic = destination / max(candidates)[1]
    if intrinsic.is_file() and re.search(r"<img\b", img):
        with Image.open(intrinsic) as source:
            width, height = source.size
        additions = ""
        if not re.search(r"\bwidth\s*=", img):
            additions += f' width="{width}"'
        if not re.search(r"\bheight\s*=", img):
            additions += f' height="{height}"'
        img = re.sub(r"<img\b", "<img" + additions, img, count=1)
    if not candidates:
        return img
    srcset = ", ".join(f"{href(candidate)} {width}w" for width, candidate in sorted(candidates))
    from .render_md import escape_text
    return f'<picture><source type="image/webp" srcset="{escape_text(srcset)}" sizes="{escape_text(sizes)}">{img}</picture>'
