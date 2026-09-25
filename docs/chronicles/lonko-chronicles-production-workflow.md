# Lonko Chronicles — Standard Article + Social Production Workflow

**Status:** Active canonical cross-role workflow.

**Purpose:** Define the normal end-to-end operating path for launching a Lonko Chronicles article and its LinkedIn/Meta distribution without making Alex act as the project manager or file courier.

**Audience:** Alex, Claude Blog Post & Social Media, Lonko Chronicles image-production chat, Cursor Web, and any future role supporting Chronicles.

**Authority:** This file is the canonical cross-role workflow. Role-specific operating documents may add detail, but they must not contradict this workflow unless Alex explicitly changes it.

### Governance freshness rule

**GitHub is the canonical operational source. Google Drive copies are readable mirrors only.** Before Image Production applies a permanent rule, it should prefer the current repository versions of:

- `docs/chronicles/chronicles-article-contract.yaml`;
- `chronicles/state.json`;
- `docs/chronicles/lonko-chronicles-production-workflow.md`;
- `docs/brand/lonko-brand-production-tokens.md`;
- `docs/chronicles/lonko-chronicles-creative-learnings.md`;
- `docs/chronicles/lonko-chronicles-creative-registry.md`.

When a Drive mirror exposes a repo path / workflow version / sync marker, compare it with canonical GitHub. A mirror known to be stale must never override newer canonical governance. If GitHub is unavailable and a mirror is known or suspected to conflict with newer governance, **fail closed on the conflicting permanent requirement** rather than confidently applying the stale copy. Do not create a competing source of truth.

---

## 1. The normal starting point

Alex should be able to begin a publishing cycle with one sentence to **Claude Blog Post & Social Media**:

> “I want to launch a blog post.”

Alex is not expected to arrive with a topic, headline, image, keyword, or finished brief.

Claude Blog owns the process from that point and should proactively move the work through the correct stages, asking Alex only for decisions that genuinely require his judgment.

---

## 1A. Active-article gate — finish the current launch before starting another

Before topic discovery, Claude Blog must check whether a Chronicles article is already **in production and not yet published**.

**Default rule: one active launch at a time.**

If an unpublished active article exists and Alex says:

> “I want to launch a blog post.”

that means **continue the active article toward publication**, not begin discovery for a second article.

Claude Blog should immediately state the active article and its current gate, then continue from that gate.

Example:

> “Article #1 is already in production and is waiting on final hero/social approval. I’ll continue that launch rather than start Article #2.”

Do **not** research, draft, concept, or start production on another article unless Alex explicitly says something like:

- “Start the next article too.”
- “Let’s work on Article #2 while Article #1 is finishing.”
- “Pause the current article and start a new one.”

Topic ideas may remain in the backlog/roadmap, but backlog ideas are not active production.

This rule exists to prevent parallel work from creating unnecessary handoffs, version confusion, unfinished launches, and extra project-management work for Alex.

---

## 2. Topic discovery comes before visual production

**No image generation begins until the topic and editorial angle are understood and explicitly approved by Alex.**

Claude Blog first:

1. researches current and evergreen opportunities;
2. checks audience relevance;
3. checks existing Chronicles content and the separate Insights property for cannibalization risk;
4. checks evidence strength, search intent, social potential, and Lonko relevance;
5. for any timely/current candidate, verifies material factual claims against current sources and includes the supporting source links/references in the topic proposal; if credible sources disagree, identify the disagreement instead of presenting one version as settled;
6. presents the strongest topic options with clear reasoning;
7. discusses the options with Alex;
8. records the topic/angle Alex approves.

Only after that approval does visual production begin.

The image must serve the agreed article. The article must never be forced to fit an image that was generated too early.

---

## 3. Claude Blog owns editorial, SEO, social, and creative direction

After Alex approves the topic/angle, Claude Blog proceeds with the article package:

- research and source review;
- article structure and writing;
- fact checking;
- SEO and AI-search strategy;
- title, deck, slug, metadata, internal links, schema requirements;
- source dossier;
- LinkedIn post copy;
- Meta post copy;
- measurement requirements;
- supporting evidence visuals/charts when genuinely useful;
- visual concepting for the article hero and social banner.

Claude Blog remains the **Creative Director** even though it is not the routine image renderer.

Before generating any image, Claude Blog must follow the Visual Creative System and check:

- Creative Registry;
- Legacy Creative Baseline;
- Creative Learnings Log.

Claude Blog develops at least three materially different visual worlds when §57 requires it, recommends the strongest concept, aligns with Alex, and then locks the production contract.

