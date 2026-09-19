"""HTML shell helpers matching the existing Lonko Digital site."""

from __future__ import annotations

import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

THEME_FOUC = """  <script>
    (function(){try{var k='lonko-public-appearance',p=localStorage.getItem(k)||'system',d=window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';document.documentElement.setAttribute('data-theme',p==='system'?d:p);}catch(e){}}());
  </script>
"""

NAV_ITEMS = (
    ("Home", ""),
    ("About", "about/"),
    ("Insights", "insights/"),
    ("Chronicles", "chronicles/"),
    ("Contact", "contact/"),
)


def asset_prefix(depth: int) -> str:
    """Relative prefix from a page at `depth` directory levels below site root."""
    if depth <= 0:
        return ""
    return "../" * depth


def read_gtm_head() -> str:
    path = ROOT / "includes" / "gtm-head.html"
    if path.is_file():
        return path.read_text(encoding="utf-8").rstrip() + "\n"
    return (
        "<!-- Google Tag Manager -->\n"
        "<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':\n"
        "new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],\n"
        "j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=\n"
        "'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);\n"
        "})(window,document,'script','dataLayer','GTM-53DPJ88F');</script>\n"
        "<!-- End Google Tag Manager -->\n"
    )


def read_gtm_body() -> str:
    path = ROOT / "includes" / "gtm-body.html"
    if path.is_file():
        return path.read_text(encoding="utf-8").rstrip() + "\n"
    return (
        "<!-- Google Tag Manager (noscript) -->\n"
        '<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-53DPJ88F"\n'
        'height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>\n'
        "<!-- End Google Tag Manager (noscript) -->\n"
    )


def font_preloads(depth: int, *, include_regular: bool = False) -> str:
    p = asset_prefix(depth)
    lines = [
        f'  <link rel="preload" href="{p}assets/fonts/source-serif-4-bold.woff2" as="font" type="font/woff2" crossorigin>',
        f'  <link rel="preload" href="{p}assets/fonts/source-serif-4-semibold.woff2" as="font" type="font/woff2" crossorigin>',
    ]
    if include_regular:
        lines.append(
            f'  <link rel="preload" href="{p}assets/fonts/source-serif-4-regular.woff2" as="font" type="font/woff2" crossorigin>'
        )
    return "\n".join(lines) + "\n"


def nav_html(depth: int, *, current: str | None = None) -> str:
    """Primary nav. Items ONLY: Home, About, Insights, Chronicles, Contact.

    depth: 0=root, 1=chronicles/, 2=chronicles/slug or chronicles/page/N or search/.
    For deeper paths (e.g. chronicles/page/2/), pass the real filesystem depth.
    """
    p = asset_prefix(depth)
    items: list[str] = []
    for label, href in NAV_ITEMS:
        if href == "":
            link = p if p else "./"
        else:
            link = f"{p}{href}"
        # Current page highlighting
        is_current = current is not None and current.lower() == label.lower()
        # When on a chronicles subpage, Chronicles is still current
        if current is None and label == "Chronicles" and depth >= 1:
            # caller should pass current="Chronicles" explicitly; leave unset if not
            pass
        aria = ' aria-current="page"' if is_current else ""
        items.append(f'          <li><a href="{link}"{aria}>{html.escape(label)}</a></li>')
    ul = "\n".join(items)
    return f"""      <nav id="site-nav" class="site-nav" aria-label="Primary">
        <ul>
{ul}
        </ul>
      </nav>
"""


def header_html(depth: int, *, current: str | None = None) -> str:
    p = asset_prefix(depth)
    brand_href = p if p else "./"
    logo = f"{p}assets/images/lonko-logo"
    return f"""  <a class="skip-link" href="#main">Skip to main content</a>
  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="{brand_href}">
        <picture>
          <source srcset="{logo}.webp" type="image/webp">
          <img class="brand-logo" src="{logo}.png" alt="" width="36" height="36" decoding="async">
        </picture>
        <span>Lonko Digital</span>
      </a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Open navigation menu"><span class="nav-toggle-icon" aria-hidden="true"><span class="nav-toggle-line"></span><span class="nav-toggle-line"></span><span class="nav-toggle-line"></span></span></button>
{nav_html(depth, current=current).rstrip()}
      <div class="header-actions">
        <button id="theme-toggle" class="theme-toggle" type="button" aria-label="Switch to dark theme">Theme</button>
      </div>
    </div>
  </header>
"""


