"""Shallow-clone cttir/tutorials and emit a flat tutorial index JSON.

Output: data/_generated/cttir_tutorials.json — list of
  {slug, topic, title, description, url, tags}

Hard-fails on clone failure, missing frontmatter, or zero tutorials.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CTTIR_REPO = "https://github.com/cttir/tutorials"
TUTORIALS_BASE_URL = "https://cttir.github.io/tutorials/tutorials"
REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "data" / "_generated"
OUT_PATH = OUT_DIR / "cttir_tutorials.json"

# Topic slugs we will consider. Anything else fails the build.
KNOWN_TOPICS = {
    "regression-modelling", "bioinformatics", "machine-learning", "inference",
    "probability", "clinical-biostatistics", "visualisation", "bayesian",
    "statistical-foundations", "time-series", "survival-analysis", "sample-size",
    "multivariate", "experimental-design", "meta-analysis", "descriptive-statistics",
}

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    block = m.group(1)
    out: dict = {}
    current_key: str | None = None
    current_list: list | None = None
    for raw in block.splitlines():
        if not raw.strip():
            continue
        if raw.startswith("  - ") and current_list is not None:
            current_list.append(raw[4:].strip().strip('"'))
            continue
        m2 = re.match(r"([A-Za-z_-]+):\s*(.*)$", raw)
        if not m2:
            continue
        key, val = m2.group(1), m2.group(2).strip()
        if val == "":
            current_key = key
            current_list = []
            out[key] = current_list
        else:
            current_key = None
            current_list = None
            out[key] = val.strip('"').strip("'")
    return out


def _on_rm_error(func, path, _exc):
    # Windows: git pack files are read-only; force-clear and retry.
    try:
        os.chmod(path, 0o700)
        func(path)
    except Exception:
        pass


def _shallow_clone(target: Path) -> None:
    if target.exists():
        shutil.rmtree(target, onerror=_on_rm_error)
    cmd = ["git", "clone", "--depth", "1", "--filter=blob:none", "--no-checkout",
           CTTIR_REPO, str(target)]
    subprocess.run(cmd, check=True)
    subprocess.run(["git", "-C", str(target), "sparse-checkout", "init", "--cone"], check=True)
    subprocess.run(["git", "-C", str(target), "sparse-checkout", "set", "tutorials"], check=True)
    subprocess.run(["git", "-C", str(target), "checkout"], check=True)


def main() -> int:
    workdir = Path(os.environ.get("CTTIR_CLONE_DIR") or tempfile.mkdtemp(prefix="cttir-"))
    print(f"[fetch_cttir] cloning into {workdir}", file=sys.stderr)
    try:
        _shallow_clone(workdir)
    except subprocess.CalledProcessError as e:
        print(f"[fetch_cttir] FATAL: clone failed: {e}", file=sys.stderr)
        return 2

    tutorials_dir = workdir / "tutorials"
    if not tutorials_dir.is_dir():
        print(f"[fetch_cttir] FATAL: {tutorials_dir} missing after clone", file=sys.stderr)
        return 2

    out: list[dict] = []
    bad: list[str] = []
    for qmd in sorted(tutorials_dir.rglob("*.qmd")):
        rel = qmd.relative_to(tutorials_dir)
        parts = rel.parts
        if len(parts) != 2:
            continue
        topic, fname = parts
        if topic not in KNOWN_TOPICS:
            bad.append(f"unknown topic dir: {topic}")
            continue
        slug = fname[:-4]
        if slug == "index":
            continue
        try:
            text = qmd.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = qmd.read_text(encoding="utf-8", errors="replace")
        fm = _parse_frontmatter(text)
        title = fm.get("title")
        if not title:
            bad.append(f"missing title: {rel}")
            continue
        description = fm.get("description") or ""
        cats = fm.get("categories") or []
        if not isinstance(cats, list):
            cats = []
        tags = [c for c in cats[1:]] if cats else []
        out.append({
            "slug": f"{topic}/{slug}",
            "topic": topic,
            "title": title,
            "description": description,
            "url": f"{TUTORIALS_BASE_URL}/{topic}/{slug}.html",
            "tags": tags,
        })

    if bad:
        print("[fetch_cttir] frontmatter problems:", file=sys.stderr)
        for b in bad[:20]:
            print(f"  - {b}", file=sys.stderr)
        if len(bad) > 20:
            print(f"  (+ {len(bad)-20} more)", file=sys.stderr)
    if not out:
        print("[fetch_cttir] FATAL: zero tutorials extracted", file=sys.stderr)
        return 2

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[fetch_cttir] wrote {len(out)} tutorials to {OUT_PATH.relative_to(REPO_ROOT)}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
