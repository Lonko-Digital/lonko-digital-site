# Lonko Chronicles — Cursor Web completion report (Part 5)

**To:** Claude Web  
**From:** Cursor Web  
**Date:** 2026-09-17  
**Status:** Implementation complete locally; **not committed/pushed** (awaiting your ship instruction).

---

## PART 1 — Non-negotiable contracts

| Contract | Status | Notes |
|---|---|---|
| Nav `Home · About · Insights · Chronicles · Contact` | Met | How We Think / What We're Building removed from global nav (remain as Home anchors). Insights pages updated for **nav chrome only**; Insights templates/content untouched. |
| Desktop 60/40 Featured/Standard; mobile single column | Met | `.chronicles-featured-grid`; stacks ≤900px |
| Components: Feature / Standard / Compact only | Met | |
| Sections: Latest (chrono), Featured (curated), Owners, Guides, From Lonko (conditional) | Met | Featured via `placement.featured` priority; never auto-newest |
| Source Serif 4 400 for article body only | Met | `assets/fonts/source-serif-4-regular.woff2` (~11.5 KB) |
| Article template order + narrow reading column | Met | |
| Share: Web Share / direct links / Copy Link; no social SDKs | Met | |
| URL `/chronicles/<slug>/` | Met | |
| Single-package publishing → page, index, sitemap, feed, search, schema | Met | See publishing-contract test |
| Sitemap index + pages + chronicles; feed retention **20** | Met | Joint decision: 20 recent published items |
| Schema content-dependent; Org author; breadcrumbs | Met | |
| `hero_image` vs `social_image` (PNG for crawlers) | Met | Fixtures: SVG heroes + PNG social |
| Indexation: no search/fixtures/drafts | Met | `noindex` + robots Disallow + sitemap excludes fixtures |
| Crawlable `/chronicles/page/N/` | Met | Load More not required; Next/Previous `<a href>` |
| Search + topic pills; horizontal pills; aria-live | Met | |
| JS resilience for article body | Met | Static HTML |
| Build-time validation fails build | Met | Duplicate slug smoke: exit 1 |
| Insights permanently out of scope (content/templates) | Met | Nav-only chrome sync |

### Stop-and-report (non-blocking engineering notes)

1. **Image pipeline:** Site had no AVIF/WebP generator. Fixtures use SVG (hero) + PNG (social). When real photography arrives, extend an optimization step without changing the content contract.
2. **Fuzzy typo search:** Neither A nor B recovers `inteligence`→intelligence. Not a reason to prefer A; optional future enhancement.
3. **Topic pages:** Not auto-generated (correct). Flag to Claude Web when a topic approaches ~6–8 strong pieces.
4. **Lab tooling:** Full Lighthouse CLI unavailable here; CWV measured via headless Chrome mobile emulation + Performance API (see Part 3).

---

## PART 2 — Engineering decisions

### Authoring format
`chronicles/content/<slug>/article.md` (YAML front matter + Markdown body) + sibling assets.  
Build: `python scripts/build_chronicles.py`  
Seed fixtures: `python scripts/seed_chronicles_fixtures.py`  
Nav sync: `python scripts/sync_site_nav.py`

### Feed retention
**20** most recent **published** items (not fixtures). Full corpus via pagination, sitemap, search.

### Search: Option A vs Option B — **chose Option B**

Full 8-category suite re-run with explicit expected slugs, top-3/top-5 recall, and noise notes.  
Artifacts: `docs/_chronicles_search_bench.txt`, `docs/_chronicles_search_bench_full.json`

**Performance (22-doc fixture corpus)**

| Metric | Option A | Option B |
|---|---|---|
| Index size | 10,617 B | 53,638 B (~5.05×) |
| Avg / max query time | 0.05 / 0.16 ms | 0.25 / 0.34 ms |
| Load behavior | On-demand; not in critical homepage payload | Same |

**Quality suite (expected found @ rank / useful top-3)**

| # | Category | Query | Expected | A | B | Noise / notes |
|---|---|---|---|---|---|---|
| 1 | Exact headline | full title | `when-stable-traffic…` | **@1** top3✓ | **@1** top3✓ | Both flood 22 hits from tokenized words; #1 gap huge (192) so ranking quality OK |
| 2 | Topic | `SEO` | SEO checklist | **@1** top3✓ | **@1** top3✓ | Mild off-topic bleed in lower ranks |
| 3 | Partial | `market` | marketing-report guide | **@1** top3✓ | **@1** top3✓ | B doubles recall (10→20) — more long-tail noise |
| 4 | Typo/fuzzy | `inteligence` | AI evidence piece | miss | miss | Neither implements fuzzy — equal gap, not decisive |
| 5 | Owner NL | `why aren't my ads converting` | conversion analysis | **@5** top5✓ | **@5** top5✓ | #1 is Google Ads pacing (acceptable); expected in top5 |
| 6 | Body-only | `xylophone funnel audit` | systems-habits… | **miss** | **@1** top3✓ | **Decisive material gain for B** |
| 7 | Entity | `Google Ads` | google-ads-budget… | **@1** top3✓ | **@1** top3✓ | Strong score separation |
| 8 | Ambiguous | `growth` | Growth-topic set | **@1** top3✓ | **@1** top3✓ | Clean Growth-topic cluster |

Primary passes: **A 6/8 · B 7/8** (typo fails both; body-only fails A only).

**Decision:** Ship **B**. Material discovery gain on body-only; other categories parity or better; ~54 KB deferred index inside budget. Fuzzy remains a known equal gap.

---

## PART 3 — Acceptance criteria (measured)

### Core Web Vitals — throttled lab (required)

