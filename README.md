# r-heller/website

Personal academic website of R. Heller. Built with [Hugo](https://gohugo.io/) (extended) and a small in-repo `academic` theme. Deployed to GitHub Pages via Actions on every push to `main`.

Live: <https://r-heller.github.io/website/>

## Local development

```sh
hugo server -D    # http://localhost:1313/website/ — drafts on
hugo --quiet      # one-shot build into ./public
```

Requires Hugo extended ≥ 0.141 (CI uses 0.159).

## Layout

| Path | Purpose |
|---|---|
| `content/` | Page sources (Markdown). Top-level files = main pages; subdirs = sections (`blog/`, `courses/`, `tutorials/`, `legal/`). |
| `content/legal/` | `impressum.md`, `datenschutz.md`, `haftungsausschluss.md` — DSGVO-compliant German legal pages. |
| `themes/academic/` | In-repo theme. Templates and base CSS live here; do not edit unless redesigning. |
| `layouts/` | Project-level overrides that take precedence over the theme. |
| `layouts/_default/baseof.html` | Loads custom CSS and the Plausible script. |
| `layouts/partials/header.html` | Top nav, including the **Rechtliches** dropdown (nested menus). |
| `layouts/partials/footer.html` | Footer with the three legal links. |
| `layouts/partials/head/extensions.html` | Self-hosted Plausible Analytics script. |
| `static/` | Files copied verbatim to the site root (`/css/custom.css`, `/images/...`). |
| `assets/` | Hugo Pipes inputs (currently unused at build time; CSS is served from `static/`). |
| `scripts/check-legal-placeholders.sh` | CI guard — fails the build if `{{...}}` placeholders or `TODO`/`FIXME` survive into `public/legal/`. |
| `Exported Items.bib` | Zotero export, retained for future regeneration of `content/publications.md`. |
| `.github/workflows/deploy.yml` | Build → placeholder check → upload artifact → deploy to Pages. |

## Adding content

- **A page** (about, contact, etc.): edit the corresponding file in `content/`.
- **A blog post / course / tutorial**: add a Markdown file under the relevant section, e.g. `content/blog/2026-05-thing.md`. Front matter: `title`, `date`, `draft: false`.

## Navigation

The top nav is configured in `hugo.toml` under `[[menu.main]]`. The "Rechtliches" entry uses Hugo's nested menu pattern (`identifier = "rechtliches"` + child entries with `parent = "rechtliches"`). The custom `header.html` partial renders nested entries as a dropdown.

## Analytics

Plausible is loaded from a self-hosted instance for `r-heller.github.io/website`. It uses no cookies and no personal data; documented in `content/legal/datenschutz.md`. To change the endpoint or disable, edit the `<script>` tag in `layouts/partials/head/extensions.html`.

## Legal pages

The three files under `content/legal/` are written in German and tailored to a single Diensteanbieter (R. Heller, Hoyerswerda). Aliases redirect the legacy `/impressum/` and `/privacy/` URLs. Edits to legal text go directly in those Markdown files; the placeholder script in CI prevents stray `{{TOKENS}}` from reaching production.

## Deployment

`git push origin main` → Actions builds with Hugo, runs the placeholder check, and publishes via `actions/deploy-pages`. Manual run: workflow dispatch on the **Deploy Hugo site to GitHub Pages** workflow.

First-time GitHub Pages setup: **Settings → Pages → Source: GitHub Actions**.

## License

Code under [LICENSE](./LICENSE). Editorial content © R. Heller, all rights reserved (see `content/legal/haftungsausschluss.md`).
