#!/usr/bin/env python3
"""
merge_pubs.py — Merge Zotero BibTeX + PubMed into a single deduplicated publications.md

Strategy:
  1. Parse Zotero .bib (ground truth — these are definitely yours)
  2. Fetch PubMed results
  3. Match by DOI (normalized)
  4. For Zotero entries: use Zotero metadata, supplement missing fields from PubMed
  5. For PubMed-only entries: include them (they're from your author query)
  6. Deduplicate and output grouped by year, descending
"""

import argparse
import re
import sys
import time
from collections import defaultdict, OrderedDict

try:
    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    from bibtexparser.customization import convert_to_unicode
except ImportError:
    print("Error: pip install bibtexparser", file=sys.stderr)
    sys.exit(1)

try:
    import requests
except ImportError:
    print("Error: pip install requests", file=sys.stderr)
    sys.exit(1)


# --- Helpers ---

def normalize_doi(doi: str) -> str:
    if not doi:
        return ""
    doi = doi.strip().lower()
    doi = re.sub(r'^https?://doi\.org/', '', doi)
    doi = re.sub(r'^doi:\s*', '', doi)
    return doi


def clean_latex(text: str) -> str:
    if not text:
        return ""
    text = text.replace("{", "").replace("}", "")
    text = text.replace("\\relax ", "").replace("\\relax", "")
    replacements = {
        "\\&": "&", "\\textendash": "\u2013", "\\textemdash": "\u2014",
        "\\'e": "\u00e9", "\\'a": "\u00e1", '\\"u': "\u00fc", '\\"o': "\u00f6",
        '\\"a': "\u00e4", "\\ss": "\u00df", "~": " ", "\\,": " ",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    text = re.sub(r"\\[a-zA-Z]+", "", text)
    return text.strip()


def format_authors_bib(authors_str: str, bold_patterns: list) -> str:
    if not authors_str:
        return ""
    authors = [a.strip() for a in authors_str.split(" and ")]
    formatted = []
    for author in authors:
        author = clean_latex(author)
        if "," in author:
            parts = author.split(",", 1)
            last = parts[0].strip()
            first = parts[1].strip()
            author = f"{first} {last}" if first else last
        is_bold = any(pat.lower() in author.lower() for pat in bold_patterns)
        formatted.append(f"<b>{author}</b>" if is_bold else author)
    return ", ".join(formatted)


def format_authors_pubmed(author_list: list, bold_patterns: list) -> str:
    if not author_list:
        return ""
    formatted = []
    for author in author_list:
        name = author.get("name", "")
        is_bold = any(pat.lower() in name.lower() for pat in bold_patterns)
        formatted.append(f"<b>{name}</b>" if is_bold else name)
    return ", ".join(formatted)


# --- PubMed fetching ---

ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"


def pubmed_search(query: str) -> list:
    resp = requests.get(ESEARCH, params={
        "db": "pubmed", "term": query, "retmax": 500, "retmode": "json", "sort": "date"
    })
    resp.raise_for_status()
    pmids = resp.json().get("esearchresult", {}).get("idlist", [])
    print(f"  PubMed: {len(pmids)} results", file=sys.stderr)
    return pmids


def pubmed_fetch(pmids: list) -> list:
    articles = []
    for i in range(0, len(pmids), 100):
        batch = pmids[i:i+100]
        resp = requests.get(ESUMMARY, params={
            "db": "pubmed", "id": ",".join(batch), "retmode": "json"
        })
        resp.raise_for_status()
        result = resp.json().get("result", {})
        for pmid in batch:
            if pmid in result:
                articles.append(result[pmid])
        if i + 100 < len(pmids):
            time.sleep(0.4)
    return articles


def get_pubmed_doi(article: dict) -> str:
    for aid in article.get("articleids", []):
        if aid.get("idtype") == "doi":
            return normalize_doi(aid.get("value", ""))
    return ""


# --- Unified publication record ---

def bib_to_record(entry: dict) -> dict:
    doi = normalize_doi(entry.get("doi", ""))
    year = str(entry.get("year", "Unknown"))
    title = clean_latex(entry.get("title", "Untitled"))
    journal = clean_latex(entry.get("journal", entry.get("booktitle", "")))
    volume = entry.get("volume", "")
    number = entry.get("number", "")
    pages = entry.get("pages", "").replace("--", "\u2013")
    return {
        "source": "zotero",
        "doi": doi,
        "year": year,
        "title": title,
        "journal": journal,
        "volume": volume,
        "number": number,
        "pages": pages,
        "authors_raw": entry.get("author", ""),
        "pubmed_authors": None,
    }


def pubmed_to_record(article: dict) -> dict:
    doi = get_pubmed_doi(article)
    pubdate = article.get("pubdate", "")
    year = pubdate.split(" ")[0] if pubdate else ""
    if not year.isdigit():
        year = article.get("sortpubdate", "").split("/")[0]
    if not year or not year.isdigit():
        year = "Unknown"
    return {
        "source": "pubmed",
        "doi": doi,
        "year": year,
        "title": article.get("title", "Untitled").rstrip("."),
        "journal": article.get("fulljournalname", article.get("source", "")),
        "volume": article.get("volume", ""),
        "number": article.get("issue", ""),
        "pages": article.get("pages", ""),
        "authors_raw": None,
        "pubmed_authors": article.get("authors", []),
        "pmid": article.get("uid", ""),
    }


# --- Rendering ---

def render_record(rec: dict, bold_patterns: list) -> str:
    if rec.get("authors_raw"):
        authors = format_authors_bib(rec["authors_raw"], bold_patterns)
    elif rec.get("pubmed_authors"):
        authors = format_authors_pubmed(rec["pubmed_authors"], bold_patterns)
    else:
        authors = ""

    title = rec["title"]
    doi = rec.get("doi", "")
    journal = rec.get("journal", "")
    volume = rec.get("volume", "")
    number = rec.get("number", "")
    pages = rec.get("pages", "")
    year = rec.get("year", "")

    if doi:
        doi_url = f"https://doi.org/{doi}"
        title_html = f'<a href="{doi_url}">{title}</a>'
    elif rec.get("pmid"):
        title_html = f'<a href="https://pubmed.ncbi.nlm.nih.gov/{rec["pmid"]}/">{title}</a>'
    else:
        title_html = title

    journal_html = f"<b><i>{journal}</i></b>" if journal else ""
    ref_parts = []
    if year:
        ref_parts.append(year)
    vol_str = volume
    if vol_str and number:
        vol_str += f"({number})"
    if vol_str:
        ref_parts.append(vol_str)
    if pages:
        if ref_parts:
            ref_parts[-1] += f":{pages}"
        else:
            ref_parts.append(pages)
    if ref_parts:
        journal_html += ". " + ", ".join(ref_parts) + "."

    return (
        f'<div class="publication-item">\n'
        f'<span class="pub-authors">{authors}.</span>\n'
        f'<span class="pub-title">{title_html}.</span>\n'
        f'<span class="pub-journal">{journal_html}</span>\n'
        f'</div>\n'
    )


# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="Merge Zotero + PubMed publications")
    parser.add_argument("bibfile", help="Zotero .bib export")
    parser.add_argument("--pubmed-query",
        default='"Heller RA"[Author] OR "Heller Raban"[Author] OR "Heller Raban Arved"[Author]',
        help="PubMed search query")
    parser.add_argument("--bold-patterns", nargs="+", default=["Heller"])
    parser.add_argument("--output", "-o", default=None)
    parser.add_argument("--skip-pubmed", action="store_true", help="Only use Zotero data")
    args = parser.parse_args()

    # 1. Parse Zotero
    print("Parsing Zotero BibTeX...", file=sys.stderr)
    bib_parser = BibTexParser(common_strings=True)
    bib_parser.customization = convert_to_unicode
    with open(args.bibfile, encoding="utf-8") as f:
        raw_bib = f.read()
    raw_bib = raw_bib.replace("{\\relax ", "{").replace("\\relax ", "").replace("\\relax", "")
    import io
    bib_db = bibtexparser.load(io.StringIO(raw_bib), parser=bib_parser)
    print(f"  Zotero: {len(bib_db.entries)} entries", file=sys.stderr)

    records = OrderedDict()
    no_doi_records = []

    for entry in bib_db.entries:
        rec = bib_to_record(entry)
        doi = rec["doi"]
        if doi:
            records[doi] = rec
        else:
            no_doi_records.append(rec)

    # 2. Fetch PubMed
    if not args.skip_pubmed:
        print("Fetching PubMed...", file=sys.stderr)
        pmids = pubmed_search(args.pubmed_query)
        articles = pubmed_fetch(pmids)
        print(f"  PubMed: {len(articles)} articles fetched", file=sys.stderr)

        known_coauthors = {
            "biglari", "moghaddam", "schomburg", "haubruck", "seelig",
            "hackler", "chillon", "demircan", "sun q", "bock t",
            "sperl", "daniel", "raven", "pilz", "diegmann",
            "bachmann", "tanner", "schmidmaier", "westhauser", "younsi",
            "gr\u00fctzner", "grutzner", "miska", "ferbert", "swing",
            "willy", "back da", "estel", "torri", "gaab",
            "tjardes", "trentzsch", "karadjian", "belhadj",
            "haase", "maares", "seibert", "cherkezov", "minich",
            "reible", "klingenberg", "lescure", "persani",
            "rayman", "taylor ew", "hughes dj", "du laing",
            "massoud", "bazarbachi", "blenkinsop", "alhalabi",
        }

        def is_likely_mine(article):
            authors = article.get("authors", [])
            author_names = " ".join(a.get("name", "").lower() for a in authors)
            for coauth in known_coauthors:
                if coauth in author_names:
                    return True
            title = article.get("title", "").lower()
            sci_keywords = ["spinal cord", "selenium", "zinc", "trace element",
                           "selenoprotein", "covid-19", "sars-cov", "non-union",
                           "bone", "fracture", "orthop", "trauma"]
            for kw in sci_keywords:
                if kw in title:
                    return True
            return False

        pubmed_only = 0
        skipped = 0
        supplemented = 0
        for article in articles:
            pm_rec = pubmed_to_record(article)
            doi = pm_rec["doi"]
            if doi and doi in records:
                zot = records[doi]
                if not zot["journal"] and pm_rec["journal"]:
                    zot["journal"] = pm_rec["journal"]
                    supplemented += 1
                if not zot["pages"] and pm_rec["pages"]:
                    zot["pages"] = pm_rec["pages"]
                if not zot["number"] and pm_rec["number"]:
                    zot["number"] = pm_rec["number"]
            elif doi:
                if is_likely_mine(article):
                    records[doi] = pm_rec
                    pubmed_only += 1
                else:
                    skipped += 1
                    print(f"  Skipped (likely different Heller): {pm_rec['title'][:70]}...", file=sys.stderr)
            else:
                pm_title = pm_rec["title"].lower()[:60]
                found = False
                for r in list(records.values()) + no_doi_records:
                    if r["title"].lower()[:60] == pm_title:
                        found = True
                        break
                if not found and is_likely_mine(article):
                    no_doi_records.append(pm_rec)
                    pubmed_only += 1

        print(f"  Supplemented: {supplemented} Zotero entries enriched", file=sys.stderr)
        print(f"  PubMed-only: {pubmed_only} new entries added", file=sys.stderr)
        print(f"  Skipped: {skipped} entries (likely different author)", file=sys.stderr)

    all_records = list(records.values()) + no_doi_records
    total = len(all_records)

    by_year = defaultdict(list)
    for rec in all_records:
        by_year[rec["year"]].append(rec)

    sorted_years = sorted(by_year.keys(), key=lambda y: int(y) if y.isdigit() else 0, reverse=True)

    lines = [
        "---",
        'title: "Publications"',
        "date: 2025-01-01",
        "---",
        "",
        f"<!-- {total} publications (Zotero + PubMed merged) -->",
        "",
    ]

    for year in sorted_years:
        entries = by_year[year]
        entries.sort(key=lambda r: (r.get("authors_raw") or "").split(",")[0].lower())
        lines.append(f"## {year}\n")
        for rec in entries:
            lines.append(render_record(rec, args.bold_patterns))
        lines.append("")

    output = "\n".join(lines)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"{total} publications written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
