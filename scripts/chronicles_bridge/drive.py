"""Optional Google Drive sync for Chronicles inbox (least privilege).

Required secrets:
  DRIVE_SERVICE_ACCOUNT_JSON  — service account key JSON (string)
  DRIVE_INBOX_FOLDER_ID       — Lonko Chronicles / Inbox folder ID

Recommended for cloud archive (v1 smoke + ops):
  DRIVE_PROCESSED_FOLDER_ID   — Lonko Chronicles / Processed
  DRIVE_QUARANTINE_FOLDER_ID  — Lonko Chronicles / Quarantine

If secrets are absent, callers use the local bridge/inbox filesystem path.
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


def processed_folder_id() -> str:
    return os.environ.get("DRIVE_PROCESSED_FOLDER_ID", "").strip()


def quarantine_folder_id() -> str:
    return os.environ.get("DRIVE_QUARANTINE_FOLDER_ID", "").strip()


def _service():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    raw = os.environ["DRIVE_SERVICE_ACCOUNT_JSON"]
    info = json.loads(raw) if raw.strip().startswith("{") else json.loads(Path(raw).read_text(encoding="utf-8"))
    # Folder ACLs are the real boundary; scope must allow read + parent moves.
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
        .list(
            q=q,
            fields="files(id,name)",
            pageSize=100,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        )
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


def move_folder(service, folder_id: str, new_parent_id: str, old_parent_id: str) -> None:
    """Move a package folder from Inbox to Processed or Quarantine."""
    service.files().update(
        fileId=folder_id,
        addParents=new_parent_id,
        removeParents=old_parent_id,
        fields="id,parents",
        supportsAllDrives=True,
    ).execute()


def sync_inbox_to_local(local_inbox: Path) -> list[dict]:
    """Download each Drive inbox package folder.

    Returns list of {id, name, path} so callers can archive by Drive file id.
    """
    if not drive_configured():
        return []
    service = _service()
    local_inbox.mkdir(parents=True, exist_ok=True)
    downloaded: list[dict] = []
    for folder in list_inbox_folders(service):
        path = download_folder(service, folder["id"], local_inbox)
        downloaded.append({"id": folder["id"], "name": folder["name"], "path": str(path)})
    # Persist map for the ingest step (same job)
    map_path = local_inbox / ".drive_folder_map.json"
    map_path.write_text(json.dumps(downloaded, indent=2) + "\n", encoding="utf-8")
    return downloaded


def archive_drive_results(
    results: list[dict],
    *,
    inbox_map_path: Path,
) -> list[dict]:
    """Move Drive package folders to Processed or Quarantine based on ingest outcome.

    results: list of ingest result dicts with slug + outcome.
    """
    if not drive_configured():
        return []
    if not inbox_map_path.is_file():
        return []
    mapping = {row["name"]: row for row in json.loads(inbox_map_path.read_text(encoding="utf-8"))}
    proc = processed_folder_id()
    quar = quarantine_folder_id()
    inbox = os.environ["DRIVE_INBOX_FOLDER_ID"]
    if not proc and not quar:
        return [{"note": "Drive archive folder IDs not set; left packages in Inbox"}]

    service = _service()
    actions: list[dict] = []
    for result in results:
        slug = result.get("slug") or ""
        outcome = result.get("outcome") or ""
        row = mapping.get(slug)
        if not row:
            continue
        target = None
        if outcome in {"staged", "noop_replay"} and proc:
            target = proc
        elif outcome == "quarantine" and quar:
            target = quar
        if not target:
            actions.append({"slug": slug, "action": "skipped", "reason": "no target folder id"})
            continue
        try:
            move_folder(service, row["id"], target, inbox)
            actions.append(
                {
                    "slug": slug,
                    "action": "moved",
                    "to": "processed" if target == proc else "quarantine",
                    "drive_id": row["id"],
                }
            )
        except Exception as exc:  # noqa: BLE001
            actions.append({"slug": slug, "action": "error", "error": str(exc)})
    return actions


def _mime_for(path: Path) -> str:
    suffix = path.suffix.lower()
    return {
        ".json": "application/json",
        ".yaml": "text/yaml",
        ".yml": "text/yaml",
        ".md": "text/markdown",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".avif": "image/avif",
        ".txt": "text/plain",
    }.get(suffix, "application/octet-stream")


def _create_drive_folder(service, name: str, parent_id: str) -> str:
    meta = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    created = (
        service.files()
        .create(body=meta, fields="id,name", supportsAllDrives=True)
        .execute()
    )
    return created["id"]


def _upload_file(service, local_path: Path, parent_id: str) -> str:
    from googleapiclient.http import MediaFileUpload

    media = MediaFileUpload(str(local_path), mimetype=_mime_for(local_path), resumable=True)
    meta = {"name": local_path.name, "parents": [parent_id]}
    created = (
        service.files()
        .create(body=meta, media_body=media, fields="id,name", supportsAllDrives=True)
        .execute()
    )
    return created["id"]


def upload_package_to_inbox(package_dir: Path) -> dict:
    """Upload a local package directory into Drive Inbox as a child folder.

    Replaces an existing Inbox child with the same name.
    """
    if not drive_configured():
        raise RuntimeError("Drive is not configured")
    package_dir = Path(package_dir)
    if not package_dir.is_dir():
        raise FileNotFoundError(package_dir)

    service = _service()
    inbox = os.environ["DRIVE_INBOX_FOLDER_ID"]
    slug = package_dir.name

    # Remove existing same-name folder in Inbox (idempotent smoke reruns)
    for existing in list_inbox_folders(service):
        if existing["name"] == slug:
            service.files().update(
                fileId=existing["id"],
                body={"trashed": True},
                supportsAllDrives=True,
            ).execute()

    root_id = _create_drive_folder(service, slug, inbox)

    def walk(local: Path, parent_id: str) -> None:
        for child in sorted(local.iterdir()):
            if child.name.startswith("."):
                continue
            if child.is_dir():
                nested_id = _create_drive_folder(service, child.name, parent_id)
                walk(child, nested_id)
            elif child.is_file():
                _upload_file(service, child, parent_id)

    walk(package_dir, root_id)
    return {"id": root_id, "name": slug, "parent": inbox}
