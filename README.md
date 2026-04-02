# r-heller.github.io

Personal academic website of R. Heller.
Built with [Hugo](https://gohugo.io/) and the [Coder](https://github.com/luizdepra/hugo-coder/) theme.
Deployed via GitHub Pages.

## Local Development

```bash
# Install Hugo (macOS)
brew install hugo

# Preview locally
hugo server
```

Then open http://localhost:1313/

## Editing Content

- **Publications**: Edit `content/publications.md`
- **R Packages**: Edit `content/r-packages.md`
- **Contact**: Edit `content/contact.md`
- **About**: Edit `content/about.md`
- **Avatar**: Replace `static/images/avatar.svg` with your photo (update `hugo.toml` accordingly)
- **Site config**: Edit `hugo.toml` (title, social links, email, etc.)

## Scripts

- `scripts/bib2hugo.py` — Convert Zotero BibTeX export to publications.md
- `scripts/pubmed2hugo.py` — Fetch publications from PubMed
- `scripts/merge_pubs.py` — Merge Zotero + PubMed into deduplicated publications.md

## Deployment

Push to `main` branch and GitHub Actions builds and deploys automatically.

**First-time setup**: In your GitHub repo settings, go to **Pages** and set Source to **GitHub Actions**.
