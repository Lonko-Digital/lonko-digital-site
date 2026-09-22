# Lonko Chronicles — article presentation (live page)

**Status:** complete site presentation contract (permanent). Approved by Alex 2026-09-22 after Article #2 live-page corrections.  
**Canonical path:** `docs/chronicles/lonko-chronicles-article-presentation.md`  
**Implementation:** `assets/css/site.css` (`.chronicles-hero-figure`, `.chronicles-share*`); word-count strip in `scripts/chronicles_lib/render_md.py`

## Purpose

Chronicles article **layout/presentation** is shared site infrastructure — not a per-article redesign. Future articles inherit these rules automatically. Do not reopen them unless Alex explicitly changes the contract.

This covers the **rendered article page** (hero placement, spacing, Share row, public-facing metadata hygiene). Creative asset production (1600×900 hero export, etc.) remains governed by OS §57.

## Permanent presentation rules

### 1. Hero sits in the editorial column — not full-bleed

- Rendered hero max width: **`42rem` / `672px`**, centered.
- Below that breakpoint: fluid with normal gutters (`min(42rem, calc(100% - 2rem))`).
- Preserve the asset’s native aspect ratio (`width: 100%; height: auto` — do not force a crop in CSS).
- **Do not** stretch the hero to full browser/viewport width on desktop.
- Source hero files stay at production export size (default **1600×900**). Presentation width is CSS only — do not regenerate/resize the asset to “fix” layout.

### 2. Space between hero and body copy

- Leave clear breathing room under the banner before the first paragraph (~**2.5rem / 40px** bottom margin on `.chronicles-hero-figure`).
- Body text must not sit flush against the image.

### 3. Share row: one UI system

- Label (“SHARE”) and controls (Share / Copy link / Email / LinkedIn / X) must:
  - sit on **one vertically aligned row**;
  - use the same **UI sans** stack (`Segoe UI` / system UI), not the article serif;
  - not inherit global `h2` serif styling for the label.
- Footer links remain separate site chrome; Share is article chrome — keep Share self-consistent.

### 4. No internal editorial metadata in public HTML

- Never publish internal notes such as `(~1,150 words)` (or similar word-count lines) in the article body or after Sources.
- Reading time in the byline (`N min read`) is the public-facing duration signal.
- Packages that accidentally include a trailing word-count line are stripped at render time — still remove them from source packages when found.

## Live / PRE-PUBLISH visual checklist (fast)

Use after deploy — do **not** reinvent layout per article:

1. Hero is capped ~672px, centered; not edge-to-edge on desktop.
2. Visible gap between hero bottom and first body paragraph.
3. Share label + controls aligned; same sans font family.
4. No `(~N words)` or similar editorial leftovers visible.
5. Mobile: hero fluid with gutters; no forced 672px width.

## Ownership

| Role | Owns |
|---|---|
| Cursor Web | Shared CSS/template presentation; renderer hygiene; live visual QA when presentation defects appear |
| Claude Blog | Do not put internal word-count / production notes in public article body |
| Alex | Approves changes to this presentation contract |

## What not to do

- Full-bleed article heroes on desktop “because the asset is 1600px wide.”
- Per-article one-off hero width hacks when the shared rule is wrong — fix the shared CSS once.
- Baking layout fixes into regenerated image files.
- Letting package footnotes / word counts leak into live HTML.
