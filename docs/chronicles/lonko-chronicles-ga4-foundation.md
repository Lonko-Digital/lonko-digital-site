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
| **Chronicles GA4 foundation** (this doc + site JS) | Cursor Web | Once (infrastructure) |
| **GTM → GA4 event tags** for the shared events | Alex / GTM Admin | Once |
| **Article creative + package** | Claude Blog | Every article |
| **Automated page-marker assertions** | Cursor CI / production-contract tests | Every PR/preview build |
| **Hosted preview + deploy + live verify** | Cursor Web | Every article (normal publishing path) |
| **Alex APPROVED FOR PUBLICATION** | Alex | Every article |

After foundation + one-time GTM mapping:

- Claude writes the article and notes any *extra* measurement needs only.
- Normal articles inherit shared events automatically — no per-article GA4 engineering.
- Cursor verifies wiring via automated tests + deploy verification, not a separate redesign project.

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

## PRE-PUBLISH tracking QA (automated + light human)

Prefer automated assertions (production-contract tests) that article HTML includes the shared measurement markers. Claude confirms editorial measurement intent only when requesting a *new* shared event. Cursor Web changes GA4/GTM infrastructure only when intentionally requested — not as a per-article project.

Optional human Tag Assistant check on the **hosted preview** (not production-first) remains available but is not a Cursor babysitting gate.

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
| Cursor Web | Site `dataLayer` implementation, template wiring, CI assertions, deploy verification |
| Alex / GTM Admin | GTM container tags, GA4 custom dimensions, container publish |
| Alex | Final publication authorization |
