# Lonko Brand — Production Tokens (verified)

**Purpose:** Lightweight reference of **actual production values** extracted from the
Lonko Digital public website codebase. For creative/editorial teams (Claude Blog)
and engineering. **Not** a second design system.

**Verified:** 2026-09-19 from `lonko-digital-site` production CSS/assets.  
**Do not invent values.** If a token is missing here, inspect the source file.

---

## 1. Core colors

Source: `assets/css/site.css` (`:root` / `[data-theme="light"]`, lines 3–23).

| Role | Token | HEX | RGB | Production use |
|---|---|---|---|---|
| Primary Lonko red | `--brand-red` | `#e10600` | `rgb(225, 6, 0)` | CTAs, active nav, semantic left-border accents |
| Brand red hover | `--brand-red-hover` | `#c00500` | `rgb(192, 5, 0)` | Primary button hover only |
| Brand black / near-black | `--brand-black` | `#0b0b0f` | `rgb(11, 11, 15)` | Skip-link bg; dark theme page bg; shadow base |
| White (literal) | *(no token; hardcoded)* | `#ffffff` / `#fff` | `rgb(255, 255, 255)` | Primary CTA text on red; elevated surfaces |
| Page background (off-white) | `--bg` | `#f7f8fa` | `rgb(247, 248, 250)` | Light theme body background |
| Elevated surface | `--bg-elevated` | `#ffffff` | `rgb(255, 255, 255)` | Cards, header base |
| Body text | `--text` | `#1a1d24` | `rgb(26, 29, 36)` | Primary copy (light theme) |
| Muted text | `--text-muted` | `#5c6370` | `rgb(92, 99, 112)` | Secondary copy |
| Border | `--border` | `#dfe3ea` | `rgb(223, 227, 234)` | Dividers, card edges |

### Which red for creative?

Use **`--brand-red` / `#e10600` / `rgb(225, 6, 0)`** for:

- Article hero divider lines
- Social-banner headline accents
- Social-banner brand treatment accents

Use `--brand-red-hover` (`#c00500`) **only** if mirroring a hover/pressed UI state — not for static creative.

### Overlay / scrim

**No dedicated `--scrim` / overlay token exists** in production CSS.

Nearest encoded near-black for dark overlays: `--brand-black` `#0b0b0f`.  
Header uses translucent elevated surface (`color-mix(... 92%, transparent)`), not a branded photo scrim. Overlay **opacity is not encoded** — creative must choose opacity without claiming a production token.

---

## 2. Semantic red rule (from implementation)

Encoded comments in `assets/css/site.css`:

- Line 106: `/* K1: inline links are neutral; red reserved for CTA / active nav / rare emphasis */`
- Line 2170 (Chronicles scope): `Brand red only for CTAs, active pills, and semantic highlights.`

**How the site applies it:**

- Red is **not** used for ordinary body links.
- Red **is** used for: `.btn-primary`, active nav (`aria-current="page"`), active pills, and **semantic left borders** (`border-left: 3px solid var(--brand-red)` on pull quotes / north-star / Chronicles blockquotes).

**Policy for promotional/editorial social creative:**

The repo encodes a **website UI** restraint rule. It does **not** encode an explicit ban on restrained brand-red use in social/editorial imagery. Thin red dividers and selective red headline emphasis are **consistent** with existing semantic left-border / brand-accent patterns (`3px solid var(--brand-red)`).

---

## 3. Typography

Source: `assets/css/site.css` (`@font-face` + `body` / `h1,h2` / Chronicles body).

| Surface | Family | Fallbacks | Weights in production |
|---|---|---|---|
| UI / nav / body (site chrome) | `Segoe UI` | `system-ui, -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif` | 500, 600, 650, 700, 800 (context-dependent) |
| Site H1/H2 + Chronicles card titles | `Source Serif 4` | `Georgia, "Times New Roman", serif` | 600, 700 (self-hosted woff2) |
| Chronicles article body | `Source Serif 4` | `Georgia, serif` | 400 (self-hosted regular) |
| Buttons / CTAs | inherits UI sans (`Segoe UI` stack) | same as body | **600** (`.btn`) |

Font files:

- `assets/fonts/source-serif-4-regular.woff2` (400)
- `assets/fonts/source-serif-4-semibold.woff2` (600)
- `assets/fonts/source-serif-4-bold.woff2` (700)

### Social banner headline recommendation

Use the **UI / brand wordmark stack**, not article serif:

- **Family:** `"Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif`
- **Weight:** `700` (matches `.brand` wordmark weight) or `600` (matches `.btn`)

Do **not** default social-banner headlines to Source Serif 4 unless the creative brief explicitly wants editorial-article voice.

---

## 4. Logo assets

### Public site (this repo)

