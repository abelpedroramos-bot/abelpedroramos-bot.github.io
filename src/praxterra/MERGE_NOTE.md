# Merge note: PRAXTERRA section into the fieldreadyqhse.com build (r2, 24 Nov 2026)

For: Claude Code on the Mac mini (hub: 01_Claude/Outbox/T-JEN-20261124-1405_website_r2/repo).
Do this only after Abel approves the preview. Nothing here is published.

This module was built from Drive because the r2 repo was not reachable from the chat. It is
self-contained, so it does not depend on the r2 generator's classes or templates.

## What it writes

`python3 build_praxterra.py --site-root <repo root>` creates `/praxterra/` only:

- `/praxterra/index.html` (section page with comparison table)
- `/praxterra/<slug>/index.html` for self-assessment-tool, records-pack, starter-kit, professional-toolkit
- `/praxterra/licence/index.html`
- `/praxterra/assets/` (praxterra.css, self-hosted Archivo and Public Sans fonts with OFL licences, images)

It also writes `home_block.html` (homepage block) and `sitemap_urls.txt` next to the script.
It needs `/assets/logo.png` and `/assets/favicon.png` from the main site (both exist in r2).

## Steps

1. Copy this folder to `src/praxterra/` in the repo.
2. Run `python3 src/praxterra/build_praxterra.py --site-root <repo root>` (no `--preview`).
3. In the main generator, insert the contents of `home_block.html` on the homepage after the last product group.
4. Add a nav item "PRAXTERRA" → `praxterra/` and a footer link in the main generator.
5. Add the six URLs in `sitemap_urls.txt` to sitemap.xml.
6. Check `FRQ_LINKS` at the top of the script against r2's real paths (home, packs anchor, contact anchor, legal/terms, legal/refund, legal/privacy). Fix there if they differ.
7. r2's CHECKS.md greps for "PRAXTERRA" and expects 0 hits. Exclude `/praxterra/` and the homepage block from that check, since PRAXTERRA is now meant to be there.
8. Run the link checker: 0 broken links expected (the preview had 210 internal refs, 0 broken).
9. When Gumroad products exist, fill `gumroad_url` in `praxterra_catalogue.json` and rebuild. Empty URL = disabled "Available soon" button and no Gumroad script.

## Rules this module follows (Abel, 24 Nov 2026)

- PRAXTERRA is a voluntary standard: never "official", "certified", "accredited", or equivalent to ISO, EMAS or BREEAM. No other scheme's logos or text.
- The standard stays free on praxterra.com; buying a tool never earns points or a level.
- Professional Toolkit outputs are "Result Report Templates", never certificates.
- The standard is "Version 1.0 (Edition 1)", never "draft".
- No personal address or phone number. Images are shown with object-fit: contain (never stretched).