---

## 4. Claude Blog creates one complete Lonko Chronicles image-production prompt

Once the visual concept is agreed, Claude Blog gives Alex **one complete, copy-paste-ready prompt** addressed to the **Lonko Chronicles** image-production chat.

Alex should not have to rewrite, supplement, or remember production requirements.

The prompt must begin with the explicit execution directive:

> **ACTION: EXECUTE HERO + SOCIAL PRODUCTION NOW**

When Alex pastes a complete prompt containing that directive into the Image Production chat, **that single paste is execution authorization**. Alex does not need a second “run it” / “go ahead” message.

The prompt must include, at minimum:

- final article title/topic and short explanation of what the story is actually about;
- final article slug;
- audience and intended emotional/business takeaway;
- approved visual concept;
- exact hero requirements;
- exact social-banner requirements;
- exact on-image copy, if any;
- scene-generation instructions;
- deterministic brand-compositing instructions where exact text/logo/color fidelity matters;
- anti-repetition / realism / no-fake-UI requirements;
- acceptance criteria;
- requested output format;
- any deliberate permanent-rule override labeled exactly **ALEX-APPROVED EXCEPTION**.

Claude may echo permanent production constants for readability/checksum purposes, but it does not redefine them.

### 4A. Canonical-contract precedence

The production handoff has two authority layers:

- **Article-specific creative decisions:** Claude Blog's approved production prompt is authoritative.
- **Permanent production constants:** canonical GitHub governance is authoritative.

Permanent constants include at minimum: hero/social dimensions, Lonko brand red, logo policy, permanent typography rules, filename pattern, asset lifecycle/storage, and freeze/preservation rules.

If Claude accidentally echoes a conflicting permanent value, Image Production must **not silently follow it**. Stop that conflicting instruction, normalize to the canonical value, and report the discrepancy. A permanent-rule override is valid only when the production prompt clearly labels it **ALEX-APPROVED EXCEPTION**. Never infer an exception.

Default final dimensions are hard requirements:

- **Article hero: 1600×900 px**
- **Social banner: 1200×628 px**

unless Alex explicitly approves a different specification before rendering.

---

## 4B. Handoff execution gate — a status update is not an image-production order

The Lonko Chronicles image-production workspace must distinguish between **context/status** and an **actionable production handoff**.

**Do not generate, edit, composite, save, or move image assets merely because Alex pastes a Claude response that mentions image work, says an image is pending, or says Claude is waiting on Lonko Chronicles.** That is context only.

Image production begins only from an actionable production handoff. The standard handoff contains the actual Claude-authored production prompt beginning with:

> **ACTION: EXECUTE HERO + SOCIAL PRODUCTION NOW**

When Alex pastes that complete prompt, **the paste itself authorizes execution**. No second confirmation message is required. A status/planning/next-step message without the execution directive remains non-actionable.

The actionable handoff contains the locked article-specific production contract and is preflighted against canonical permanent production rules before any render begins.

If Alex pastes a Claude status message without the actual production brief, the Lonko Chronicles workspace should:

1. identify it as a status/context handoff;
2. **not create any image**;
3. tell Alex what the current gate is;
4. ask only for the already-created production prompt if it is not present/accessible.

If the production prompt is already available in shared project/Drive context, the workspace may retrieve it rather than making Alex reconstruct it, but execution still requires the explicit production directive from Alex's actionable handoff.

**Approval gate:** keep four states separate: (A) candidate shown for review, (B) visually acceptable feedback, (C) final image approval, and (D) publication approval. “Looks good” or similar casual feedback does not automatically promote files unless the surrounding context clearly constitutes final image approval. Final image approval is never the same as **APPROVED FOR PUBLICATION**. Generated/revised assets remain drafts until Alex explicitly approves the final hero/social assets; only then may they be moved/copied into Approved Assets and labeled ALEX-APPROVED FINAL ASSETS.

This rule prevents accidental production from status memos and keeps Alex in control of every creative execution/approval transition.

---

## 5. Lonko Chronicles owns image production

Alex copies Claude Blog’s prompt into the dedicated **Lonko Chronicles** image-production chat.

Lonko Chronicles then:

1. reads and follows the approved brief;
2. creates the article hero;
3. creates the social banner;
4. validates exact final dimensions;
5. uses image generation for scene creation/editing;
6. uses controlled/deterministic compositing for exact logo, typography, approved copy, and exact brand colors where needed;
7. does not reopen the article topic or creative direction unless it discovers a genuine defect or impossible requirement.

### 5A. Image-production preflight

