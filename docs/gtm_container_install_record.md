# GTM Container Install Record — Lonko Digital Public Site

**Container ID:** `GTM-53DPJ88F`  
**Scope:** Public company website (`lonko-digital-site`) only  

### Current live status (updated 2026-08-22)

Container install remains sitewide. **Tags are now configured and firing** through the published container (confirmed via live `gtm.js` inspection). As of this update:

| Tag | ID |
| --- | --- |
| Google Analytics 4 (GA4) | `G-Y8T0Q59191` |
| Google Ads tag | `AW-18390009990` |
| LinkedIn Insight Tag | Partner ID `10662377` |
| GA4 Event `site_click` | Measurement ID `G-Y8T0Q59191` |
| GA4 Event `site_scroll_depth` | Measurement ID `G-Y8T0Q59191` |

No Meta Pixel is configured. Public description of these tags: [Privacy Policy](../privacy/).

---

## Original install note (2026-08-15)

**Status at install:** Installed and validated in local source — container-only; no analytics/advertising tags configured inside GTM at that time.

---

## Pre-install inspection

| Item | Finding |
| --- | --- |
| Architecture | Static multi-page HTML (GitHub Pages). No React/Next/Eleventy/Jekyll layout (`.nojekyll` present). |
| Shared template | None. Pages are standalone HTML. |
| Existing GTM | **None** (source + live site at install time) |
| Existing gtag.js / GA4 / Google Ads AW | **None** |
| Meta Pixel / LinkedIn Insight | **None** |
| Other scripts | Theme preference bootstrap (`lonko-public-appearance`) + `assets/js/site.js` (nav/theme only) |

**Conflict check:** No duplicate Google tagging risk. Proceeded with install.

---

## Implementation approach

Because there is no shared layout engine, the official GTM snippets are kept as a single source of truth and synced into every public HTML page:

| Path | Role |
| --- | --- |
| `includes/gtm-head.html` | Canonical `<head>` GTM `<script>` |
| `includes/gtm-body.html` | Canonical `<body>` GTM `<noscript>` |
| `scripts/sync_gtm_snippets.py` | Applies includes to all pages; asserts one container install per page |

Official Google placement used:

- Head script immediately after charset + viewport (as high as practical)
- Noscript iframe immediately after `<body>`

At install time, **no** Google Ads, GA4, Meta, LinkedIn, or conversion tags were added in source HTML. Tag configuration lives in the GTM container UI / published container, not as hard-coded vendor snippets in page HTML.

---

## Pages receiving GTM-53DPJ88F

| Page | Head script | Noscript after `<body>` | `GTM-53DPJ88F` refs |
| --- | --- | --- | --- |
| `index.html` | Yes | Yes (immediate) | 2 (one install) |
| `404.html` | Yes | Yes (immediate) | 2 |
| `about/index.html` | Yes | Yes (immediate) | 2 |
| `contact/index.html` | Yes | Yes (immediate) | 2 |
| `privacy/index.html` | Yes | Yes (immediate) | 2 |
| `terms/index.html` | Yes | Yes (immediate) | 2 |

Every public HTML page receives exactly one GTM-53DPJ88F installation (script + noscript).

---

## Files changed (original install)

- `includes/gtm-head.html` *(created)*
- `includes/gtm-body.html` *(created)*
- `scripts/sync_gtm_snippets.py` *(created)*
- `scripts/public_safety_audit.py` *(dotenv pattern tightened — see below)*
- `index.html`
- `404.html`
- `about/index.html`
- `contact/index.html`
- `privacy/index.html` *(GTM snippet at install; policy later updated 2026-08-22 to describe live tags)*
- `terms/index.html`
- `docs/gtm_container_install_record.md` *(this file)*

**Not changed at install:** private `marketing-agent/` platform; site CSS; layout; SEO; navigation.

---

## public_safety_audit.py behavior (post-GTM hardening)

**Approach:** file-aware, not a globally weakened dotenv regex.

1. **Universal credential checks** (all scanned files): named secret-key assignments (api key / client secret / access token / refresh token / oauth token|secret / secret key / private key) with optional spaces and quotes; Bearer tokens; AWS access keys; PEM private key blocks; Google OAuth client IDs; LinkedIn client ID assignments; Google Ads customer IDs; personal-email domains; localhost URLs (docs exempt).
2. **Dotenv-style `KEY = value` scanning** only for dotenv-context files (names starting with `.env`, ending in `.env`, `env.example`, `*.env.example`, bare `*.example` that are not JSON). Not applied to HTML, JS, or Python source.
3. **`tests/` is not scanned** by the CLI (regression fixtures intentionally contain secret-shaped strings).
4. GTM / normal `ROOT = Path(...)` / `height="0"` are not special-cased allowlists — they simply fall outside the dotenv file context and do not match named-secret key patterns.

See `tests/test_public_safety_audit.py` for regression coverage.

---

## Validation performed

Local source (all 6 HTML pages) at install:

- [x] `GTM-53DPJ88F` present exactly **twice** per page (script + noscript)
- [x] Exactly one head block and one noscript block per page
- [x] Head snippet inside `<head>`; noscript immediately after `<body>`
- [x] No hard-coded Google Ads / GA4 / Meta / LinkedIn vendor snippets introduced in HTML (tags managed in GTM)
- [x] `python scripts/public_safety_audit.py` — **PASS**
- [x] `python scripts/sync_gtm_snippets.py` — **OK** (idempotent)

Live container inspection (2026-08-22): published `gtm.js` for `GTM-53DPJ88F` includes GA4, Google Ads, LinkedIn Insight, and the two GA4 custom events listed above.

---

## Privacy Policy

Updated **2026-08-22** so public wording matches the live tags (GA4, Google Ads tag, LinkedIn Insight Tag). Effective date on the Privacy Policy page: August 22, 2026. Cookie-consent / CMP decisions remain a separate attorney-review item and are out of scope for this documentation update.

---

## Stop line

GTM foundation remains installed sitewide. Live container currently fires GA4, a Google Ads tag, and a LinkedIn Insight Tag as documented above. Do not edit GTM from this repo without an explicit tracking/governance task.
