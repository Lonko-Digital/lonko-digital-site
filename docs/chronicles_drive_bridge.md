# Chronicles Drive publishing bridge

Transport-only intake for Lonko Chronicles. The frozen v4 article contract in
`scripts/chronicles_lib` remains authoritative.

## Package layout

```
inbox/<slug>/
  manifest.json       # package_id, slug, content_sha256, created_at, producer
  article.yaml        # full v4 metadata
  body.md             # long-form Markdown body
  assets/             # raster only: png/jpg/jpeg/webp/avif
  CHECKSUMS.sha256    # required
```

`content_sha256` = SHA-256 over sorted lines `{file_sha256}  {relpath}\n` for all
package files except `manifest.json` and `CHECKSUMS.sha256`. Text files use LF;
`article.yaml` is normalized via parse + `yaml.safe_dump(sort_keys=True)`.

## Drive permission model (least privilege)

Create a Google Cloud service account. Share **only** these Drive folders with it:

| Folder | Access | Secret |
|---|---|---|
| Inbox | Reader (or Content manager if moves required) | `DRIVE_INBOX_FOLDER_ID` |
| Processed (90-day retention) | Content manager | `DRIVE_PROCESSED_FOLDER_ID` (optional v1) |
| Quarantine (30-day retention) | Content manager | `DRIVE_QUARANTINE_FOLDER_ID` (optional v1) |

Repo secrets:

- `DRIVE_SERVICE_ACCOUNT_JSON` — full service-account JSON
- `DRIVE_INBOX_FOLDER_ID`

No site deploy keys in Drive. GitHub Actions uses `GITHUB_TOKEN` to open PRs only.

## Workflow

`.github/workflows/chronicles-drive-ingest.yml`

- Triggers: `schedule` (every 6 hours) + `workflow_dispatch`
- Flow: optional Drive sync → validate/checksums/v4 → stage `chronicles/content/<slug>/` → build → **open PR**
- **Never pushes to `main`.** Alex merge = publication authorization.

## Local commands

```bash
python scripts/run_chronicles_ingest.py --inbox bridge/inbox
python scripts/test_chronicles_bridge_acceptance.py
```

## Soft-retire (v1)

`status: retired` keeps the canonical HTML URL, emits `noindex,nofollow`, shows a
temporary retired notice, and removes the article from Latest/Featured/sections,
sitemap, feed, and search. Final notice copy routes through Claude Web later.

## Cost

Public repo standard GitHub-hosted runners: $0. Low-frequency schedule is
negligible. Drive API: ordinary Workspace/Drive usage only.
