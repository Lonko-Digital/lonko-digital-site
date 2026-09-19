# Chronicles Drive publishing bridge

Transport-only intake for Lonko Chronicles. The frozen v4 article contract in
`scripts/chronicles_lib` remains authoritative.

## Drive folder location (important)

Google **service accounts have no My Drive storage quota**. They can **read** and
**move** packages in a folder shared as Editor, but they **cannot upload** into a
normal My Drive folder.

**Preferred:** put `Lonko Chronicles/` on a **Google Shared Drive** and add the
service account as **Content manager**. Then CI can upload smoke packages too.

**Also valid for production:** Claude Blog (human) uploads packages into Inbox;
the service account only downloads, validates, and moves to Processed/Quarantine.
That matches the editorial workflow and works with My Drive shares.

## Preferred Drive folder structure

Create these folders in Google Drive (Shared Drive preferred, or My Drive):

```
Lonko Chronicles/
  Inbox/          ← Claude Blog drops one package folder here
  Processed/      ← successful / replay packages (90-day retention)
  Quarantine/     ← failed packages (30-day retention)
```

Share **only** these three folders (not the whole Drive) with the bridge
service account:

| Folder | Permission for service account |
|---|---|
| Inbox | **Editor** (needs to move packages out after ingest) |
| Processed | **Editor** |
| Quarantine | **Editor** |

Do **not** share personal Drive roots or unrelated Lonko folders.

## Package layout (inside Inbox)

```
Inbox/<slug>/
  manifest.json
  article.yaml
  body.md
  assets/             # raster only: png/jpg/jpeg/webp/avif
  CHECKSUMS.sha256    # required
```

## GitHub secrets (exact names)

Repo → Settings → Secrets and variables → Actions → New repository secret:

| Secret name | Value |
|---|---|
| `DRIVE_SERVICE_ACCOUNT_JSON` | Full JSON contents of the downloaded service-account key file |
| `DRIVE_INBOX_FOLDER_ID` | Folder ID of `Lonko Chronicles/Inbox` (from the Drive URL) |
| `DRIVE_PROCESSED_FOLDER_ID` | Folder ID of `Lonko Chronicles/Processed` |
| `DRIVE_QUARANTINE_FOLDER_ID` | Folder ID of `Lonko Chronicles/Quarantine` |

Folder ID = the long ID in the browser URL when that folder is open:
`https://drive.google.com/drive/folders/<THIS_PART>`

All four secrets are required for the real cloud smoke test and ongoing ops.

## Service account (create once)

1. Open Google Cloud Console → create/select a small project (e.g. `lonko-chronicles-bridge`).
2. Enable **Google Drive API**.
3. IAM → Service Accounts → Create (`lonko-chronicles-bridge`).
4. Keys → Add key → JSON → download once; store only in the GitHub secret.
5. Copy the service account email (`…@….iam.gserviceaccount.com`) and share the three folders with it as Editor.

## Security note (v1)

Uses a long-lived Google service-account JSON key stored only as a GitHub Actions
secret. Acceptable for small v1 because: folder ACL is narrow, key never enters
git, and revoke/rotate is “delete key in GCP + replace secret.” Future upgrade:
GitHub OIDC + Google Workload Identity Federation (no long-lived key). Not in
scope for v1 unless a material reason appears.

## Workflow

`.github/workflows/chronicles-drive-ingest.yml`

- Triggers: `schedule` (every 6 hours) + `workflow_dispatch`
- Flow: Drive sync → validate/checksums/v4 → stage → build → Drive archive → **open PR**
- **Never pushes to `main`.** Alex merge = publication authorization.

## Python dependencies

Authoritative install path: `requirements-chronicles-bridge.txt`

Includes `pyyaml`, `markdown`, `google-auth`, and `google-api-python-client`
(required by `scripts/chronicles_bridge/drive.py`). Both Drive workflows install
from this file; do not gate Google packages on secret interpolation in shell.

```bash
pip install -r requirements-chronicles-bridge.txt
python scripts/test_chronicles_bridge_deps.py
```

## Local / smoke helpers

```bash
pip install -r requirements-chronicles-bridge.txt
python scripts/build_bridge_smoke_package.py
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
