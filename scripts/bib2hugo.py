#!/usr/bin/env python3
"""
bib2hugo.py — Convert a Zotero BibTeX export to a Hugo publications.md page.

Usage:
    python3 bib2hugo.py my_publications.bib > content/publications.md

    Or with options:
    python3 bib2hugo.py my_publications.bib \
        --author "R.A. Heller" \
        --bold-patterns "Heller" \
        --output content/publications.md

Requirements:
    pip install bibtexparser

The script:
  - Parses .bib files exported from Zotero
  - Groups entries by year (descending)
  - Bolds your name in the author list
  - Links titles to DOIs when available
  - Outputs Hugo-compatible Markdown with HTML for the YuLab publication style
"""

import argparse
import re
import sys
from collections import defaultdict

try:
    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    from bibtexparser.customization import convert_to_unicode
except ImportError:
    print("Error: bibtexparser not installed. Run: pip install bibtexparser", file=sys.stderr)
    sys.exit(1)


def clean_latex(text: str) -> str:
    """Remove common LaTeX artifacts from BibTeX fields."""
    if not text:
        return ""
    # Remove braces
    text = text.replace("{", "").replace("}", "")
    # Common LaTeX commands
    replacements = {
        "\\&": "&",
        "\\textendash": "\u2013",
        "\\textemdash": "\u2014",
        "\\'e": "\u00e9",
        "\\'a": "\u00e1",
        '\\"u': "\u00fc",
        '\\"o': "\u00f6",
        '\\"a': "\u00e4",
        "\\ss": "\u00df",
        "~": " ",
        "\\,": " ",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    # Remove remaining backslash commands
    text = re.sub(r"\\[a-zA-Z]+", "", text)
    return text.strip()


def format_authors(authors_str: str, bold_patterns: list[str]) -> str:
    """
    Format author string and bold matching names.

    BibTeX authors are separated by ' and '.
    Each author is 'Last, First' or 'First Last'.
    """
    if not authors_str:
        return ""

    authors = [a.strip() for a in authors_str.split(" and ")]
    formatted = []

    for author in authors:
        author = clean_latex(author)
        # Convert "Last, First" to "First Last" if needed
        if "," in author:
            parts = author.split(",", 1)
            author = f"{parts[1].strip()} {parts[0].strip()}"

        # Bold if matches any pattern
        is_bold = any(pat.lower() in author.lower() for pat in bold_patterns)
        if is_bold:
            formatted.append(f"<b>{author}</b>")
        else:
            formatted.append(author)

    return ", ".join(formatted)


def format_entry(entry: dict, bold_patterns: list[str]) -> str:
    """Format a single BibTeX entry as an HTML publication item."""
    authors = format_authors(entry.get("author", ""), bold_patterns)
    title = clean_latex(entry.get("title", "Untitled"))
    journal = clean_latex(entry.get("journal", entry.get("booktitle", "")))
    year = entry.get("year", "")
    volume = entry.get("volume", "")
    number = entry.get("number", "")
    pages = entry.get("pages", "").replace("--", "\u2013")
    doi = entry.get("doi", "")

    # Build title with DOI link
    if doi:
        doi_url = doi if doi.startswith("http") else f"https://doi.org/{doi}"
        title_html = f'<a href="{doi_url}">{title}</a>'
    else:
        title_html = title

    # Build journal reference
    journal_html = ""
    if journal:
        journal_html = f"<b><i>{journal}</i></b>"
        ref_parts = []
        if year:
            ref_parts.append(year)
        vol_str = ""
        if volume:
            vol_str = volume
            if number:
                vol_str += f"({number})"
        if vol_str:
            ref_parts.append(vol_str)
        if pages:
            ref_parts[-1] = ref_parts[-1] + f":{pages}" if ref_parts else pages

        if ref_parts:
            journal_html += ". " + ", ".join(ref_parts)
        journal_html += "."

    return (
        f'<div class="publication-item">\n'
        f'<span class="pub-authors">{authors}.</span>\n'
        f'<span class="pub-title">{title_html}.</span>\n'
        f'<span class="pub-journal">{journal_html}</span>\n'
        f'</div>\n'
    )


def main():
    parser = argparse.ArgumentParser(
        description="Convert BibTeX to Hugo publications.md (YuLab style)"
    )
    parser.add_argument("bibfile", help="Path to .bib file (Zotero export)")
    parser.add_argument(
        "--bold-patterns",
        nargs="+",
        default=["Heller"],
        help="Name patterns to bold in author lists (default: Heller)",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file path (default: stdout)",
    )
    args = parser.parse_args()

    # Parse BibTeX
    bib_parser = BibTexParser(common_strings=True)
    bib_parser.customization = convert_to_unicode

    with open(args.bibfile, encoding="utf-8") as f:
        bib_db = bibtexparser.load(f, parser=bib_parser)

    # Group by year
    by_year = defaultdict(list)
    for entry in bib_db.entries:
        year = entry.get("year", "Unknown")
        by_year[year].append(entry)

    # Sort years descending
    sorted_years = sorted(by_year.keys(), reverse=True)

    # Build output
    lines = [
        "---",
        'title: "Publications"',
        "date: 2025-01-01",
        "---",
        "",
        f"<!-- Generated from {args.bibfile} by bib2hugo.py -->",
        f"<!-- {len(bib_db.entries)} publications total -->",
        "",
    ]

    for year in sorted_years:
        entries = by_year[year]
        # Sort entries within year (by first author last name)
        entries.sort(key=lambda e: e.get("author", "").split(",")[0].lower())

        lines.append(f"## {year}\n")
        for entry in entries:
            lines.append(format_entry(entry, args.bold_patterns))
        lines.append("")

    output = "\n".join(lines)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Written {len(bib_db.entries)} publications to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
