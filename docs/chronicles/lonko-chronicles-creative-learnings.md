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

**Issue:** Social-banner iterations used styled text and invented marks instead of faithfully using the actual Lonko logo.

**Decision:** Logo-bearing creative must composite the authoritative real logo asset. Default public-facing social/banner creative includes the authentic Lonko mark + text wordmark “Lonko Digital” unless Alex explicitly approves a logo-free exception.

**Reusable lesson:** A typed/generated company name, ring, geometric “L,” generic icon, approximate mark, or any model-invented symbol is not the Lonko logo. Wrong or missing logo = automatic reject.

**Applies to:** Social/public-facing creative requiring Lonko branding. Locked hero briefs that explicitly specify “no logo” remain logo-free.

**Production assets (this repo):** `assets/images/lonko-logo.png` (+ `.webp`). Compose with text wordmark “Lonko Digital” as the live site header does. See `docs/brand/lonko-brand-production-tokens.md`.

---

## L011 — Final output dimensions are hard production requirements

**Issue:** Article #1 creative was repeatedly treated as acceptable when it was only approximately the correct aspect ratio, while the actual social production requirement is an exact **1200×628** export.

**Decision:** Final asset dimensions are pass/fail production requirements, not suggestions. The default Chronicles social banner export is **1200×628**. The default article hero export is **1600×900** unless an article-specific brief explicitly overrides it before rendering.

**Reusable lesson:** “Essentially the right ratio” is acceptable for an intermediate photographic base, never for a final deliverable. Validate pixel dimensions before creative approval.

**Applies to:** Final hero/social exports and any derivative production asset.

---

## L012 — Lock the production contract before rendering

**Issue:** Article #1 entered rendering before every deterministic production detail was locked, causing avoidable rework around dimensions, colors, typography, and logo treatment.

**Decision:** Before the first render, the brief must explicitly lock: asset role, exact pixel dimensions, approved copy, brand HEX/RGB values, font stack and weight, authoritative logo asset, text/logo compositing method, and required output filename/format.

**Reusable lesson:** Do not start rendering while any deterministic production requirement is still described vaguely or is waiting to be discovered.

**Applies to:** Every hero, social banner, and branded editorial creative.

---

## L013 — Separate scene generation from deterministic brand compositing

**Issue:** The image model produced an orange/gold accent, serif typography, and an invented logo/wordmark when asked to render the full branded social asset.

**Decision:** Use image generation for the photographic/illustrative scene. Apply exact typography, logo assets, approved copy, and exact brand colors in a controlled compositing pass whenever fidelity matters.

**Reusable lesson:** Generate the story; composite the brand.

**Applies to:** Any public-facing creative with exact text, logos, or brand-token requirements.

---

## L014 — Freeze layers that already passed QA

**Issue:** Article #1 risked reopening accepted photography and editorial decisions while correcting unrelated brand-layer defects.

**Decision:** Once a layer passes QA, later revisions must be scoped only to the failed layer unless a genuine new defect is discovered.

**Reusable lesson:** Copy pass stays passed during image QA; photography pass stays passed during brand compositing; technical implementation does not reopen creative direction without a real defect.

**Applies to:** The full Chronicles production workflow.

---

## L015 — Brand assets are fail-closed

**Issue:** During Article #1's social-banner correction, the image-generation step created an approximate/redrawn Lonko-style mark instead of using the authoritative Lonko logo asset, even though the workflow explicitly required the real logo.

**Decision:** If an exact brand asset is required and the authoritative file is not actually available to the production step, stop that brand-compositing step. Do not approximate, redraw, infer, stylize, or ask an image model to create a substitute. Retrieve the real asset or ask Alex for it once, then resume.

**Reusable lesson:** No authoritative logo file = no logo-bearing final creative. Brand identity is fail-closed.

**Applies to:** Every Lonko public-facing asset containing the logo, wordmark, or any other exact brand mark.

---

## L016 — Status context is not execution authorization

**Issue:** A Claude status response saying Article #1 was waiting on Lonko Chronicles was misread as an instruction to generate the images immediately.

**Decision:** Mentions of pending creative work, current gates, or "waiting on Lonko Chronicles" are context only. The image-production workspace acts only when Alex explicitly instructs it to run the actual production prompt/brief.

