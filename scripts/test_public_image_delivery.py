"""Verify image layout reservations, alt attributes and responsive hero budgets."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
from xml.etree import ElementTree as ET

from PIL import Image

from chronicles_lib.model import load_all_articles

ROOT = Path(__file__).resolve().parents[1]


class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            self.images.append(dict(attrs))


def main():
    ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = set()
    for name in ['sitemap-pages.xml', 'sitemap-chronicles.xml']:
        urls.update(e.text for e in ET.parse(ROOT / name).findall('.//sm:loc', ns))
    total = 0
    for url in urls:
        path = ROOT / urlsplit(url).path.lstrip('/') / 'index.html'
        parsed = Images()
        parsed.feed(path.read_text(encoding='utf-8'))
        for image in parsed.images:
            total += 1
            assert 'alt' in image, (url, image)
            width, height = int(image['width']), int(image['height'])
            assert width > 0 and height > 0, (url, image)
            src = urlsplit(image['src'])
            if src.scheme or src.netloc:
                continue
            asset = ROOT / unquote(src.path).lstrip('/') if src.path.startswith('/') else path.parent / unquote(src.path)
            with Image.open(asset) as file:
                assert abs(width / height - file.width / file.height) < .01, (url, image)
    articles = load_all_articles(ROOT / 'chronicles/content')
    for article in articles:
        if article.status != 'published':
            continue
        directory = ROOT / 'chronicles' / article.slug / Path(article.hero_image).parent
        stem = Path(article.hero_image).stem
        for width in [480, 800, 1200, 1600]:
            candidate = directory / f'{stem}-{width}.webp'
            assert candidate.is_file() and candidate.stat().st_size < 200_000, candidate
        html = (directory.parent / 'index.html').read_text(encoding='utf-8')
        assert 'type="image/webp"' in html and 'srcset=' in html and 'sizes=' in html
    print(f'PUBLIC IMAGE DIMENSIONS / ALT ATTRIBUTES / HERO DELIVERY: PASS ({total} image tags)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
