#!/usr/bin/env python3
"""Refresh data/software_meta.json: version and last update of each software card.

For every entry in data/software.y(a)ml that links a GitHub repository
(`repo:` or `github:`), the script records

* the version: `Version:` in DESCRIPTION (R packages; an entry may name another
  file with `version_file:`, e.g. a package inside a monorepo), otherwise
  `version` in package.json or manifest.json, otherwise the latest release tag;
* the last update: the committer date of the newest commit on the default
  branch.

Private or unreachable repositories are skipped. Entries that cannot be
refreshed keep their previous values, and the file is left untouched when no
repository can be read at all, so a failed refresh never blanks the cards.

Usage: GITHUB_TOKEN=... python3 scripts/update_software_meta.py
(the token is optional but avoids the low anonymous API rate limit).
Only the Python standard library is needed.
"""
from __future__ import annotations

import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "software_meta.json"
API = "https://api.github.com"

NAME_RE = re.compile(r"""^-\s+name:\s*["']?([^"'#]+?)["']?\s*(?:#.*)?$""")
VFILE_RE = re.compile(r"""^\s+version_file:\s*["']?([^"'#\s]+)["']?\s*(?:#.*)?$""")
REPO_RE = re.compile(
    r"""^\s+(?:repo|github):\s*["']?https://github\.com/([^/\s"']+/[^/\s"'#]+?)(?:\.git)?/?["']?\s*(?:#.*)?$"""
)


def catalogue(with_files: bool = False):
    """Map card name -> owner/repo for every entry that links GitHub.

    With `with_files=True`, also return card name -> `version_file:` value.
    """
    src = next((p for p in (DATA / "software.yml", DATA / "software.yaml") if p.exists()), None)
    if src is None:
        sys.exit("data/software.yml or data/software.yaml not found")
    repos: dict[str, str] = {}
    files: dict[str, str] = {}
    name = None
    for line in src.read_text(encoding="utf-8").splitlines():
        m = NAME_RE.match(line)
        if m:
            name = m.group(1).strip()
            continue
        m = REPO_RE.match(line)
        if m and name:
            repos[name] = m.group(1)
            continue
        m = VFILE_RE.match(line)
        if m and name:
            files[name] = m.group(1)
    return (repos, files) if with_files else repos


def get(path: str):
    req = urllib.request.Request(
        API + path,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "software-meta-refresh",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def file_text(full: str, ref: str, path: str) -> str | None:
    j = get(f"/repos/{full}/contents/{path}?ref={ref}")
    if not isinstance(j, dict) or j.get("encoding") != "base64":
        return None
    return base64.b64decode(j["content"]).decode("utf-8", "replace")


def version(full: str, ref: str, desc_path: str = "DESCRIPTION") -> str | None:
    desc = file_text(full, ref, desc_path)
    if desc:
        m = re.search(r"^Version:\s*(\S+)", desc, re.M)
        if m:
            return m.group(1)
    for name in ("package.json", "manifest.json"):
        text = file_text(full, ref, name)
        if text:
            try:
                v = json.loads(text).get("version")
            except (ValueError, AttributeError):
                v = None
            if v:
                return str(v)
    rel = get(f"/repos/{full}/releases/latest")
    if isinstance(rel, dict) and rel.get("tag_name"):
        return rel["tag_name"].lstrip("v")
    return None


def main() -> int:
    old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    new: dict[str, dict] = {}
    failed = 0
    repos, files = catalogue(with_files=True)
    for name, full in sorted(repos.items(), key=lambda kv: kv[0].lower()):
        try:
            repo = get(f"/repos/{full}")
            if not repo or repo.get("private"):
                continue
            ref = repo["default_branch"]
            entry = {}
            v = version(repo["full_name"], ref, files.get(name, "DESCRIPTION"))
            if v:
                entry["version"] = v
            head = get(f"/repos/{repo['full_name']}/commits/{ref}")
            if head:
                entry["updated"] = head["commit"]["committer"]["date"][:10]
            if entry:
                new[name] = entry
        except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as e:
            failed += 1
            print(f"warning: {name} ({full}): {e}", file=sys.stderr)
            if name in old:
                new[name] = old[name]
    if not new:
        print("no repository could be read; keeping the existing file", file=sys.stderr)
        return 0
    OUT.write_text(json.dumps(new, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(new)} entries, {failed} failures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