Before rendering, Image Production must:

1. confirm the explicit execution directive is present;
2. resolve the slug and derive the normal final filenames:
   - `<slug>-hero-1600x900.png`
   - `<slug>-social-1200x628.png`;
3. resolve permanent constants from canonical GitHub governance;
4. compare any echoed prompt constants against canonical values;
5. resolve the authoritative high-resolution Lonko logo from the shared Brand Assets location when branding is required;
6. separate generated scene layers from deterministic text/logo/color layers;
7. fail closed on any unresolved condition listed in §5C below.

### 5B. Frozen-base persistence

For any candidate actually shown to Alex, persist enough source state to support narrow corrections reliably. Do **not** upload every rejected generation experiment.

When relevant, preserve in the shared **Draft Assets** workspace:

- the exact passed scene/base image;
- the review candidate actually shown to Alex;
- deterministic copy inputs from the locked prompt;
- the authoritative logo/composite input reference;
- the exact crop/composition embodied in the frozen base.

The practical rule is: **persist the image layer itself at the exact crop/composition that passed.** If social photography passes but typography fails, the next revision must rebuild the social composite from that exact frozen social scene rather than regenerating the subject, environment, lighting, composition, or hero.

Draft storage is working-state storage only. It is not approval.

### 5C. Image-production fail-closed conditions

Stop rather than improvise when any of the following applies:

- authoritative logo required but unavailable;
- article slug missing;
- exact social copy missing or ambiguous;
- requested dimensions conflict with canonical rules without an **ALEX-APPROVED EXCEPTION**;
- brand color conflicts with canonical rules without an approved exception;
- required reference asset missing;
- a frozen correction base is required but unavailable;
- generated fake Lonko branding appears;
- meaningful fabricated UI appears;
- the image implies an unsupported real customer/client relationship;
- final dimensions fail;
- filename/slug/asset-role validation fails;
- exact on-image text fails;
- logo fidelity fails;
- final files are not verified in Approved Assets after final image approval;
- Alex has not explicitly approved final images;
- the message is status/context rather than a real execution order.

Alex reviews the generated assets in Lonko Chronicles.

If Alex requests changes, Lonko Chronicles revises them there until Alex approves the final assets.

Passed layers stay frozen. A typography or logo correction does not reopen approved photography without a genuine new defect.

---

## 6. Approved image handoff — Alex is not the file courier

Once Alex approves both images, Lonko Chronicles must:

1. save the approved hero and social banner to the **shared Google Drive Approved Assets folder** that Claude Blog can read:
   - Folder name: **Approved Assets**
   - Folder ID: `1sGbYPmWpo-cSyFxhCi8HF9Rz3LOplV-P`
   - Canonical folder URL: `https://drive.google.com/drive/folders/1sGbYPmWpo-cSyFxhCi8HF9Rz3LOplV-P`
   - Current Library/Drive path when visible to ChatGPT: `/Google Drive/RF760626/Lonko Chronicles - Shared Production/Approved Assets/`
2. use stable, meaningful filenames tied to the article slug;
3. return the exact canonical filenames after confirming the uploads succeeded in that folder;
4. clearly mark them as **ALEX-APPROVED FINAL ASSETS**.

**Hard storage rule:** ChatGPT Library paths, sandbox paths, local container paths, or other private/internal locations are **not valid cross-role handoff locations** for approved Chronicles assets. They may be used for temporary working files only. The final approved files must be uploaded to the Google Drive **Approved Assets** folder above before telling Claude Blog they are ready.

Example naming convention:

- `<article-slug>-hero-1600x900.png`
- `<article-slug>-social-1200x628.png`

**Do not rely on temporary chat sandbox paths as the cross-role handoff.**

Alex should not need to download the files and upload them to Claude or Cursor manually.

After upload, Image Production must verify the exact final files in Approved Assets and return an **authoritative asset receipt**, not filenames alone. Include, where available:

- article slug;
- hero filename;
- hero Drive file ID;
- hero dimensions;
- hero format;
- social filename;
- social Drive file ID;
- social dimensions;
- social format;
- Creative Registry IDs once assigned;
- approval state;
- Approved Assets folder/location;
- checksum/hash or other stable version indicator when tooling exposes one.

Never invent a checksum. Drive file ID + exact filename + dimensions + format + approval state is an acceptable stable identity when no checksum is available.

Claude Blog and Cursor Web retrieve the approved files directly from the shared location using the receipt. Alex does not move, rename, or relay binary files.

