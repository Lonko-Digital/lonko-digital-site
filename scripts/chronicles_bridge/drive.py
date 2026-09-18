"""Optional Google Drive sync for Chronicles inbox (least privilege).

Requires secrets:
  DRIVE_SERVICE_ACCOUNT_JSON  — service account key JSON
  DRIVE_INBOX_FOLDER_ID       — shared Drive folder for incoming packages
  DRIVE_PROCESSED_FOLDER_ID   — optional archive folder
  DRIVE_QUARANTINE_FOLDER_ID  — optional quarantine folder

If secrets are absent, callers should use the local bridge/inbox filesystem path.
"""

from __future__ import annotations

import io
import json
import os
from pathlib import Path


def drive_configured() -> bool:
    return bool(
        os.environ.get("DRIVE_SERVICE_ACCOUNT_JSON", "").strip()
        and os.environ.get("DRIVE_INBOX_FOLDER_ID", "").strip()
    )


def _service():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    raw = os.environ["DRIVE_SERVICE_ACCOUNT_JSON"]
    info = json.loads(raw) if raw.strip().startswith("{") else json.loads(Path(raw).read_text(encoding="utf-8"))
    creds = service_account.Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/drive"],
    )
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def list_inbox_folders(service=None) -> list[dict]:
    """List immediate child folders in the inbox (each = one article package)."""
    service = service or _service()
    folder_id = os.environ["DRIVE_INBOX_FOLDER_ID"]
    q = (
        f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' "
        "and trashed = false"
    )
    resp = (
        service.files()
        .list(q=q, fields="files(id,name)", pageSize=100, supportsAllDrives=True, includeItemsFromAllDrives=True)
        .execute()
    )
    return resp.get("files", [])


def download_folder(service, folder_id: str, dest: Path) -> Path:
    """Download a Drive folder tree into dest/<name>/."""
    dest.mkdir(parents=True, exist_ok=True)
    meta = service.files().get(fileId=folder_id, fields="id,name", supportsAllDrives=True).execute()
    package_dir = dest / meta["name"]
    if package_dir.exists():
        import shutil

        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True)

    q = f"'{folder_id}' in parents and trashed = false"
    resp = (
        service.files()
        .list(
            q=q,
            fields="files(id,name,mimeType)",
            pageSize=200,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        )
        .execute()
    )
    for f in resp.get("files", []):
        if f["mimeType"] == "application/vnd.google-apps.folder":
            download_folder(service, f["id"], package_dir)
            # nested folder lands as package_dir/<name>; move up if nested assets/
            nested = package_dir / f["name"]
            if nested.is_dir() and f["name"] == "assets":
                pass  # already correct
            continue
        _download_file(service, f["id"], package_dir / f["name"])
    return package_dir


def _download_file(service, file_id: str, dest: Path) -> None:
    from googleapiclient.http import MediaIoBaseDownload

    request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(buf.getvalue())


def move_file(service, file_id: str, new_parent_id: str, old_parent_id: str) -> None:
    service.files().update(
        fileId=file_id,
        addParents=new_parent_id,
        removeParents=old_parent_id,
        fields="id,parents",
        supportsAllDrives=True,
    ).execute()


def sync_inbox_to_local(local_inbox: Path) -> list[Path]:
    """Download each Drive inbox package folder into local_inbox. Returns paths."""
    if not drive_configured():
        return []
    service = _service()
    local_inbox.mkdir(parents=True, exist_ok=True)
    downloaded: list[Path] = []
    for folder in list_inbox_folders(service):
        path = download_folder(service, folder["id"], local_inbox)
        downloaded.append(path)
    return downloaded