| Asset | Path | Format | Intrinsic size | Role |
|---|---|---|---|---|
| Logo mark (header/favicon) | `assets/images/lonko-logo.png` | PNG | **72×72** | Header mark + favicon |
| Logo mark (WebP) | `assets/images/lonko-logo.webp` | WebP | **72×72** | Header `<picture>` source |
| Default OG share | `assets/images/og-share.png` | PNG | **1200×630** | Site-wide social fallback (not the logo) |

### Higher-resolution mark (NOT in this GitHub repository)

A larger approved mark also exists **outside** `Lonko-Digital/lonko-digital-site`:

| Asset | Location | Format | Intrinsic size |
|---|---|---|---|
| Approved Alex mark (hi-res) | Local sibling project `marketing-agent/static/brand/lonko-logo.png` | PNG | **1024×1044** |

**Important:** That path is **not** part of the public website GitHub repo. Do not document it as a `lonko-digital-site` path. For high-res creative compositing, use the sibling file from the local Lonko platform workspace (or copy bytes into the article package `assets/`). The **canonical in-repo** logo files remain `assets/images/lonko-logo.png` and `.webp` only.

Noted historically in `docs/public_showcase/linkedin/README.md` (public site ships the small display copy).

### What exists / does not exist (this repo)

| Variant | Status |
|---|---|
| Mark / icon only | **Exists** (headdress on black) — `assets/images/lonko-logo.png` |
| Combined mark + wordmark file | **Does not exist** as a single image |
| Light / reversed logo file | **Does not exist** in this repo |
| Dark / full-color mark | The production mark **is** dark-ground (black bg) — suitable on dark overlays |
| SVG logo | **Does not exist** |

### How the production header/footer actually brand

- **Header:** `<img class="brand-logo" src="…/lonko-logo.png">` + adjacent HTML text **`Lonko Digital`** (`.brand` → `font-weight: 700`, UI sans stack). See `scripts/chronicles_lib/shell.py` `header_html()` and `index.html`.
- **Footer:** text-only name (`.footer-name`), no logo image.

### Recommended social-banner brand treatment

1. Place the **real mark** from `assets/images/lonko-logo.png` (or a hi-res copy sourced from the sibling `marketing-agent` project into the package — never invent a path inside this repo that does not exist).
2. Set the wordmark as text **“Lonko Digital”** in the UI sans stack at weight **700** — matching production header composition.
3. Do **not** generate a fake “LONKO DIGITAL” wordmark inside the image model.

---

## 5. Article #1 — exact brand application (production values only)

Approved headline (unchanged):  
**One Search Wants an Answer. The Other Wants a Business.**

### Hero

| Element | Value |
|---|---|
| Divider color | `#e10600` / `rgb(225, 6, 0)` / `var(--brand-red)` |
| Divider width | **3px** (matches production semantic `border-left: 3px solid var(--brand-red)`) |

Do not change photography, crop, or structure.

### Social banner

| Element | Value |
|---|---|
| Headline font | `"Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif` |
| Headline weight | `700` |
| White text | `#ffffff` / `rgb(255, 255, 255)` |
| Red accent | `#e10600` / `rgb(225, 6, 0)` |
| Overlay/scrim base | `#0b0b0f` / `rgb(11, 11, 15)` (`--brand-black`); **opacity not tokenized** |
| Logo mark path (this repo) | `assets/images/lonko-logo.png` |
| Logo mark (hi-res, sibling project only) | Local `marketing-agent/static/brand/lonko-logo.png` — **not** in this GitHub repo |
| Wordmark | Text “Lonko Digital” (not a generated glyph); weight 700 |
| Placement | Bottom-right mark + wordmark, matching header pairing |

---

## 6. Creative-prompt hygiene (supports L008–L010)

When briefing image tools:

1. **Colors:** pass exact HEX/RGB (`#e10600`), never “Lonko red” / “brand orange.”
2. **Type:** pass the exact Segoe UI stack + weight, never “modern sans-serif.”
3. **Logo:** composite the real `lonko-logo` asset + text wordmark; never ask the model to invent the logo.

---

## 7. Source index

| Fact | Source |
|---|---|
| Color tokens | `assets/css/site.css` `:root` |
| Semantic red comments | `assets/css/site.css` ~L106, ~L2170 |
| 3px red borders | `.north-star-quote`, `.chronicles-article-body blockquote`, etc. |
| Typography | `assets/css/site.css` `@font-face`, `body`, `h1,h2`, `.btn`, `.brand` |
| Header logo wiring | `scripts/chronicles_lib/shell.py`, `index.html` |
| Public logo files (this repo) | `assets/images/lonko-logo.png`, `.webp` |
| Hi-res approved mark (sibling local project) | `marketing-agent/static/brand/lonko-logo.png` — outside this GitHub repo |
| Logo provenance note | `docs/public_showcase/linkedin/README.md` |