If Approved Assets contains similarly named candidates or duplicates, Image Production must not guess. Resolve the exact approved Drive file IDs/version identity before handoff; ask Alex only if a genuine approval ambiguity remains.

If the shared location is ever unavailable to one of the roles, that is an infrastructure/setup defect to fix once — not a recurring manual-download workflow for Alex.

---

## 7. Claude Blog performs final visual QA

After retrieving the two Alex-approved images, Claude Blog checks the actual files against the original brief and §57.

Claude verifies, as applicable:

- correct article/topic relationship;
- correct concept;
- realism and anatomy;
- anti-repetition;
- exact dimensions;
- correct headline/copy;
- brand colors;
- typography;
- actual Lonko logo treatment;
- mobile/feed readability;
- accessibility/alt-text fit;
- no fabricated UI, claims, customer relationship, or unintended branding.

Claude returns a clear result for each asset:

- **APPROVED**
- **REVISE**
- **REJECT**

If revision is required, Claude gives a narrowly scoped correction. Alex takes only that correction back to Lonko Chronicles.

Claude does not casually reopen the article, approved concept, or passed image layers.

---

## 8. Claude Blog owns publish readiness; Cursor Web executes preview, deploy, and live verify

Once the article, social copy, and final visuals all pass QA, Claude Blog prepares the complete publication package and presents the final publish-readiness state to Alex.

No external publication occurs until Alex explicitly authorizes publication with language such as:

- **APPROVED FOR PUBLICATION**
- **Publish it**
- **Go live**

**Normal production teammates (workflow v2):**

1. **Claude Blog Post & Social Media** — editorial package  
2. **ChatGPT — Lonko Chronicles / Image Production** — hero/social assets  
3. **Cursor Web** — hosted pre-publish preview, automated validation, deploy, live production verification  

There is **no** routine fourth “Publishing Operator” role. ChatGPT outside Image Production is exception/escalation only.

After Alex's explicit publication approval (and after Claude + Alex have reviewed the **hosted preview** URL):

1. Claude Blog freezes the approved article/social package and returns one **PUBLISH HANDOFF** to **Cursor Web** (not a separate operator).
2. The handoff includes title, slug, frozen status, approval date, package/Drive references, exact hero/social filenames, and **DEPLOY — DO NOT EDIT CONTENT**.
3. Cursor Web builds/validates, ensures the hosted preview remains green, merges/deploys to production, and verifies the live URL.
4. Cursor Web deploys the exact approved candidate. The only non-editorial changes allowed at deploy time are publication status and the real publication dates.
5. Automated production verification runs against the live URL (`scripts/verify_chronicles_production.py`, workflow `.github/workflows/chronicles-production-verify.yml`). It writes a machine-readable result Claude can read without using its own web fetch:
   - https://raw.githubusercontent.com/Lonko-Digital/lonko-digital-site/chronicles-verify/articles/{slug}.json
   - https://raw.githubusercontent.com/Lonko-Digital/lonko-digital-site/chronicles-verify/latest.json
6. Claude reads that result. `overall: PASS` means **PRODUCTION VERIFIED**. `overall: FAIL` is a real production signal for Cursor Web.
7. Claude may also try a direct live check. If that fetch returns 404, 403, a cache error, a proxy error, or any result that disagrees with a PASS verification record, Claude classifies its own fetch as **TOOL / PROXY INCONCLUSIVE**. It must not call the article down, reopen editorial QA, or ask for a site change whose only purpose is to make Claude's fetch succeed.
8. Claude then returns LinkedIn/Meta copy + UTM URLs for Alex to post.

Alex should not manage GitHub, publishing routes, GA4, or schema during a normal article.
7. **Cursor Web publishing route (workflow v2):**
   - Prefer the established Drive → GitHub Actions bridge when the Inbox is reachable; otherwise Cursor Web translates the frozen handoff onto a dedicated GitHub publication branch with exact approved asset bytes, regenerates derived surfaces, and opens a PR against `main`.
   - Both paths end at the same safety boundary: **a PR, never a direct push to `main`.**
   - The PR must produce a **hosted pre-publish preview** (see `.github/workflows/chronicles-pr-preview.yml`) before merge.
   - The PR must preserve frozen content and identify any unavoidable technical mapping without silently changing editorial decisions.
8. **Alex merge remains authoritative.** Cursor Web may prepare and validate the PR after publication approval, but it does not merge to `main` until Alex explicitly authorizes the merge (chat authorization is enough).
9. Alex should not manually assemble files, download/re-upload assets, reconstruct metadata, choose routes, or locate the bridge Inbox.
10. If Claude Blog later gains a verified writable publishing/deploy connector, direct routine publication may move there without changing the editorial or merge-authorization gates.

