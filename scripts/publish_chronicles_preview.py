#!/usr/bin/env python3
"""Assemble and push a hosted certification preview to branch preview-site.

Usage (from repo root):
  python scripts/publish_chronicles_preview.py --label cert-v2 --slug google-ads-ai-max-migration-what-changed

Prints a rawcdn.githack.com browser URL (text/html + relative CSS/JS).
Requires git push access. Production Pages stays on main (lonkodigital.com).
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, capture_output=True, **kwargs)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="cert-v2", help="preview path label under pr/")
    ap.add_argument("--slug", default="", help="article slug to highlight")
    args = ap.parse_args()

    # Ensure build is current
    subprocess.check_call([sys.executable, str(ROOT / "scripts" / "build_chronicles.py")])

    slug = args.slug
    if not slug:
        sys.path.insert(0, str(ROOT / "scripts"))
        from chronicles_lib.model import load_all_articles, public_articles

        arts = public_articles(load_all_articles(ROOT / "chronicles" / "content"))
        if not arts:
            print("No published articles to preview", file=sys.stderr)
            return 1
        slug = arts[0].slug

    dist = ROOT / "preview-dist"
    dest = dist / "pr" / args.label
    if dist.exists():
        shutil.rmtree(dist)
    dest.mkdir(parents=True)
    shutil.copytree(ROOT / "assets", dest / "assets")
    shutil.copytree(ROOT / "chronicles", dest / "chronicles")
    if (ROOT / "index.html").is_file():
        shutil.copy2(ROOT / "index.html", dest / "index.html")

    # Commit to preview-site via worktree (orphan if branch does not exist yet)
    work = ROOT / ".preview-worktree"
    if work.exists():
        shutil.rmtree(work)
    # Fetch may fail when preview-site has never been pushed; that is OK.
    subprocess.run(
        ["git", "fetch", "origin", "preview-site"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    ls = subprocess.run(
        ["git", "ls-remote", "--heads", "origin", "preview-site"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    subprocess.run(["git", "worktree", "remove", "-f", str(work)], cwd=ROOT, capture_output=True)
    if ls.stdout.strip():
        run(["git", "worktree", "add", "-B", "preview-site", str(work), "origin/preview-site"], cwd=ROOT)
    else:
        print("Creating orphan preview-site branch via worktree...", file=sys.stderr)
        run(["git", "worktree", "add", "--orphan", "-B", "preview-site", str(work)], cwd=ROOT)
        # clear orphan tracked files
        for p in work.iterdir():
            if p.name == ".git":
                continue
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()

    target = work / "pr" / args.label
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(dest, target)

    run(["git", "add", "-A"], cwd=work)
    status = subprocess.run(["git", "status", "--porcelain"], cwd=work, capture_output=True, text=True)
    if status.stdout.strip():
        run(["git", "config", "user.name", "lonko-chronicles-preview"], cwd=work)
        run(
            ["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"],
            cwd=work,
        )
        run(["git", "commit", "-m", f"Preview {args.label} ({slug})"], cwd=work)
        run(["git", "push", "-u", "origin", "preview-site"], cwd=work)
    sha = run(["git", "rev-parse", "HEAD"], cwd=work).stdout.strip()
    run(["git", "worktree", "remove", "-f", str(work)], cwd=ROOT)

    # rawcdn.githack serves text/html (jsDelivr returns text/plain for .html).
    # Do not point GitHub Pages at preview-site — production Pages is main + CNAME.
    url = (
        f"https://rawcdn.githack.com/Lonko-Digital/lonko-digital-site/{sha}/"
        f"pr/{args.label}/chronicles/{slug}/index.html"
    )
    print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
