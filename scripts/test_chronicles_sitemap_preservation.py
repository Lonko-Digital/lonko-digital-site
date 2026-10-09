"""A Chronicles rebuild must preserve unrelated authored sitemap dates."""
import tempfile
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET

from chronicles_lib import build


def main():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        sitemap = root / "sitemap-pages.xml"
        sitemap.write_text('''<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>https://lonkodigital.com/insights/clicks-but-no-leads/</loc><lastmod>2026-10-08</lastmod></url>
<url><loc>https://lonkodigital.com/insights/one-good-week-isnt-a-trend/</loc><lastmod>2026-10-07</lastmod></url>
</urlset>''', encoding="utf-8")
        with patch.object(build, "ROOT", root), patch.object(build, "_discover_insight_urls", return_value=[]):
            build.write_sitemaps([], 1)
            first = sitemap.read_bytes()
            build.write_sitemaps([], 1)
            assert sitemap.read_bytes() == first
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        entries = ET.fromstring(first).findall("sm:url", namespace)
        dates = {e.findtext("sm:loc", namespaces=namespace): e.findtext("sm:lastmod", namespaces=namespace) for e in entries}
        assert dates["https://lonkodigital.com/insights/clicks-but-no-leads/"] == "2026-10-08"
        assert dates["https://lonkodigital.com/insights/one-good-week-isnt-a-trend/"] == "2026-10-07"
    print("SITEMAP DATE PRESERVATION / REBUILD IDEMPOTENCE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
