# Lonko Chronicles — Creative Learnings Log

**Canonical path:** `docs/chronicles/lonko-chronicles-creative-learnings.md`

Living record of **reusable creative lessons** approved by Alex (+ ChatGPT review where noted).
Governed by the Visual Creative System in
`docs/chronicles/lonko-chronicles-operating-system.md` §57 (especially §57.18).

Exact production color/type/logo values live in
`docs/brand/lonko-brand-production-tokens.md` — not duplicated here.

**Three separate records (never merge):**

| Record | Purpose |
|---|---|
| Creative Registry | Approved assets (with CR IDs) |
| Legacy Creative Baseline (§57.17) | Pre-§57 visual territory (no CR IDs) |
| Creative Learnings Log (this file) | Reusable mistakes / lessons |

**Governance test for new entries:** Would remembering this lesson materially reduce the chance that a future creative round repeats a known mistake? If yes: log it. If no: keep it article-specific.

**Format:** one entry per lesson. Lessons are permanent until Alex supersedes them.
This is not a CMS and is not loaded by the site build.

---

## L001 — Empty registry ≠ blank creative history

**Issue:** The first creative round treated the new empty Creative Registry as if Lonko had no existing visual history.

**Decision:** Creative concepting must consider the Legacy Creative Baseline as well as the Registry.

**Reusable lesson:** An empty current registry never overrides known historical creative territory.

**Applies to:** All future Chronicles/social creative.

---

## L002 — Person swap is not meaningful variation

**Issue:** A different ethnicity, age, gender, or individual can leave the underlying creative concept essentially unchanged.

**Decision:** Variation must come from story, environment, activity, composition, emotional interpretation, viewpoint, device use, or format — not casting alone.

**Reusable lesson:** Different person ≠ different creative world.

**Applies to:** All future visual concepting.

---

## L003 — Avoid artificial digital topic signals

**Issue:** Early concepts used glowing map pins, floating UI, and screen glows to communicate what a device/search experience meant.

**Decision:** Prefer real human situations and plausible physical behavior over digital overlays.

**Reusable lesson:** If the topic can be communicated through what is actually happening in the scene, do that instead of adding artificial UI/effects.

**Applies to:** Photography-style hero/social creative.

---

## L004 — Topic action cannot be ambiguous

**Issue:** “Person grabs keys and walks toward the door” could mean work, errands, school pickup, shopping, or many unrelated activities.

**Decision:** The local-intent panel was revised to show an actual interaction with a local service professional arriving.

**Reusable lesson:** A visual should not require the caption to explain the key topic signal when the human situation itself can make it clear.

**Applies to:** Topic-led hero and social creative.

---

## L005 — Banner vs chart roles

**Issue:** Article #1's earlier chart-based visualization was being used as both evidence and promotional creative.

**Decision:** Banner and chart are separate jobs.

**Reusable lesson:** Banner earns attention. Chart earns trust. Hero/social creative primarily communicates story, relevance, emotion, and attention. Charts/graphs/data visualization primarily communicate evidence and understanding inside the article.

**Applies to:** Chronicles.

---

## L006 — Do not force extra data visualization

**Issue:** Article #1 could technically support an Ahrefs 34.5%-vs-58% visual.

**Decision:** Do not build it because the prose already explains the evidence clearly and a two-point chart could imply a continuous trend from two separate studies.

**Reusable lesson:** Only add charts when they materially improve comprehension and faithfully represent the evidence structure.

**Applies to:** All evidence-led Chronicles content.

---

## L007 — In-scene branding must not imply fabricated real relationship

**Issue:** Early concepting considered placing Lonko brand accents/signage on service vehicles/storefronts that could imply a real Lonko client relationship.

**Decision:** Brand signal comes from post-production color/typography treatment, not branding on people, businesses, or vehicles standing in for a general scenario.

**Reusable lesson:** Illustrating a general phenomenon is different from claiming a real customer case study; imagery must not blur that line.

**Applies to:** Any hero/social creative featuring a business, employee, or service professional as a stand-in for a general scenario.

---

## L008 — Exact brand colors, not descriptive color names

**Issue:** Generated assets drifted to orange/gold despite prompts saying “Lonko red.”

**Decision:** Brand-dependent creative prompts/specs must carry the actual production value.

**Reusable lesson:** Use exact verified color values such as `#e10600`, not only descriptive labels such as “Lonko red.”

**Applies to:** Any generated/composited creative using Lonko brand color.

**Production values:** see `docs/brand/lonko-brand-production-tokens.md` (`--brand-red` `#e10600`).

---

## L009 — Exact typography, not general style descriptions

**Issue:** The Article #1 social banner rendered an editorial serif despite the brief requesting a “clean modern sans-serif.”

**Decision:** Brand-dependent text treatments must reference the actual production font stack and weight.

**Reusable lesson:** Use the verified UI stack and explicit weight rather than vague wording like “modern sans-serif.”

**Applies to:** Any branded on-image copy.

**Production values:** UI sans
`"Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif`
at weight **700** for social-banner headlines — see `docs/brand/lonko-brand-production-tokens.md`.

---

## L010 — Real logo asset, never generated substitute

**Issue:** The social banner generated “LONKO DIGITAL” as styled text instead of using the actual Lonko logo mark.

**Decision:** Logo-bearing creative must composite an authoritative logo asset.

**Reusable lesson:** A typed/generated company name is not a substitute for the real logo mark.

**Applies to:** Social/public-facing creative requiring Lonko branding.

**Production assets (this repo):** `assets/images/lonko-logo.png` (+ `.webp`). Compose with text wordmark “Lonko Digital” as the live site header does. See `docs/brand/lonko-brand-production-tokens.md`.

---

## Status

L001–L010 active as of 2026-09-19. Read this log before §57.16 step 3 / concept development, together with the Creative Registry and Legacy Creative Baseline (§57.17).
