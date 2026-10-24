"""Approved B-5 metadata and repeated-image alt fidelity regression."""
from html.parser import HTMLParser
import html
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TITLES = {
    "local-services-ads-new-billing-rules-what-changed": "Google Local Services Ads: New Billing Rules (2026)",
    "google-conversion-lift-small-business-eligibility": "Google Conversion Lift: Can Small Businesses Qualify?",
    "chatgpt-ads-small-business-what-changed": "ChatGPT Ads for Small Business: What's Proven (2026)"
}
ALTS = {
    "meta-product-browsing-opt-out-hero-1600x900.png": "Small business owner taping a shipping box at a packing table while checking her phone",
    "chatgpt-ads-small-business-what-changed-hero-1600x900.png": "Small business owner on a sunlit porch reading a printed one-page comparison sheet, laptop closed",
    "local-services-ads-new-billing-rules-what-changed-hero-1600x900.png": "Business owner at her desk circling a line on a printed Google Local Services Ads billing statement",
    "google-conversion-lift-small-business-eligibility-hero-1600x900.png": "Small shop owner behind a velvet rope looking toward ad measurement dashboards just out of reach",
    "ai-overviews-local-search-what-changed-hero-1600x900.png": "Homeowner researching at his kitchen table, then greeting a local service pro at his front door",
    "google-ads-ai-max-migration-what-changed-hero-1600x900.png": "Contractor in a truck cab at a job site glancing at a phone notification",
    "google-conversion-lift-small-business-eligibility-chart-budget-threshold-comparison.png": "Chart: $5,000 Conversion Lift minimum vs 52% of small businesses spending under $1,000 a month",
    "ai-overviews-local-search-what-changed-chart-local-pack-vs-ai-overview.png": "Chart: Local Pack on 93% of local searches; AI Overviews on 92% of informational, 97% of hybrid"
}


class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []
    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.items.append(dict(attrs))


def main():
    pages = [ROOT / "index.html", *ROOT.glob("*/index.html"),
             *(ROOT / "insights").glob("*/index.html"),
             *(ROOT / "chronicles").glob("*/index.html")]
    seen = set()
    for path in pages:
        page = path.read_text(encoding="utf-8")
        title = html.unescape(re.search(r"<title>(.*?)</title>", page, re.S).group(1))
        assert len(title) <= 60, (path, title)
        parser = Images()
        parser.feed(page)
        for image in parser.items:
            name = image["src"].rsplit("/", 1)[-1]
            if name in ALTS:
                assert image["alt"] == ALTS[name], (path, name)
                assert len(image["alt"]) <= 100
                seen.add(name)
    assert seen == set(ALTS)
    for slug, expected in TITLES.items():
        page = (ROOT / "chronicles" / slug / "index.html").read_text(encoding="utf-8")
        assert html.unescape(re.search(r"<title>(.*?)</title>", page).group(1)) == expected
    listing = (ROOT / "chronicles/index.html").read_text(encoding="utf-8")
    assert "<title>Lonko Chronicles | Marketing News and Analysis</title>" in listing
    description = re.search(r'<meta name="description" content="([^"]+)">', listing).group(1)
    assert description == "Lonko Chronicles: evidence-led analysis of Google Ads, Meta, LinkedIn and AI search changes, and what each one means for your business and budget."
    assert 140 <= len(description) <= 155
    print("B-5 APPROVED TITLES / LISTING METADATA / REPEATED ALTS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
