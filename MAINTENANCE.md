# Maintenance review — 30 October 2026

## Purpose and acceptance criteria

The academic site should make reviewed publications and software discoverable,
work on mobile and with a keyboard, and build a complete Pages artifact. This
milestone requires working navigation, honest counts, usable failure paths and
checks that reject missing output.

## Findings and repairs

- High: the overview promised a filtered mobile list but implemented no list.
  Added linked text results synchronized with search and filters, a live result
  status, and a useful empty-result message. URLs are restricted to HTTP(S).
- High: a desktop CDN failure prevented all search/filter initialization. The
  list and controls now remain available; the graph reports its failure.
- Medium: saved graph positions were trusted without validating their shape.
  Reject non-object or non-finite cached coordinates and recompute the layout.
- Medium: venue/language counts were hard-coded to zero; venue choices stopped
  after twelve. Calculate actual counts and expose all available venues.
- Medium: empty type selections and comma-containing journal names could not
  survive URL reload. Preserve those states, normalize reversed years, label
  the range inputs and keep their displayed values in sync after reset.
- High release gate: missing legal routes or empty overview JavaScript could
  pass the build scripts. Both now fail; four regression tests cover these paths.
- Documentation named the wrong theme/layout and omitted Go/module requirements.
  README now matches the pinned Hugo Coder module and actual build commands.

## Verification

Hugo extended 0.159.2 and Go 1.27.3 on macOS arm64: complete build passed, with
54 pages, one paginator and 18 aliases. The offline graph builder produced
62 nodes (52 publications, 10 software) and 703 edges. All 763 checked local
HTML links/assets resolved; external endpoints and fragment targets were not
included in that scan. Legal/JavaScript budget guards and four regression tests
passed before the browser work; final checks are recorded below.

Chromium 153 / Playwright 1.63: desktop, 390-pixel mobile, blocked graph CDN and
malformed local storage scenarios passed. Tests exercise no-result search,
clearing search, type filters, empty selection, reset, comma-containing venue
filters and URL reload. No page errors or horizontal overflow were observed.
Normal/mobile screenshots were reviewed. The same browser test is now part of
the build workflow. Analytics was blocked during tests; endpoint behavior and
legal compliance are not certified by these checks.

## First use and next release action

Follow the exact prerequisites and commands in README. `npm run test:browser`
starts its own local static server over `public/` and closes it after testing.
Rerun the graph builder when reviewed source data changes. Publication annotations
and their provenance are preserved; no bibliographic claims were rewritten.

This is locally checked, not deployed. After review and an authorized push,
inspect the existing Pages workflow for that exact commit and exercise the
hosted site. Safari/Firefox, hosted analytics and live outbound URLs remain
unverified. Broader content normalization and a fully offline graph library
are deferred; the list already provides the essential failure path.
