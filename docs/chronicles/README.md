# Lonko Chronicles — editorial governance (repo docs)

Production workflow v2 (normal path): **Claude Blog → ChatGPT Images → Cursor Web → Alex**.
There is **no routine Publishing Operator**.

Claude Blog owns editorial/creative governance and maintains Creative Registry
content. ChatGPT Images (Lonko Chronicles image production) renders hero/social
assets. Cursor Web owns hosted preview, engineering, deploy, and live verify.
Alex approves final creative and publication.

These Markdown files are **reference artifacts only**. They are:
- not loaded by the static site build
- not runtime content
- not a CMS / database / second content model

## Governance freshness

**GitHub is canonical.** Google Drive holds readable mirrors only. When a
mirrored copy is synced, it should cite the repo path plus commit SHA and/or
sync date. Do not build a new Drive sync system — this is a documentation rule
only.

## Canonical paths (authoritative)

| Document | Canonical path |
|---|---|
| Operating system | [`lonko-chronicles-operating-system.md`](./lonko-chronicles-operating-system.md) |
| Production workflow | [`lonko-chronicles-production-workflow.md`](./lonko-chronicles-production-workflow.md) |
| Article contract | [`chronicles-article-contract.yaml`](./chronicles-article-contract.yaml) |
| Active article state | [`../../chronicles/state.json`](../../chronicles/state.json) |
| Creative registry | [`lonko-chronicles-creative-registry.md`](./lonko-chronicles-creative-registry.md) |
| Creative learnings | [`lonko-chronicles-creative-learnings.md`](./lonko-chronicles-creative-learnings.md) |
| GA4 / dataLayer foundation | [`lonko-chronicles-ga4-foundation.md`](./lonko-chronicles-ga4-foundation.md) |
| Article presentation (live page) | [`lonko-chronicles-article-presentation.md`](./lonko-chronicles-article-presentation.md) |
| Brand production tokens | [`../brand/lonko-brand-production-tokens.md`](../brand/lonko-brand-production-tokens.md) |

Full repo-relative paths:

- `docs/chronicles/lonko-chronicles-operating-system.md`
- `docs/chronicles/lonko-chronicles-production-workflow.md`
- `docs/chronicles/chronicles-article-contract.yaml`
- `chronicles/state.json`
- `docs/chronicles/lonko-chronicles-creative-registry.md`
- `docs/chronicles/lonko-chronicles-creative-learnings.md`
- `docs/chronicles/lonko-chronicles-ga4-foundation.md`
- `docs/chronicles/lonko-chronicles-article-presentation.md`
- `docs/brand/lonko-brand-production-tokens.md`

**Do not use** `claude/lonko-chronicles-operating-system.md` or
`claude/lonko-chronicles-creative-registry.md` as operational paths in this
repository. Repository copies are authoritative after the 2026-09-19 sync.

## Ownership

| Role | Owns |
|---|---|
| Claude Blog Post & Social Media | Editorial package, SEO/social, creative direction, visual QA criteria, publish-ready freeze |
| ChatGPT Images (Lonko Chronicles image production) | Hero + social banner render/revision; returns approved asset references |
| Cursor Web | Hosted preview, engineering/implementation, deploy, production verify |
| Alex | Final creative approval and publication authorization |

There is **no routine Publishing Operator**. ChatGPT outside Image Production is
exception/escalation only.

## Asset format note (engineering)

Local/test fixtures may use SVG heroes for convenience. **Drive publishing
packages reject SVG** — production packages must ship raster assets
(`png` / `jpg` / `jpeg` / `webp` / `avif`). See
[`../chronicles_drive_bridge.md`](../chronicles_drive_bridge.md).