def footer_html(depth: int) -> str:
    p = asset_prefix(depth)
    return f"""  <footer class="site-footer">
    <div class="container footer-grid">
      <div class="footer-brand">
        <p class="footer-name">Lonko Digital</p>
        <p class="footer-tag">Marketing intelligence for clearer business decisions.</p>
        <p class="footer-copy">&copy; <span id="year"></span> Lonko Digital. All rights reserved.</p>
      </div>
      <nav class="footer-links" aria-label="Footer">
        <a href="{p}about/">About</a>
        <a href="{p}privacy/">Privacy Policy</a>
        <a href="{p}terms/">Terms of Use</a>
        <a href="{p}contact/">Contact</a>
      </nav>
    </div>
  </footer>
  <script>document.getElementById('year').textContent = new Date().getFullYear();</script>
"""


def favicon_links(depth: int) -> str:
    p = asset_prefix(depth)
    return (
        f'  <link rel="icon" href="{p}assets/images/favicon.ico" sizes="any">\n'
        f'  <link rel="icon" href="{p}assets/images/lonko-logo.png" type="image/png" sizes="72x72">\n'
    )


def head_open(
    *,
    depth: int,
    title: str,
    description: str,
    canonical: str,
    og_title: str | None = None,
    og_description: str | None = None,
    og_image: str | None = None,
    og_image_width: int | None = None,
    og_image_height: int | None = None,
    og_type: str = "website",
    robots: str | None = None,
    extra_head: str = "",
    include_regular_font: bool = False,
    json_ld_blocks: list[str] | None = None,
) -> str:
    """Build opening <!DOCTYPE>…</head><body>…GTM body with shared meta."""
    og_title = og_title or title
    og_description = og_description or description
    og_image = og_image or "https://lonkodigital.com/assets/images/og-share.png"
    p = asset_prefix(depth)
    robots_tag = f'  <meta name="robots" content="{html.escape(robots)}">\n' if robots else ""
    ld = ""
    for block in json_ld_blocks or []:
        ld += f'  <script type="application/ld+json">\n  {block}\n  </script>\n'

    og_size_meta = ""
    if og_image_width and og_image_height and og_image_width > 0 and og_image_height > 0:
        og_size_meta = (
            f'  <meta property="og:image:width" content="{int(og_image_width)}">\n'
            f'  <meta property="og:image:height" content="{int(og_image_height)}">\n'
        )

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
{favicon_links(depth)}{read_gtm_head()}  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}">
{robots_tag}  <link rel="canonical" href="{html.escape(canonical)}">
  <meta property="og:title" content="{html.escape(og_title)}">
  <meta property="og:description" content="{html.escape(og_description)}">
  <meta property="og:type" content="{html.escape(og_type)}">
  <meta property="og:url" content="{html.escape(canonical)}">
  <meta property="og:site_name" content="Lonko Digital">
  <meta property="og:image" content="{html.escape(og_image)}">
{og_size_meta}  <meta property="og:image:alt" content="{html.escape(og_title)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(og_title)}">
  <meta name="twitter:description" content="{html.escape(og_description)}">
  <meta name="twitter:image" content="{html.escape(og_image)}">
{ld}{THEME_FOUC}{font_preloads(depth, include_regular=include_regular_font)}  <link rel="stylesheet" href="{p}assets/css/site.css">
{extra_head}</head>
<body>
{read_gtm_body()}"""


def scripts_close(depth: int, *, extra_scripts: list[str] | None = None) -> str:
    p = asset_prefix(depth)
    parts = [footer_html(depth).rstrip()]
    parts.append(f'  <script src="{p}assets/js/site.js"></script>')
    for src in extra_scripts or []:
        parts.append(f'  <script src="{src}"></script>')
    parts.append("</body>")
    parts.append("</html>")
    return "\n".join(parts) + "\n"
