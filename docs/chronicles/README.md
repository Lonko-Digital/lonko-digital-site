# Lonko Chronicles — editorial governance (repo docs)

Claude Blog Post & Social Media owns editorial/creative governance and maintains
Creative Registry content. Alex approves final creative and publication.
Cursor Web owns web engineering/implementation/support and syncs approved
governance docs into this repository.

These Markdown files are **reference artifacts only**. They are:
- not loaded by the static site build
- not runtime content
- not a CMS / database / second content model

## Canonical paths (authoritative)

| Document | Canonical path |
|---|---|
| Operating system | [`lonko-chronicles-operating-system.md`](./lonko-chronicles-operating-system.md) |
| Creative registry | [`lonko-chronicles-creative-registry.md`](./lonko-chronicles-creative-registry.md) |
| Creative learnings | [`lonko-chronicles-creative-learnings.md`](./lonko-chronicles-creative-learnings.md) |
| Brand production tokens | [`../brand/lonko-brand-production-tokens.md`](../brand/lonko-brand-production-tokens.md) |

Full repo-relative paths:

- `docs/chronicles/lonko-chronicles-operating-system.md`
- `docs/chronicles/lonko-chronicles-creative-registry.md`
- `docs/chronicles/lonko-chronicles-creative-learnings.md`
- `docs/brand/lonko-brand-production-tokens.md`

**Do not use** `claude/lonko-chronicles-operating-system.md` or
`claude/lonko-chronicles-creative-registry.md` as operational paths in this
repository. Repository copies are authoritative after the 2026-09-19 sync.

## Ownership

| Role | Owns |
|---|---|
| Claude Blog Post & Social Media | Creative strategy, standards, registry content, visual QA criteria |
| Alex | Final creative approval and publication authorization |
| Cursor Web | Web engineering, implementation, and sync support |

## Asset format note (engineering)

Local/test fixtures may use SVG heroes for convenience. **Drive publishing
packages reject SVG** — production packages must ship raster assets
(`png` / `jpg` / `jpeg` / `webp` / `avif`). See
[`../chronicles_drive_bridge.md`](../chronicles_drive_bridge.md).
