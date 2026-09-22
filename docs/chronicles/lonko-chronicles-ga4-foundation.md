# Lonko Chronicles — GA4 / dataLayer foundation

**Status:** complete site infrastructure (permanent). Built once; reused by every article.  
**Site `dataLayer`:** shipped 2026-09-21. **GTM → GA4 tags:** verified live in `GTM-53DPJ88F` on 2026-09-22.  
**Canonical path:** `docs/chronicles/lonko-chronicles-ga4-foundation.md`  
**Related:** Operating System §53; `docs/gtm_container_install_record.md`

## Purpose

Chronicles measurement must **never** be a per-article engineering blocker.

GTM (`GTM-53DPJ88F`) and GA4 (`G-Y8T0Q59191`) are already live sitewide. This document defines the **reusable Chronicles event layer** that article pages push into `dataLayer`. Claude Blog does not invent a new GA4 setup for each post. Cursor Web does not rebuild tracking per article unless Claude requests a **genuine new event** beyond this shared set.

## Permanent operating model

| Gate | Who | When |
|---|---|---|
| **Chronicles GA4 foundation** (this doc + site JS) | Cursor Web | Once (before first Chronicles article live) |
| **GTM → GA4 event tags** for the shared events | Alex / GTM Admin | Once (map `dataLayer` events → GA4) |
| **Article creative + package** | Claude Blog | Every article |
| **PRE-PUBLISH tracking QA** | Cursor Web | Confirm foundation still healthy (fast checklist) — not a rebuild |
| **Alex APPROVED FOR PUBLICATION** | Alex | Every article |
| **POST-PUBLISH verify** | Cursor Web | After release |

After foundation + one-time GTM mapping:

- Claude writes the article and notes any *extra* measurement needs only.
- Alex approves content/creative.
- Publish does **not** wait for new GA4 engineering unless Claude requests a genuine new shared event.

## Shared event architecture

All events fire only on Chronicles **article** pages (`data-chronicles-page="article"`).  
Common parameters on every push: `article_slug`, `content_group: "chronicles"`.

| Event | When | Extra parameters |
|---|---|---|
| `chronicles_scroll_depth` | Reader crosses 25 / 50 / 75 / 90% once each | `scroll_percent` |
| `chronicles_share` | Share control used | `share_method` (`native` \| `copy` \| `email` \| `facebook` \| `instagram` \| `linkedin` \| `x`) |
| `chronicles_outbound_source_click` | Click on a Sources & Further Reading link | `link_url`, `link_text` |
| `chronicles_internal_link_click` | Same-origin click in article body or Related Stories | `link_url`, `link_text` |
| `chronicles_to_site_nav` | Primary nav or brand click leaving toward other site sections | `nav_label`, `link_url` |

Implementation: `scripts/chronicles_lib/build.py` → emitted as `chronicles/assets/chronicles.js` (measurement block activates only when the article marker is present).

### Coexistence with sitewide events

Do **not** replace or rename existing site events (`site_click`, `site_scroll_depth`). Chronicles events are **additive** and article-scoped. Prefer Chronicles events for content-performance analysis; use sitewide events for whole-site behavior. Avoid designing per-article vanity events that duplicate these five.

## GTM Admin checklist (one-time)

In container `GTM-53DPJ88F`, create GA4 Event tags → measurement ID `G-Y8T0Q59191` for each event name above. Trigger on Custom Event matching the `event` name. Forward parameters as GA4 event parameters / custom dimensions as needed:

- `article_slug`
- `scroll_percent`
- `share_method`
- `link_url` / `link_text`
- `nav_label`
- `content_group`

Publish the container. Record completion in `docs/gtm_container_install_record.md`.

**Done (2026-09-22):** shared event tags are present in the published container. Remaining per-article work is the fast PRE-PUBLISH health check only.

## PRE-PUBLISH tracking QA (fast checklist)

Use this every article — do **not** rebuild tracking:

1. Article HTML includes `data-chronicles-page="article"` and `data-article-slug`.
2. `chronicles.js` loads on the article page.
3. In Tag Assistant / preview: scrolling fires `chronicles_scroll_depth` at thresholds once each.
4. Share / source / related / nav clicks push the expected events.
5. No per-article one-off event names unless Alex approved a foundation extension.

## What not to do

- Invent per-article GA4 setups or one-off event names for routine posts.
- Make Alex manually rebuild tags for each post.
- Treat a measurement **specification** as completed **implementation**.
- Leave Chronicles tracking as a recurring Claude Blog publish blocker.
- Duplicate Enhanced Measurement / `site_scroll_depth` under a new vanity name for the same meaning without a clear analysis reason.

## Ownership

| Role | Owns |
|---|---|
| Claude Blog | Measurement *requirements* for major initiatives; flag only *new* events beyond this set |
| Cursor Web | Site `dataLayer` implementation, template wiring, PRE/POST publish QA checklists |
| Alex / GTM Admin | GTM container tags, GA4 custom dimensions, container publish |
| Alex | Final publication authorization |