**Cursor Web is the normal per-article technical teammate** for preview, validation, deploy, and live verify.

Cursor Web is also the exception path for infrastructure needs such as:

- publishing bridge failure;
- template defect;
- shared article presentation defects (hero width/spacing, Share row, public metadata hygiene — see `docs/chronicles/lonko-chronicles-article-presentation.md`);
- schema/metadata system defect;
- tracking infrastructure change;
- new article capability;
- site rendering/performance/accessibility defect.

Alex should not need to open Cursor for ordinary *editorial* work — only for technical publishing steps that Cursor owns.

---

## 9. Claude Blog must return the live URL and tracked social URLs

After automated production verification records `overall: PASS` for the live URL, Claude Blog gives Alex a final social-distribution package containing:

- final live canonical article URL;
- quick live-page presentation check against `docs/chronicles/lonko-chronicles-article-presentation.md` (hero width/spacing, Share row, no leaked word-count notes) — escalate to Cursor Web only if the shared template is wrong;
- final LinkedIn post copy;
- final Meta post copy;
- approved social banner reference;
- **LinkedIn UTM URL**;
- **Meta UTM URL**;
- any additional platform-specific URL required by the approved distribution plan.

Default UTM structure:

```
?utm_source={platform}&utm_medium=organic_social&utm_campaign={article_slug}&utm_content={post_variant}
```

Default launch values:

- `utm_medium=organic_social`
- `utm_campaign=<article-slug>`
- `utm_content=launch_post`

Source values must reflect the actual platform.

Examples:

- LinkedIn: `utm_source=linkedin`
- Meta cross-platform post when one shared link is intentionally used: `utm_source=meta`
- Facebook-only distribution: `utm_source=facebook`
- Instagram-only clickable destination: `utm_source=instagram`

For later reposts/creative variants, keep the campaign stable and change `utm_content`, for example:

- `followup_post`
- `stat_angle`
- `owner_angle`

Claude Blog must not ask Alex to manually construct these URLs.

---

## 10. Alex owns social posting

After Claude Blog confirms the article is live and supplies the finished social package:

- **Alex posts to LinkedIn**
- **Alex posts to Meta**

Alex uses:

- Claude’s approved platform-specific copy;
- the approved 1200×628 social banner;
- the corresponding Claude-provided UTM URL.

Cursor Web deploys the website article from Claude Blog’s approved package after hosted-preview QA; Claude Blog verifies the live article and supplies the final social package; Alex publishes the social posts.

---

## 11. The whole recurring flow

The normal flow is:

**Claude first checks for an active unpublished Chronicles article (`chronicles/state.json`). If one exists, Alex → Claude Blog resumes that article at its current gate. If none exists (or Alex explicitly authorizes parallel/new production), then Alex → Claude Blog topic discovery → Alex approves topic/angle → Claude Blog researches/writes + develops creative direction → Claude gives one complete prompt to Lonko Chronicles → Lonko Chronicles creates hero + social banner → Alex revises/approves images → Lonko Chronicles saves approved assets and returns canonical names/references → Claude retrieves and QA-checks the assets → Cursor Web hosts a real pre-publish preview → Claude + Alex QA the preview → Alex gives final publication approval → Claude immediately returns the complete Publish Handoff to Cursor Web → Cursor deploys the exact approved candidate → automated production verification runs → Claude reads the machine-readable result → if Claude's own fetch disagrees with a PASS record, it labels that fetch TOOL / PROXY INCONCLUSIVE and does not reopen the article → Claude returns LinkedIn/Meta copy + UTM links → Alex posts LinkedIn + Meta.**

This is the default. Do not add extra handoffs unless a genuine technical or editorial problem requires them.

---

## 12. Operator experience standard

Alex should need to remember only the starting action:

> “I want to launch a blog post.”

The system should know the rest.

Do not make Alex repeatedly answer:

- Who goes next?
- What size are the banners?
- Where is the logo?
- Who writes the image prompt?
- Who checks the images?
- Who publishes the article?
- What UTM should I use?
- Do I need Cursor?
- Do I need to download/upload the assets?

Those are workflow responsibilities, not Alex’s recurring project-management tasks.

---

## 13. Quality principle

This workflow simplifies coordination, not quality.

**Basic means narrow, not half-built.  
We do not defer quality. We defer scope.  
Build depth underneath. Present clarity on top.**

The goal is fewer preventable handoffs and fewer revision loops while preserving the highest editorial, visual, SEO, tracking, and brand standards.
