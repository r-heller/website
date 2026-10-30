# r-heller/website

R. Heller's academic site, built with Hugo extended and the pinned
[Hugo Coder](https://github.com/luizdepra/hugo-coder) module. The Pages workflow
publishes pushes to `main`; the maintenance candidate has not been deployed.

## Local development

Install Hugo **extended 0.159.2** (the CI version), Go >= 1.21, and Python >= 3.10.
The first build downloads the pinned theme module. The overview graph builder
uses the standard library; optional PyYAML is not required. Browser checks
add Node 24 and the development-only Playwright dependency in `package-lock.json`.

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build_overview_graph.py
hugo --gc --minify
sh scripts/check-legal-placeholders.sh public
sh scripts/check-overview-budget.sh public
npm ci
npx playwright install chromium
npm run test:browser
hugo server -D
```

Open the URL printed by Hugo. `-D` includes drafts for local review. The graph
must be built before previewing the overview page. It is derived from the tracked
publication list and annotations; no network probe runs unless `--probe-net` is
explicitly supplied. Generated graph/build files are ignored by Git.

## Structure and editing

- `content/`: Markdown pages and sections. Legal pages are `impressum.md` and
  `privacy.md`; their rendered routes are `/impressum/` and `/privacy/`.
- `data/`: reviewed publication, topic, method and software annotations.
- `go.mod` and `go.sum`: pinned external theme, downloaded by Hugo modules.
- `layouts/`: project overrides, including `_partials/header.html` and
  `partials/head/extensions.html`.
- `static/`: custom CSS, images and overview JavaScript. `assets/` supplies Hugo
  Pipes inputs where referenced by templates.
- `scripts/`: overview generation and build guards. Guards require built legal
  pages and a nonempty overview JS directory; they fail on unresolved tokens.

Edit `hugo.toml` for the nested Contributions menu, site metadata and theme
settings. Add a Markdown file with title/date/draft front matter for a new post.
Keep publication DOIs and annotation records in sync; the graph builder rejects
missing or stale annotations rather than inventing relationships.

## Analytics and publication

`layouts/partials/head/extensions.html` loads a script from
`analytics.hellebo.de`. Review the actual endpoint behavior and privacy notice
when changing analytics. Placeholder checks do not establish legal compliance.
The overview uses a pinned third-party graph library with an integrity hash.
The keyboard-accessible list, search and filters remain available if it fails.
Filter URLs preserve empty type selections and journal names containing commas.
The graph cache is checked before reuse; its
320 KiB check covers this repository's overview JavaScript, excluding those CDNs.

The existing workflow builds the graph and site, runs the guards, and deploys a
Pages artifact. Hosted CI results and publication must be checked for the exact
commit after an authorized push. Local verification is recorded in
[MAINTENANCE.md](MAINTENANCE.md).

Code is under [LICENSE](LICENSE). Review separate content and third-party asset
rights before reuse; an included bibliography is provenance, not a blanket
content license.
