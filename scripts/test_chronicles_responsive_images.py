"""Regression coverage for cross-article cards and approved image delivery."""
import hashlib
import sys
import tempfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chronicles_lib import build
from chronicles_lib.model import load_all_articles
from chronicles_lib.responsive_images import generate_images, picture


def main():
    articles = load_all_articles(build.CONTENT)
    target = next(a for a in articles if a.slug == "google-ads-ai-max-migration-what-changed")
    for depth, prefix in ((0, "chronicles/"), (1, ""), (2, "../"), (3, "../../")):
        card = build.story_card(target, variant="compact", depth=depth)
        assert f'src="{prefix}{target.slug}/{target.hero_image}"' in card, (depth, card)
        assert 'width="1600"' in card and 'height="900"' in card
    with tempfile.TemporaryDirectory() as temp:
        package, output = Path(temp) / "package", Path(temp) / "output"
        package.mkdir()
        output.mkdir()
        Image.new("RGB", (1600, 900), "navy").save(package / "hero.png")
        Image.new("RGB", (2400, 1534), "white").save(package / "chart.png")
        original = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in package.iterdir()}
        generate_images(package, output, "hero.png")
        for width in (480, 800, 1200, 1600):
            with Image.open(output / f"hero-{width}.webp") as candidate:
                assert candidate.size == (width, round(width * 900 / 1600))
        with Image.open(output / "chart-2400.webp") as candidate:
            assert candidate.size == (2400, 1534)
            assert candidate.tobytes() == Image.open(package / "chart.png").tobytes()
        assert original == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in package.iterdir()}
        result = picture('<img src="hero.png" alt="Approved">', "hero.png", output, lambda p: "../target/" + p, "100vw")
        assert 'type="image/webp"' in result and 'sizes="100vw"' in result
        assert '../target/hero-480.webp 480w' in result
        assert 'width="1600" height="900"' in result and 'src="hero.png" alt="Approved"' in result
        assert picture("original", "missing.png", output, lambda p: p, "100vw") == "original"
        # A future detailed image must fail the delivery gate if it cannot meet
        # the budget at the established quality; do not silently ship a huge hero.
        Image.effect_noise((1600, 900), 100).convert('RGB').save(package / 'hero.png')
        try:
            generate_images(package, output, 'hero.png')
        except ValueError as error:
            assert '200 KB delivery budget' in str(error)
        else:
            raise AssertionError('Oversized hero must fail the build')
    for article in articles:
        if article.status == 'published' and article.hero_image:
            stem = Path(article.hero_image).stem
            for candidate in (build.OUT / article.slug / 'assets').glob(f'{stem}-*.webp'):
                assert candidate.stat().st_size < 200_000, candidate
    print("RESPONSIVE IMAGES / RELATED CARD PATHS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
