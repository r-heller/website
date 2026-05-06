"""Assemble the unified overview graph.

Reads:
  - content/publications.md             (52 publications, hand-written HTML)
  - data/publication_annotations.yml    (DOI → topics + methods)
  - data/software.yml                   (10 R packages, fully annotated)
  - data/_generated/cttir_tutorials.json (output of fetch_cttir_index.py)
  - data/research_topics.yml, tutorial_topics.yml, methods.yml

Writes:
  - static/overview/graph.json          (nodes + edges + index for the page)

Edge model (per OVERVIEW_PLAN.md Phase 1):
  - shared-tags : same-type or cross-type, ≥2 shared tags or ≥1 shared method
                  (effectively method-share for cross-domain).
  - used-in     : reserved (no detection until CTTIR exposes references_doi/software).
  - topic-related: same research_topic (within pubs+sw) or same tutorial_topic
                   (within courses), thinner background structure.

Cross-domain (publication ↔ course, software ↔ course) edges only form via
methods → tutorial_topics. Capped at 3 strongest course matches per publication.

CI gates (exit non-zero on failure) — see OVERVIEW_PLAN.md.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path

# ---------- minimal YAML loader (avoid PyYAML dependency) ----------------

def load_yaml(path: Path):
    """Load the small, well-shaped YAML files we author here.

    Supports: top-level list of mappings; scalar values; inline-list values
    written as [a, b, c]; block-list values written with `- item` lines.
    Comments (# ...) and blank lines are ignored.
    """
    text = path.read_text(encoding="utf-8")
    lines = []
    for raw in text.splitlines():
        s = raw.split("#", 1)[0].rstrip() if not raw.lstrip().startswith("#") else ""
        if s.strip():
            lines.append(s)
    items: list[dict] = []
    cur: dict | None = None
    pending_list_key: str | None = None
    for ln in lines:
        if ln.startswith("- "):
            if cur is not None:
                items.append(cur)
            cur = {}
            pending_list_key = None
            ln = ln[2:]
            if not ln.strip():
                continue
        if cur is None:
            cur = {}
            pending_list_key = None
        m = re.match(r"^(\s*)([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", ln)
        if not m:
            # continuation of a block list?
            if pending_list_key is not None:
                stripped = ln.strip()
                if stripped.startswith("- "):
                    cur[pending_list_key].append(_scalar(stripped[2:].strip()))
                    continue
            continue
        _, key, val = m.groups()
        if val == "":
            cur[key] = []
            pending_list_key = key
        elif val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            cur[key] = [_scalar(p.strip()) for p in inner.split(",") if p.strip()] if inner else []
            pending_list_key = None
        else:
            cur[key] = _scalar(val)
            pending_list_key = None
    if cur is not None:
        items.append(cur)
    return items


def _scalar(v: str):
    v = v.strip()
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    if v.lstrip("-").isdigit():
        try:
            return int(v)
        except ValueError:
            return v
    return v


# ---------- publication parsing -------------------------------------------

PUB_BLOCK_RE = re.compile(r'<div class="publication-item">(.*?)</div>', re.S)
DOI_RE = re.compile(r'doi\.org/([^"]+)"')
TITLE_RE = re.compile(r'pub-title"><a[^>]*>([^<]+)</a>')
AUTHORS_RE = re.compile(r'pub-authors">(.*?)</span>', re.S)
JOURNAL_RE = re.compile(r'<i>([^<]+)</i>')


def _strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s).strip()


def parse_publications(md_path: Path) -> list[dict]:
    md = md_path.read_text(encoding="utf-8")
    chunks = re.split(r"^## (\d{4})\s*$", md, flags=re.M)
    out = []
    for i in range(1, len(chunks), 2):
        year = int(chunks[i])
        body = chunks[i + 1]
        for block in PUB_BLOCK_RE.findall(body):
            doi_m = DOI_RE.search(block)
            title_m = TITLE_RE.search(block)
            authors_m = AUTHORS_RE.search(block)
            journal_m = JOURNAL_RE.search(block)
            if not (doi_m and title_m):
                raise SystemExit(f"[build] FATAL: malformed publication entry; "
                                 f"missing DOI or title near year {year}")
            out.append({
                "doi": doi_m.group(1),
                "title": title_m.group(1).strip(),
                "authors": _strip_tags(authors_m.group(1)) if authors_m else "",
                "journal": journal_m.group(1).strip() if journal_m else "",
                "year": year,
                "url": f"https://doi.org/{doi_m.group(1)}",
            })
    return out


# ---------- main ----------------------------------------------------------

def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    data = repo / "data"

    research_topics = load_yaml(data / "research_topics.yml")
    tutorial_topics = load_yaml(data / "tutorial_topics.yml")
    methods = load_yaml(data / "methods.yml")
    software = load_yaml(data / "software.yml")
    pub_anno_list = load_yaml(data / "publication_annotations.yml")

    rtopic_slugs = {t["slug"] for t in research_topics}
    ttopic_slugs = {t["slug"] for t in tutorial_topics}
    method_slugs = {m["slug"] for m in methods}
    method_to_ttopics = {m["slug"]: list(m.get("tutorial_topics") or []) for m in methods}

    pub_anno = {a["doi"]: a for a in pub_anno_list}
    pubs = parse_publications(repo / "content" / "publications.md")

    # CI gate: every pub has a DOI (parser already enforces).
    # CI gate: every pub DOI present in annotations.
    missing_anno = [p["doi"] for p in pubs if p["doi"] not in pub_anno]
    if missing_anno:
        print(f"[build] FATAL: {len(missing_anno)} publications without annotations:",
              file=sys.stderr)
        for d in missing_anno[:10]:
            print(f"  - {d}", file=sys.stderr)
        return 2
    extra_anno = [d for d in pub_anno if d not in {p["doi"] for p in pubs}]
    if extra_anno:
        print(f"[build] FATAL: {len(extra_anno)} stale annotations:", file=sys.stderr)
        for d in extra_anno[:10]:
            print(f"  - {d}", file=sys.stderr)
        return 2

    # Soft URL probe (warn, never fail): some repos are private and 404 anonymously.
    if "--probe-net" in sys.argv:
        for sw in software:
            try:
                req = urllib.request.Request(sw["repo"], method="HEAD")
                with urllib.request.urlopen(req, timeout=15) as r:
                    if r.status >= 400:
                        print(f"[build] WARN: {sw['name']} repo HEAD {r.status}: {sw['repo']}",
                              file=sys.stderr)
            except Exception as e:
                print(f"[build] WARN: {sw['name']} repo unreachable ({sw['repo']}): {e}",
                      file=sys.stderr)

    # Tutorials.
    cttir_path = data / "_generated" / "cttir_tutorials.json"
    if not cttir_path.exists():
        print(f"[build] FATAL: {cttir_path} missing — run scripts/fetch_cttir_index.py first",
              file=sys.stderr)
        return 2
    courses = json.loads(cttir_path.read_text(encoding="utf-8"))
    if not courses:
        print("[build] FATAL: zero courses in CTTIR index", file=sys.stderr)
        return 2

    # ---------------- node assembly ------------------------------------
    nodes = []
    for p in pubs:
        a = pub_anno[p["doi"]]
        topics = list(a.get("topics") or [])
        meths = list(a.get("methods") or [])
        for t in topics:
            if t not in rtopic_slugs:
                print(f"[build] FATAL: pub {p['doi']} has unknown topic {t}", file=sys.stderr)
                return 2
        for mt in meths:
            if mt not in method_slugs:
                print(f"[build] FATAL: pub {p['doi']} has unknown method {mt}", file=sys.stderr)
                return 2
        nodes.append({
            "id": f"pub-{p['doi']}",
            "type": "publication",
            "title": p["title"],
            "url": p["url"],
            "year": p["year"],
            "venue": p["journal"],
            "authors": p["authors"],
            "topics": topics,
            "methods": meths,
            "primary_topic": topics[0] if topics else None,
        })
    for sw in software:
        topics = list(sw.get("topics") or [])
        meths = list(sw.get("methods") or [])
        for t in topics:
            if t not in rtopic_slugs:
                print(f"[build] FATAL: sw {sw['name']} has unknown topic {t}", file=sys.stderr)
                return 2
        for mt in meths:
            if mt not in method_slugs:
                print(f"[build] FATAL: sw {sw['name']} has unknown method {mt}", file=sys.stderr)
                return 2
        nodes.append({
            "id": f"sw-{sw['name']}",
            "type": "software",
            "title": sw["name"],
            "url": sw["repo"],
            "docs": sw.get("docs"),
            "language": sw.get("language"),
            "description": sw.get("description"),
            "topics": topics,
            "methods": meths,
            "primary_topic": topics[0] if topics else None,
        })
    for c in courses:
        if c["topic"] not in ttopic_slugs:
            print(f"[build] FATAL: course {c['slug']} has unknown tutorial_topic {c['topic']}",
                  file=sys.stderr)
            return 2
        nodes.append({
            "id": f"course-{c['slug']}",
            "type": "course",
            "title": c["title"],
            "url": c["url"],
            "description": c.get("description") or "",
            "tutorial_topic": c["topic"],
            "tags": c.get("tags") or [],
            "primary_topic": c["topic"],
        })

    # ---------------- topic / method coverage gates --------------------
    rtopic_count = defaultdict(int)
    ttopic_count = defaultdict(int)
    method_count = defaultdict(int)
    for n in nodes:
        if n["type"] in ("publication", "software"):
            for t in n["topics"]:
                rtopic_count[t] += 1
            for mt in n["methods"]:
                method_count[mt] += 1
        else:
            ttopic_count[n["tutorial_topic"]] += 1

    empty_rtopics = [t for t in rtopic_slugs if rtopic_count[t] == 0]
    empty_ttopics = [t for t in ttopic_slugs if ttopic_count[t] == 0]
    empty_methods = [m for m in method_slugs if method_count[m] == 0]
    if empty_rtopics:
        print(f"[build] FATAL: research_topics with zero entities: {empty_rtopics}",
              file=sys.stderr)
        return 2
    if empty_ttopics:
        print(f"[build] FATAL: tutorial_topics with zero courses: {empty_ttopics}",
              file=sys.stderr)
        return 2
    if empty_methods:
        print(f"[build] FATAL: methods with zero entities: {empty_methods}", file=sys.stderr)
        return 2

    # ---------------- edges --------------------------------------------
    edges: list[dict] = []
    edge_seen: set[tuple[str, str, str]] = set()

    def _add(a: str, b: str, kind: str, weight: float):
        if a == b:
            return
        key = (kind, *sorted((a, b)))
        if key in edge_seen:
            return
        edge_seen.add(key)
        edges.append({"source": a, "target": b, "kind": kind, "weight": weight})

    # topic-related edges within pubs+sw (same research topic).
    by_rtopic = defaultdict(list)
    for n in nodes:
        if n["type"] in ("publication", "software"):
            for t in n["topics"]:
                by_rtopic[t].append(n["id"])
    for t, ids in by_rtopic.items():
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                _add(ids[i], ids[j], "topic-related", 1.0)

    # topic-related within courses (same tutorial_topic).
    # 569 courses → naive O(n²) per topic is too dense; cap to 6 nearest neighbours
    # via a sliding window over alphabetical order to keep components connected
    # without saturating. Layout will pull rest in via compound nodes (Phase 3).
    by_ttopic = defaultdict(list)
    for n in nodes:
        if n["type"] == "course":
            by_ttopic[n["tutorial_topic"]].append(n["id"])
    for ids in by_ttopic.values():
        ids = sorted(ids)
        for i, a in enumerate(ids):
            for b in ids[i + 1: i + 4]:
                _add(a, b, "topic-related", 1.0)

    # shared-tags / shared-methods within pubs+sw.
    pub_sw = [n for n in nodes if n["type"] in ("publication", "software")]
    for i in range(len(pub_sw)):
        a = pub_sw[i]
        a_methods = set(a["methods"])
        a_topics = set(a["topics"])
        for j in range(i + 1, len(pub_sw)):
            b = pub_sw[j]
            shared_m = a_methods & set(b["methods"])
            shared_t = a_topics & set(b["topics"])
            if shared_m or len(shared_t) >= 2:
                w = float(min(5, len(shared_m) * 2 + len(shared_t)))
                _add(a["id"], b["id"], "shared-tags", w)

    # cross-domain edges via methods → tutorial_topics.
    # For each pub/sw with method M, find the courses in tutorial_topics(M).
    # Cap at 3 strongest course matches per publication/software.
    # "strongest" = course shares the most tags (or method-relevant words);
    # absent rich tags, pick by tutorial_topic match count.
    courses_by_ttopic = defaultdict(list)
    for n in nodes:
        if n["type"] == "course":
            courses_by_ttopic[n["tutorial_topic"]].append(n)

    for n in pub_sw:
        cap = 3
        cands: list[tuple[float, str, str]] = []
        for mt in n["methods"]:
            for tt in method_to_ttopics.get(mt, []):
                for c in courses_by_ttopic.get(tt, []):
                    score = 1.0
                    title_lower = c["title"].lower()
                    for tag_word in mt.replace("-", " ").split():
                        if len(tag_word) > 4 and tag_word in title_lower:
                            score += 1.0
                    cands.append((score, n["id"], c["id"]))
        cands.sort(reverse=True)
        used = set()
        added = 0
        for score, a, b in cands:
            if b in used:
                continue
            used.add(b)
            _add(a, b, "shared-tags", min(5.0, score + 1.0))
            added += 1
            if added >= cap:
                break

    # CI gate 6: ≥80% of nodes connected.
    connected = set()
    for e in edges:
        connected.add(e["source"])
        connected.add(e["target"])
    coverage = len(connected) / len(nodes) if nodes else 0.0
    if coverage < 0.80:
        print(f"[build] FATAL: edge coverage {coverage:.1%} < 80% "
              f"({len(connected)}/{len(nodes)})", file=sys.stderr)
        return 2

    # ---------------- output -------------------------------------------
    out = {
        "schema_version": 1,
        "topics": {
            "research": research_topics,
            "tutorial": tutorial_topics,
        },
        "methods": methods,
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "nodes_total": len(nodes),
            "publications": sum(1 for n in nodes if n["type"] == "publication"),
            "software": sum(1 for n in nodes if n["type"] == "software"),
            "courses": sum(1 for n in nodes if n["type"] == "course"),
            "edges_total": len(edges),
            "edges_shared_tags": sum(1 for e in edges if e["kind"] == "shared-tags"),
            "edges_topic_related": sum(1 for e in edges if e["kind"] == "topic-related"),
            "edges_used_in": sum(1 for e in edges if e["kind"] == "used-in"),
            "coverage": round(coverage, 4),
        },
    }
    out_path = repo / "static" / "overview" / "graph.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out["stats"], indent=2), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