**Reusable lesson:** Context can describe the next action without authorizing it. Require an explicit execution trigger before generating/editing/compositing images.

**Applies to:** All cross-role Chronicles handoffs and creative-production transitions.

---

## L017 — Human coherence is a pass/fail realism gate

**Issue:** A generated person can have a credible face while the hands, forearms, build, proportions, or posture look inconsistent with the rest of the same person, making the image feel visibly AI-generated.

**Decision:** Evaluate the full human subject as one coherent person — face, neck, shoulders, torso, arms, hands, posture, build, age cues, wardrobe, and role. When the brief specifies a woman or man, the entire subject must remain visually coherent with that intended person without caricature or stereotyped exaggeration.

**Reusable lesson:** A realistic face does not rescue mismatched anatomy. If body parts look like they belong to a different person, regenerate before delivery.

**Applies to:** Every generated image containing people.

---

## L018 — Alex should receive the finished standard, not the first QA pass

**Issue:** Avoidable defects were sometimes visible before delivery — weak topic fit, blurry/soft output, anatomy problems, incorrect logo treatment, approximate dimensions, or other known weaknesses — and were still surfaced for Alex to catch.

**Decision:** Run a strict internal quality gate before delivery. The production role must answer its own improvement questions, correct any material defect it can see, and only then hand the asset to Alex for final approval.

**Reusable lesson:** If we can see the problem, we fix it before Alex sees it. “Good enough” is not a delivery state.

**Applies to:** All Lonko images, banners, social creative, editorial visuals, and derivative assets.

---

## L019 — Topic relevance is a pass/fail creative requirement

**Issue:** A visually attractive image can still be weak if it only communicates a broad category rather than the exact article subject and angle.

**Decision:** Every creative must contain a defensible, quickly understandable relationship to the specific story. The scene, action, props, and emotional moment should support the article's actual subject rather than merely looking professional.

**Reusable lesson:** Beautiful but generic is a reject. The image must earn its place beside that exact article.

**Applies to:** Every Chronicles hero, social banner, and editorial creative.

---

## L020 — Approved assets live in the shared Google Drive handoff folder

**Issue:** An approved hero/social pair was saved to an internal ChatGPT Library path and handed to Claude Blog, but Claude Blog only had read access to the shared Google Drive production workspace and could not retrieve those files.

**Decision:** After Alex approves a final hero/social asset, the Lonko Chronicles production workspace must upload the file to the shared Google Drive **Approved Assets** folder before handoff.

**Canonical destination:**
- Folder: **Approved Assets**
- Folder ID: `1sGbYPmWpo-cSyFxhCi8HF9Rz3LOplV-P`
- URL: `https://drive.google.com/drive/folders/1sGbYPmWpo-cSyFxhCi8HF9Rz3LOplV-P`
- ChatGPT-visible Drive path: `/Google Drive/RF760626/Lonko Chronicles - Shared Production/Approved Assets/`

**Reusable lesson:** A file can be durable but still be inaccessible to the next role. Cross-role handoff is not complete until the approved asset exists in the shared Drive location Claude Blog can actually read. ChatGPT Library paths, sandbox paths, local/container paths, and other private-only locations are working locations, not final handoff locations.

**Applies to:** Every approved Chronicles hero, social banner, in-body image, or other creative asset that Claude Blog must retrieve.

## L021 — Chronicles GA4 is foundation, not a per-article rebuild

**Issue:** Article packages were treated as blocked on “GA4 implementation” even though GTM/GA4 were already live sitewide — because the shared Chronicles `dataLayer` event layer had never been built once.

**Decision:** Treat Chronicles measurement as permanent site infrastructure (§53.1). Shared events ship in the article template/JS; PRE-PUBLISH tracking QA is a fast health check. Only genuine *new* shared events require engineering.

**Reusable lesson:** Missing shared Chronicles tracking is an engineering foundation gap, not an editorial per-article gate to reinvent every post.

**Applies to:** All Chronicles publish-readiness assessments.

**Canonical record:** `docs/chronicles/lonko-chronicles-ga4-foundation.md`.

---

## Status

L001–L021 active as of 2026-09-21. Read this log before §57.16 step 3 / concept development, together with the Creative Registry and Legacy Creative Baseline (§57.17). For measurement gates, also read §53.1 / the GA4 foundation doc.
