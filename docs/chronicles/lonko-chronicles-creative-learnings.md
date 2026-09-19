# Lonko Chronicles — Creative Learnings Log

**Canonical path:** `docs/chronicles/lonko-chronicles-creative-learnings.md`

Living record of **reusable creative lessons** approved by Alex (+ ChatGPT review where noted).
Governed by the Visual Creative System in
`docs/chronicles/lonko-chronicles-operating-system.md` §57 (especially §57.18).

Exact production color/type/logo values live in
`docs/brand/lonko-brand-production-tokens.md` — not duplicated here.

**Format:** one entry per lesson. Lessons are permanent until Alex supersedes them.
This is not a CMS and is not loaded by the site build.

---

## L001 — Chart is evidence, not the social banner

**Issue:** Early Article #1 iterations treated the Whitespark/data chart as if it could serve as the LinkedIn/Meta stop-scroll creative.

**Decision:** Alex rejected chart-as-banner. The chart remains an **in-article data visualization** only.

**Reusable lesson:** A chart proves a claim; a social banner earns attention and human connection. Do not promote an evidence graphic to the feed creative just because the data is strong.

**Applies to:** Any article that includes charts, tables, or annotated screenshots.

---

## L002 — Dedicated hero and dedicated social banner

**Issue:** Risk of shipping one image cropped two ways for hero and social.

**Decision:** Article #1 (and future Chronicles packages) require **independent** `hero_image` and `social_image` assets with distinct jobs.

**Reusable lesson:** Hero = editorial storytelling for the article page. Social = stronger stop-scroll feed object. Separate files, separate QA.

**Applies to:** Every published Chronicles package with imagery.

---

## L003 — Do not bake the article H1 into the hero by default

**Issue:** Baking large headline text into the hero fights the HTML headline and responsive layout.

**Decision:** Article hero keeps minimal baked-in text; the real headline stays in HTML.

**Reusable lesson:** Hero imagery supports the story; it does not replace the page title.

**Applies to:** Article heroes (social banners may use on-image headline treatment when needed).

---

## L004 — Topic-first: lifestyle alone is not enough

**Issue:** Attractive lifestyle frames can pass aesthetics while failing article relevance.

**Decision:** Every concept must answer: “What in this image tells the viewer why it belongs with **this** article?” (§57.2).

**Reusable lesson:** Require defensible Topic + Human/outcome + Lonko brand signals — not decoration.

**Applies to:** All hero/social concept rounds.

---

## L005 — Three Different Worlds, not wardrobe swaps

**Issue:** Concept rounds that only change the person in the same café/scene fail anti-repetition and creative energy.

**Decision:** Enforce §57.8 — at least three **materially different** visual worlds before selecting.

**Reusable lesson:** If three concepts could be produced by swapping the person in essentially the same photograph, the round has failed.

**Applies to:** Pre-generation concept development.

---

## L006 — Realism over AI-art spectacle

**Issue:** Generated imagery drifts toward plastic skin, neon, holograms, and “look what the model can do.”

**Decision:** Apply §57.9 realism bar — would a skilled commercial photographer plausibly have captured this?

**Reusable lesson:** Prefer candid commercial photography energy; reject obvious AI-art clichés in post-generation QA.

**Applies to:** All generated or heavily composited human/lifestyle creative.

---

## L007 — Quality DNA, not scene DNA

**Issue:** Brand consistency can be misunderstood as repeating the same person, café, lake, or family setup.

**Decision:** Repeat Lonko’s identity, quality, tone, typography discipline, color system, and emotional promise — **not** the same scene cast (§57.15).

**Reusable lesson:** Recognizably Lonko, never predictable. Check the Creative Registry before proposing near-duplicates.

**Applies to:** Anti-repetition review before every new concept round.

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

L001–L010 active as of 2026-09-19. Read this log before §57.16 step 3 / concept development.