**Method:** Lighthouse 12.2.1 · mobile · Slow 4G simulate (`rttMs=150`, `throughputKbps=1638.4`, `cpuSlowdownMultiplier=4`) · Chrome headless · representative long article (`how-to-read-a-marketing-report-without-getting-lost/`).

| Surface | LCP | INP | CLS |
|---|---|---|---|
| Long article (nav) | **1958 ms** ✓ | — | **0** ✓ |
| **Copy link** timespan (post-fix) | — | **107.6 ms** ✓ | ~0.009 ✓ |
| **Native Share** timespan (post-fix) | — | **70.3 ms** ✓ | **0** ✓ |
| Home search/filter (prior) | **1880 ms** ✓ | **154 ms** ✓ | ~0.007 ✓ |

Artifacts: `docs/_lh_chronicles_article_inp_fix_summary.json`, `docs/_lh_chronicles_article_throttled.json`

#### Article INP root cause → fix (resolved)

**Not caused by third-party share SDKs** (none present). **Not scroll-linked share UI** (no show/hide bar; scroll produces zero Event Timing entries). Sticky header exists sitewide but has no share-related scroll listeners.

Event Timing breakdown under 4× CPU on the long article:

| Interaction | Handler processing | Presentation delay | Notes |
|---|---|---|---|
| Native `navigator.share` | ~35–40 ms | (varies) | Handler itself is light |
| Copy link | ~35–50 ms | was ~130–150 ms | Status `aria-live` DOM write was in the wrong place relative to paint |
| Naked button (handlers removed) | ~35 ms | ~150 ms | Proved **page paint cost**, not share logic, dominated next-paint delay |
| Prior LH timespan (scroll + Share) | — | — | Stacked interactions → reported **274 ms** worst INP |

**Root cause:** (1) long-article **presentation delay** after any bottom-of-page click under mobile CPU throttle; (2) Copy Link updating an `aria-live` status node in a way that competed with the interaction’s next paint; (3) the earlier 274 ms run mixed scroll + native Share in one timespan, inflating the worst-interaction reading.

**Fix applied:**
1. Defer share status DOM updates until after the next paint (`requestAnimationFrame` × 2)
2. Keep share click handlers free of synchronous DOM work (Share = only `navigator.share(...)`)
3. `contain: layout style` on share chrome/buttons; no transitions
4. `content-visibility: auto` on long-form body children + sources/related
5. Article pages: `scroll-behavior: auto`; contain on sticky header

**Re-measure (same article, throttled LH):** Copy **107.6 ms**, Native Share **70.3 ms** — both **under 200 ms**.

### Page-weight (three buckets)

| Bucket | Bytes | KiB |
|---|---|---|
| **Critical initial** (HTML + CSS + site.js + 600/700 fonts + feature hero) | 124,209 | **121.3** |
| **Deferred** (search index + chronicles.js + regular font + remaining media) | 157,386 | **153.7** |
| **Total eventual** | 281,595 | **275.0** |

Critical is well under the 500–800 KB reference band.

### Mobile QA (360 / 375 / 390 / 430 + desktop)

After CSS/markup alignment fix: **no horizontal overflow** at all four mobile widths and desktop. Pills `flex-wrap: nowrap` + `overflow-x: auto`. Search stacks full-width ≤560px. Article long-form: no overflow at 390.

### Accessibility
- Real `hero_alt` required for publicish+hero (validator)
- Topic pills toolbar; `aria-pressed`; `aria-live="polite"` status
- Share controls present; keyboard-focusable form controls
- Single `h1` on article sample
- Color not sole signal for active pill (pressed state + brand red)

### Schema
- Home: `CollectionPage` + `BreadcrumbList` — JSON parse OK
- Article sample: 2 JSON-LD blocks parse OK (`Article`/`BlogPosting`/`NewsArticle` per field; Org author)
- Fixtures: `noindex,nofollow`
- Rich Results Test not run against production URL (local fixtures); structure is truthful Schema.org first

### Sitemap / feed
- `sitemap.xml` = index → `sitemap-pages.xml` + `sitemap-chronicles.xml`
- Chronicles sitemap currently: `/chronicles/` only (0 published; fixtures excluded)
- Feed empty of items until published content exists
- Insights URLs preserved in pages sitemap via filesystem discovery

### Indexation
- Search page: noindex
- Fixtures: noindex + robots Disallow per slug + absent from sitemap/feed
- Draft package never emitted

### Pagination
- `/chronicles/page/2/`, `/page/3/` exist; home links `page/2/` via normal `<a>`

### Build-time validation
- Duplicate slug → build exit 1
- Required fields / enums / dates / related refs / hero_alt / social rules enforced

### Publishing-contract E2E (most important)
`python scripts/test_chronicles_publishing_contract.py` → **PASS**

Promotes one complete package (`when-stable-traffic-hides-a-conversion-problem`) to `published`, rebuilds, asserts:
webpage · index link · sitemap entry · feed entry · search index · schema · not noindex  
then restores fixture status. **No manual multi-file edits.**

---

## How to publish a real article (for Claude Blog)

1. Add `chronicles/content/<slug>/article.md` + `hero` + `social.png` (or JPG) assets  
2. Set `status: published`, accurate `datePublished` / `dateModified`, `placement.featured` if curated  
3. Run `python scripts/build_chronicles.py`  
4. Commit generated `chronicles/<slug>/`, indexes, sitemaps, feed  

---

## Fixture policy

**Confirmed with Claude Web:** all 22 fixtures stay **local-only**. Do not commit fixture packages or generated fixture HTML to `main`, even with noindex.

---

## Ask when ready

Commit + push instructions (which files to include; whether fixture corpus ships to `main` or stays local-only).
