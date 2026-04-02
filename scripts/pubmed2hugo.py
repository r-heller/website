#!/usr/bin/env python3
"""
pubmed2hugo.py — Fetch publications from PubMed and generate Hugo publications.md

Usage:
    python3 pubmed2hugo.py --orcid 0000-0001-8006-9742
    python3 pubmed2hugo.py --author "Heller RA" --output content/publications.md

Requirements:
    pip install requests

This uses the NCBI E-utilities API (free, no key required for <3 req/sec).
For heavier use, register at https://www.ncbi.nlm.nih.gov/account/ and pass --api-key.
"""

import argparse
import json
import re
import sys
import time
from collections import defaultdict

try:
    import requests
except ImportError:
    print("Error: requests not installed. Run: pip install requests", file=sys.stderr)
    sys.exit(1)

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"


def search_pubmed(query: str, api_key: str = None) -> list[str]:
    """Search PubMed and return list of PMIDs."""
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": 500,
        "retmode": "json",
        "sort": "date",
    }
    if api_key:
        params["api_key"] = api_key

    resp = requests.get(ESEARCH_URL, params=params)
    resp.raise_for_status()
    data = resp.json()

    pmids = data.get("esearchresult", {}).get("idlist", [])
    count = data.get("esearchresult", {}).get("count", "0")
    print(f"Found {count} results, fetching {len(pmids)} PMIDs...", file=sys.stderr)
    return pmids


def fetch_summaries(pmids: list[str], api_key: str = None) -> list[dict]:
    """Fetch article summaries from PubMed."""
    if not pmids:
        return []

    articles = []
    # Process in batches of 100
    for i in range(0, len(pmids), 100):
        batch = pmids[i:i + 100]
        params = {
            "db": "pubmed",
            "id": ",".join(batch),
            "retmode": "json",
        }
        if api_key:
            params["api_key"] = api_key

        resp = requests.get(ESUMMARY_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

        result = data.get("result", {})
        for pmid in batch:
            if pmid in result:
                articles.append(result[pmid])

        if i + 100 < len(pmids):
            time.sleep(0.4)  # rate limit

    return articles


def format_authors(author_list: list[dict], bold_patterns: list[str]) -> str:
    """Format PubMed author list with bolding."""
    if not author_list:
        return ""

    formatted = []
    for author in author_list:
        name = author.get("name", "")
        is_bold = any(pat.lower() in name.lower() for pat in bold_patterns)
        if is_bold:
            formatted.append(f"<b>{name}</b>")
        else:
            formatted.append(name)

    return ", ".join(formatted)


def format_article(article: dict, bold_patterns: list[str]) -> str:
    """Format a single PubMed article as HTML."""
    authors = format_authors(article.get("authors", []), bold_patterns)
    title = article.get("title", "Untitled").rstrip(".")
    journal = article.get("fulljournalname", article.get("source", ""))
    volume = article.get("volume", "")
    issue = article.get("issue", "")
    pages = article.get("pages", "")
    year = article.get("pubdate", "").split(" ")[0]  # "2024 Jan" -> "2024"

    # Get DOI from articleids
    doi = ""
    for aid in article.get("articleids", []):
        if aid.get("idtype") == "doi":
            doi = aid.get("value", "")
            break

    # Title with DOI link
    if doi:
        doi_url = f"https://doi.org/{doi}" if not doi.startswith("http") else doi
        title_html = f'<a href="{doi_url}">{title}</a>'
    else:
        pmid = article.get("uid", "")
        if pmid:
            title_html = f'<a href="https://pubmed.ncbi.nlm.nih.gov/{pmid}/">{title}</a>'
        else:
            title_html = title

    # Journal reference
    journal_html = f"<b><i>{journal}</i></b>" if journal else ""
    ref_parts = []
    if year:
        ref_parts.append(year)
    vol_str = volume
    if vol_str and issue:
        vol_str += f"({issue})"
    if vol_str:
        ref_parts.append(vol_str)
    if pages:
        if ref_parts:
            ref_parts[-1] = ref_parts[-1] + f":{pages}"
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


def main():
    parser = argparse.ArgumentParser(
        description="Fetch PubMed publications and generate Hugo publications.md"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--orcid", help="ORCID iD (e.g., 0000-0001-8006-9742)")
    group.add_argument("--author", help="PubMed author search (e.g., 'Heller RA')")
    group.add_argument("--query", help="Custom PubMed search query")

    parser.add_argument(
        "--bold-patterns", nargs="+", default=["Heller"],
        help="Name patterns to bold (default: Heller)"
    )
    parser.add_argument("--output", "-o", default=None, help="Output file path")
    parser.add_argument("--api-key", default=None, help="NCBI API key (optional)")

    args = parser.parse_args()

    # Build search query
    if args.orcid:
        query = f"{args.orcid}[auid]"
    elif args.author:
        query = f"{args.author}[Author]"
    else:
        query = args.query

    print(f"Searching PubMed: {query}", file=sys.stderr)

    # Search and fetch
    pmids = search_pubmed(query, args.api_key)
    articles = fetch_summaries(pmids, args.api_key)

    # Group by year
    by_year = defaultdict(list)
    for article in articles:
        year = article.get("pubdate", "Unknown").split(" ")[0]
        if not year.isdigit():
            year = article.get("sortpubdate", "").split("/")[0]
        if not year.isdigit():
            year = "Unknown"
        by_year[year].append(article)

    sorted_years = sorted(by_year.keys(), reverse=True)

    # Build output
    lines = [
        "---",
        'title: "Publications"',
        "date: 2025-01-01",
        "---",
        "",
        f"<!-- Generated from PubMed ({len(articles)} articles) by pubmed2hugo.py -->",
        "",
    ]

    for year in sorted_years:
        entries = by_year[year]
        lines.append(f"## {year}\n")
        for article in entries:
            lines.append(format_article(article, args.bold_patterns))
        lines.append("")

    output = "\n".join(lines)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Written {len(articles)} publications to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
