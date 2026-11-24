# fieldreadyqhse.com: how the site is built

One file drives every page: `src/catalogue.json`. `src/build.py` reads it and writes the whole site into the
repository root (`index.html`, the topic folders, product pages, help and legal pages, `404.html`, `sitemap.xml`,
`robots.txt`, `CNAME`, `.nojekyll`). It needs only Python 3.8 or newer, with no extra packages.

```
python3 src/build.py              # build into the repo root (GitHub Pages: "Deploy from branch, / (root)")
python3 src/build.py --out docs   # or build into docs/ (GitHub Pages: "/docs")
python3 -m http.server 8000       # preview: run it in the folder you built into, then open http://localhost:8000
```

Links are root-relative (`/safety/hse-plan/`), so preview the site through `http.server`, not by double-clicking the files.

## Folder layout

```
repo/
  index.html, 404.html, sitemap.xml, robots.txt, CNAME, .nojekyll   <- built, do not edit by hand
  quality/ safety/ environment/ hr-inductions/ toolbox-talks/        <- topic pages + product pages (built)
  bundles/ management-systems/ shop/ about/ help/ legal/             <- collection, help and legal pages (built)
  assets/                                                            <- copied from src/assets + src/media (built)
  src/
    build.py          the generator
    catalogue.json    THE data: site settings, topics, products, courses, help/legal text
    assets/           styles.css, site.js, logo, favicon, fonts (self-hosted, no Google calls)
    media/<slug>/     product images (01.jpg = hero) and video.mp4, already web-sized
```

## catalogue.json in short

- `site`: domain, e-mail, seller line, location, footer and band text, licence summary, refund line, `free_sample_url`
  (leave "" until a free product exists; the "Free sample" menu item then appears by itself).
- `topics`: one entry per topic (`kind: "topic"`, shown in the "Shop by topic" menu) or collection
  (`kind: "collection"`: Bundles, Management System Packs). Each has a key, name, URL path, colour and blurb.
- `families`: one record per product page. Standard and Premium are `variants` of ONE family, so they share one
  page and one URL with a selector.
- `courses`: the Udemy courses shown in the footer and on the Toolbox Talks page.
- `pages`: the About, Help, Licence, Refunds, FAQ, Contact, Terms, Privacy and Seller information pages (HTML; `{EMAIL}`,
  `{SELLER}`, `{LOCATION}`, `{UPDATED}` are filled in from `site`).

### A family record

```json
{
 "slug": "hse-plan",                       // URL = /<topic path>/<slug>/  -> keep it stable forever
 "topic": "safety",                        // main topic (colour, URL, breadcrumb)
 "tags": ["management-systems", "bundles"],// extra topics/collections where it also appears
 "family": "HSEP", "edition": "ED01", "language": "EN",
 "status": "live",                         // live | coming_soon | retired
 "hidden": false,                          // true = kept in the data but no page is built
 "order": 2, "badge": "",                  // sort order inside a topic, optional yellow badge
 "title": "...", "short": "...", "intro": "...",
 "includes": ["..."], "formats": ["DOCX","XLSX","PPTX","PDF"],
 "stats": [["113","page HSE plan"], ["5","signed HSE forms"], ["132","training slides"]],
 "note": "...", "upgrade_note": "",
 "bundles": ["emergency-packs-bundle"],    // bundles that contain this pack ("Save with the bundle")
 "contains": [],                           // for a bundle: the slugs of the packs inside it
 "images": ["/assets/media/hse-plan/01.jpg", "..."], "video": "/assets/media/hse-plan/video.mp4",
 "variants": [
  {"key": "standard", "name": "Standard", "price_ex_vat": 39.84, "gumroad_url": "", "etsy_id": "4618832885",
   "status": "live", "includes_heading": "Standard", "includes": ["..."]},
  {"key": "premium", "name": "Premium", "price_ex_vat": 80.49, "gumroad_url": "", "etsy_id": "4618844066",
   "status": "live", "includes_heading": "Premium adds", "includes": ["..."]}
 ]
}
```

Text must come from the product's live listing: no new claims, no AI wording, Field Ready QHSE is the only brand.
`etsy_id` is only for our own reference (which files to deliver); it is never shown on the site.

## How to…

**Switch on checkout for a product.** Create the product in Gumroad with the same files as its listing, then paste its link
(`https://<shop>.gumroad.com/l/<product>`) into that variant's `gumroad_url` and rebuild. The grey "Available soon"
button becomes a "Buy now" button that opens the Gumroad overlay. `gumroad.js` is only loaded on pages that have at least
one live Gumroad link.

**Add a product.** Put its images in `src/media/<slug>/` (01.jpg = hero, square, about 1400 px, JPEG) and an optional
`video.mp4`. Add one family record (copy a similar one), with a new `slug`, its `topic`, `tags` and one variant. Rebuild.
The topic pages, menus, related products, sitemap and home sections update by themselves.

**Add a variant (e.g. a Premium edition next to an existing Standard).** Add one object to that family's `variants`
with a new `key`. Use `includes` for what that variant adds. The page then shows the selector automatically. Don't create
a second family: the URL must stay the same.

**Bring out a new edition (e.g. ED01 → ED02).** Edit the family in place: change `edition`, the text, images and
prices, and the `etsy_id`/`gumroad_url` of each variant. Keep the `slug`, so the URL doesn't change. Optional:
`upgrade_note` ("Bought ED01? …"). Don't add a new family for a new edition.

**Retire a product.** Set `"status": "retired"` (no page is built; links from other pages disappear). For a product
that is not ready yet, use `"status": "coming_soon"` (page with no buy button) or `"hidden": true` (no page at all).

**Add a topic.** Add one entry to `topics` (`key`, `kind: "topic"`, `name`, `short`, `path`, `colour`, `tile`, `blurb`),
then use its key in a family's `topic` or `tags`.

**Add a language.** The site is built for one language per build (`site.language` and each family's `language` = "EN").
For a second language, copy `catalogue.json` to `catalogue.<lang>.json`, translate the text (keep the slugs), set
`site.language` and `site.domain` (for example `https://fieldreadyqhse.com/pt`), and build it into its own folder
(`python3 src/build.py --catalogue catalogue.pt.json --out pt`). Add the new pages to the main sitemap.

The build stops with a clear message if a family has a missing field, an unknown topic or tag, or a media file that
doesn't exist.

**Removed pages.** The build overwrites pages but does not delete old ones. If you rename a slug or retire a product,
remove its old folder by hand (and keep the old URL working with a redirect page if it was ever shared).
