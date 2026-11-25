#!/usr/bin/env python3
"""Field Ready QHSE static site generator (ED02, Gumroad checkout).

One file drives every page: src/catalogue.json.  Run from anywhere:
    python3 src/build.py            # writes the site into the repo root (the folder above src/)
    python3 src/build.py --out docs # or into another folder, e.g. docs/ (GitHub Pages "/docs" option)
    python3 src/build.py --catalogue catalogue.pt.json --out pt   # a second language from its own catalogue
See src/README.md for how to add a product, a variant, an edition or a language.
No third-party packages are needed (Python 3.8+).
"""
import html, json, os, shutil, subprocess, sys
from datetime import date

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
OUT = ROOT
if '--out' in sys.argv:
    OUT = os.path.join(ROOT, sys.argv[sys.argv.index('--out') + 1])

CATFILE = 'catalogue.json'
if '--catalogue' in sys.argv:
    CATFILE = sys.argv[sys.argv.index('--catalogue') + 1]
CAT = json.load(open(os.path.join(SRC, CATFILE), encoding='utf-8'))
SITE = CAT['site']
DOMAIN = SITE['domain'].rstrip('/')
EMAIL = SITE['email']
TOPICS = {t['key']: t for t in CAT['topics']}
FAM = [f for f in CAT['families'] if f.get('status', 'live') in ('live', 'coming_soon') and not f.get('hidden')]
BYSLUG = {f['slug']: f for f in CAT['families']}
COURSES = CAT.get('courses', [])
TODAY = SITE.get('updated', date.today().isoformat())
e = html.escape
WRITTEN = []

# Pack/bundle checkout URLs come from src/gumroad_map.json. A Buy link is
# emitted only when that variant is marked published. Course products are
# not in the map and are left as they are in catalogue.json.
GUMROAD_MAP_FILE = os.path.join(SRC, 'gumroad_map.json')

def apply_gumroad_map():
    if not os.path.isfile(GUMROAD_MAP_FILE):
        return
    mp = json.load(open(GUMROAD_MAP_FILE, encoding='utf-8'))
    products = mp.get('products', {})
    for f in CAT['families']:
        entry = products.get(f.get('slug')) or {}
        for v in f.get('variants') or []:
            info = entry.get(v.get('key')) or {}
            if info.get('published') and info.get('permalink'):
                v['gumroad_url'] = f"https://fieldreadyqhse.gumroad.com/l/{info['permalink']}"

apply_gumroad_map()

# ---------------------------------------------------------------- helpers
def url_of(f):
    return f"/{TOPICS[f['topic']]['path']}/{f['slug']}/"

def topic_url(k):
    return f"/{TOPICS[k]['path']}/"

def colour(f):
    return TOPICS[f['topic']]['colour']

def live_variants(f):
    return [v for v in f['variants'] if v.get('status', f.get('status', 'live')) == 'live']

def from_price(f):
    vs = live_variants(f) if f.get('status') == 'live' else []
    if not vs:
        return None
    return min(float(v['price_ex_vat']) for v in vs)

def eur(x):
    return f"€{float(x):,.2f}".replace('.00', '') if float(x).is_integer() else f"€{float(x):,.2f}"

def in_topic(f, k):
    return f['topic'] == k or k in f.get('tags', [])

def ic(name, size=20):
    paths = {
     'check': '<path d="M20 6 9 17l-5-5"></path>',
     'dl': '<path d="M12 3v12"></path><path d="m7 10 5 5 5-5"></path><path d="M5 21h14"></path>',
     'lock': '<rect x="4" y="11" width="16" height="10" rx="2"></rect><path d="M8 11V7a4 4 0 0 1 8 0v4"></path>',
     'doc': '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path><path d="M14 3v6h6"></path><path d="M8 13h8"></path><path d="M8 17h5"></path>',
     'edit': '<path d="M12 20h9"></path><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"></path>',
     'play': '<rect x="3" y="5" width="18" height="14" rx="2"></rect><path d="m10 9 5 3-5 3z"></path>',
     'menu': '<path d="M4 7h16"></path><path d="M4 12h16"></path><path d="M4 17h16"></path>',
     'mail': '<rect x="3" y="5" width="18" height="14" rx="2"></rect><path d="m3 7 9 6 9-6"></path>',
     'down': '<path d="m6 9 6 6 6-6"></path>',
     'box': '<path d="M21 8 12 3 3 8v8l9 5 9-5z"></path><path d="m3 8 9 5 9-5"></path><path d="M12 13v8"></path>',
    }
    sw = 2.5 if name == 'check' else 2
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths[name]}</svg>'

# File-type logos (Word, Excel, PowerPoint, PDF): own drawings in the familiar colours and letters.
FLOGO = {
 'DOCX': ('#2B579A', 'W', 'Word'), 'XLSX': ('#217346', 'X', 'Excel'),
 'PPTX': ('#C43E1C', 'P', 'PowerPoint'), 'PDF': ('#D0271D', 'PDF', 'PDF'),
}
ORDER = ['DOCX', 'XLSX', 'PPTX', 'PDF']
def flogo_svg(f, s=26):
    c, letter, _ = FLOGO[f]
    fs = 8.5 if len(letter) > 1 else 14
    return (f'<svg width="{s}" height="{s}" viewBox="0 0 26 26" aria-hidden="true"><rect x="1" y="1" width="24" height="24" rx="5" fill="{c}"></rect>'
            f'<path d="M15 5h5v5" fill="none" stroke="rgba(255,255,255,.55)" stroke-width="1.6"></path>'
            f'<text x="12.2" y="{18.2 if len(letter) == 1 else 16.6}" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-weight="700" font-size="{fs}" fill="#FFFFFF">{letter}</text></svg>')
def flogos(lst, sm=False):
    lst = [f for f in ORDER if f in lst]
    if not lst:
        return ''
    out = ''.join(f'<span class="flogo">{flogo_svg(f, 22 if sm else 26)}{FLOGO[f][2]} <small>({f})</small></span>' for f in lst)
    return f'<div class="flogos{" sm" if sm else ""}" aria-label="File formats">{out}</div>'

def placeholder(f, label='Product image to come'):
    return (f'<div class="ph" style="--c:{colour(f)}" role="img" aria-label="{e(f["title"])}"><img src="/assets/logo.png" alt="" width="70" height="52">'
            f'<b>{e(f["title"])}</b><span>{e(label)}</span></div>')

# ---------------------------------------------------------------- page frame
def nav_html(current):
    topics = [t for t in CAT['topics'] if t.get('kind') == 'topic']
    menu = ''.join(f'<a href="{topic_url(t["key"])}"><i class="dot" style="--c:{t["colour"]}"></i>{e(t["name"])}</a>' for t in topics)
    menu += '<a href="/shop/"><i class="dot" style="--c:#14254A"></i>All products</a>'
    def cur(k):
        return ' aria-current="page"' if k == current else ''
    items = [f'<div class="dd"><a href="/shop/"{cur("shop")}>Shop by topic {ic("down", 16)}</a><div class="dd-menu">{menu}</div></div>',
             f'<a href="{topic_url("bundles")}"{cur("bundles")}>Bundles</a>',
             f'<a href="{topic_url("management-systems")}"{cur("management-systems")}>Management System Packs</a>']
    if SITE.get('free_sample_url'):
        items.append(f'<a href="{SITE["free_sample_url"]}"{cur("free")}>Free sample</a>')
    items += [f'<a href="/courses/"{cur("courses")}>Courses</a>',
             f'<a href="/praxterra/"{cur("praxterra")}>PRAXTERRA</a>',
             f'<a href="/about/"{cur("about")}>About</a>', f'<a href="/help/"{cur("help")}>Help</a>']
    return ''.join(items)

def page(title, desc, body, path, current='', gumroad=False, og_image=''):
    canonical = f'{DOMAIN}{path}'
    og = f'<meta property="og:image" content="{DOMAIN}{og_image}">' if og_image else ''
    gum = f'\n<script src="{SITE["gumroad_script"]}"></script>' if gumroad else ''
    topics = [t for t in CAT['topics'] if t.get('kind') == 'topic']
    shop_links = ''.join(f'<a href="{topic_url(t["key"])}">{e(t["name"])}</a>' for t in topics)
    course_links = ''.join(f'<a href="/courses/#{e(c["slug"])}">{e(c["title"])}</a>' for c in COURSES if c.get('status') == 'live')
    WRITTEN.append(path)
    return f'''<!DOCTYPE html>
<html lang="{SITE.get('language', 'en')}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical}">
{og}
<link rel="icon" type="image/png" href="/assets/favicon.png">
<link rel="preload" href="/assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/styles.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="band">{e(SITE['band'])}</div>
<header class="header">
<div class="wrap">
<a class="logo" href="/"><img src="/assets/logo.png" alt="Field Ready QHSE home" width="60" height="44"></a>
<button class="menu-btn" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="site-nav">{ic('menu', 24)}</button>
<nav class="nav" id="site-nav" aria-label="Main">{nav_html(current)}</nav>
<a class="btn btn-primary btn-sm cta-sm" href="/shop/">Shop all packs</a>
</div>
</header>
<main id="main">
{body}
</main>
<footer class="footer">
<div class="wrap">
<div style="display:flex;flex-direction:column;gap:12px;flex:1 1 260px;max-width:340px">
<a class="logo" href="/"><img src="/assets/logo.png" alt="Field Ready QHSE home" width="55" height="40"></a>
<span>{e(SITE['footer_blurb'])}</span>
<span>{e(SITE['seller'])}</span>
<a href="mailto:{EMAIL}" style="text-decoration:none;font-weight:700;color:#FFFFFF">{EMAIL}</a>
</div>
<nav aria-label="Footer">
<div><b>Shop</b>{shop_links}<a href="{topic_url('bundles')}">Bundles</a><a href="{topic_url('management-systems')}">Management System Packs</a><a href="/shop/">All products</a><a href="/courses/">Courses</a><a href="/praxterra/">PRAXTERRA</a></div>
<div><b>Help</b><a href="/help/licence/">Licence</a><a href="/help/refunds/">Refunds</a><a href="/help/faq/">FAQ</a><a href="/help/contact/">Contact</a></div>
<div><b>Legal</b><a href="/legal/terms/">Terms of sale</a><a href="/legal/privacy/">Privacy policy</a><a href="/legal/imprint/">Seller information</a></div>
<div><b>Courses</b><a href="/courses/">All courses</a>{course_links}</div>
</nav>
</div>
<div class="wrap legalline">© {SITE['year']} {e(SITE['seller'])} · Payments are processed by Gumroad, our reseller and merchant of record, which handles payment, VAT and sales tax and issues your receipt.</div>
</footer>
<script src="/assets/site.js"></script>{gum}
</body>
</html>
'''

def write(path, content):
    fp = os.path.join(OUT, path.lstrip('/'))
    if fp.endswith('/'):
        fp += 'index.html'
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    with open(fp, 'w', encoding='utf-8') as fh:
        fh.write(content)

# ---------------------------------------------------------------- blocks
def price_line(f, big=False):
    p = from_price(f)
    if f.get('status') == 'coming_soon' or p is None:
        return '<span class="price">Coming soon</span>'
    pre = 'from ' if len(live_variants(f)) > 1 else ''
    return f'<span class="price">{pre}{eur(p)} <small>+ VAT (added at checkout for your country)</small></span>'

def card(f):
    u = url_of(f)
    c = colour(f)
    if f.get('images'):
        im = f'<a href="{u}" tabindex="-1" aria-hidden="true"><img class="card-img" src="{f["images"][0]}" alt="" loading="lazy" width="600" height="600"></a>'
    else:
        im = f'<a href="{u}" tabindex="-1" aria-hidden="true">{placeholder(f)}</a>'
    tags = f'<span class="tag" style="--c:{c}">{e(TOPICS[f["topic"]]["short"])}</span>'
    if f.get('edition'):
        tags += f'<span class="tag tag-o">{e(f["edition"])}</span>'
    if len(f['variants']) > 1:
        tags += f'<span class="tag tag-o">{" / ".join(e(v["name"]) for v in f["variants"])}</span>'
    if f.get('badge'):
        tags += f'<span class="tag tag-y">{e(f["badge"])}</span>'
    return f'''<article class="card" style="--c:{c}">
{im}
<div class="card-body">
<div class="tags">{tags}</div>
<h3><a href="{u}">{e(f['title'])}</a></h3>
<p>{e(f['short'])}</p>
{flogos(f['formats'], sm=True)}
<div class="card-foot">{price_line(f)}<a class="btn btn-primary btn-sm" href="{u}">View pack</a></div>
</div>
</article>'''

def grid(fs):
    return '<div class="grid">' + ''.join(card(f) for f in fs) + '</div>'

def live_courses():
    return [c for c in COURSES if c.get('status') == 'live']

def course_card(c):
    colour = c.get('colour', '#14254A')
    tags = f'<span class="tag" style="--c:{colour}">{e(c.get("topic_label", "Course"))}</span>'
    tags += f'<span class="tag tag-o">{c["videos"]} videos · {e(c["duration"])}</span>'
    inc = ''.join(f'<li>{ic("check", 16)} <span>{e(item)}</span></li>' for item in c.get('includes', []))
    inc_html = f'<ul class="course-includes">{inc}</ul>' if inc else ''
    aud = f'<p class="course-audience">{e(c["audience"])}</p>' if c.get('audience') else ''
    price = f'<span class="price">{eur(c["price"])} <small>VAT added at checkout for your country</small></span>'
    buy = (
        f'<a class="gumroad-button btn btn-primary btn-sm" href="{e(c["gumroad_url"])}" '
        f'data-gumroad-overlay-checkout="true">Buy</a>'
    )
    return (
        f'<article class="card course-card" id="{e(c["slug"])}" style="--c:{colour}">'
        f'<div class="card-body">'
        f'<div class="tags">{tags}</div>'
        f'<h3><a href="/courses/#{e(c["slug"])}">{e(c["title"])}</a></h3>'
        f'<p>{e(c["short"])}</p>'
        f'{inc_html}'
        f'{aud}'
        f'<div class="card-foot">{price}{buy}</div>'
        f'</div>'
        f'</article>'
    )

def courses_grid(cs=None):
    cs = cs if cs is not None else live_courses()
    return '<div class="grid courses-grid">' + ''.join(course_card(c) for c in cs) + '</div>'

def courses_page():
    cs = live_courses()
    body = (
        '<section class="tband" style="--c:#14254A"><div class="wrap">'
        '<div class="crumbs"><a href="/">Home</a> / Courses</div>'
        '<h1>Courses</h1>'
        '<p>Video courses for construction site training, with the downloadable packs you need to put them into practice. Instant download after purchase.</p>'
        '</div></section>'
        '<section class="section"><div class="wrap">'
        f'{courses_grid(cs)}'
        '<p class="note" style="margin-top:32px">These courses are training resources. Completion does not establish competence, accreditation or site authorisation. Licensed for use within your own organisation.</p>'
        '</div></section>'
    )
    return page(
        'Courses | Field Ready QHSE',
        'Video courses for construction site training, with downloadable packs. Instant download.',
        body, '/courses/', 'courses', gumroad=True)

def buy_button(f, v):
    if f.get('status') != 'live' or v.get('status', 'live') != 'live':
        return '<p class="soon">Coming soon. This pack is still in final review and cannot be bought yet.</p>'
    label = f'Buy now – {eur(v["price_ex_vat"])} + VAT'
    if v.get('gumroad_url'):
        return f'<a class="gumroad-button btn btn-primary btn-lg" href="{e(v["gumroad_url"])}" data-gumroad-overlay-checkout="true">{ic("dl")} {label}</a>'
    return f'<span class="btn btn-lg btn-disabled" aria-disabled="true">{ic("dl")} Available soon</span>'

def stats_html(f):
    if not f.get('stats'):
        return ''
    return '<div class="stats">' + ''.join(f'<div class="stat"><b>{e(str(n))}</b><span>{e(l)}</span></div>' for n, l in f['stats'][:3]) + '</div>'

def containing_bundles(f):
    out = [BYSLUG[s] for s in f.get('bundles', []) if s in BYSLUG and BYSLUG[s] in FAM]
    out += [b for b in FAM if f['slug'] in b.get('contains', []) and b not in out]
    return out

# ---------------------------------------------------------------- pages
def product_page(f):
    u = url_of(f)
    c = colour(f)
    t = TOPICS[f['topic']]
    vs = f['variants']
    gum = any(v.get('gumroad_url') for v in vs) and f.get('status') == 'live'
    # gallery
    imgs = f.get('images', [])
    if imgs:
        alt0 = f'{f["title"]}: image 1'
        gal = f'<img class="main" src="{imgs[0]}" alt="{e(alt0)}" width="900" height="900">'
        if len(imgs) > 1:
            gal += '<div class="thumbs">' + ''.join(
                f'<button type="button" aria-pressed="{"true" if i == 0 else "false"}" aria-label="Show image {i + 1}" data-src="{k}" data-alt="{e(f["title"])}: image {i + 1}"><img src="{k}" alt="" loading="lazy" width="140" height="140"></button>'
                for i, k in enumerate(imgs)) + '</div>'
    else:
        gal = placeholder(f, 'Product images to come')
    if f.get('video'):
        gal += f'<p class="vlabel">15-second look inside</p><video src="{f["video"]}" controls muted playsinline preload="metadata"{f" poster={chr(34)}{imgs[0]}{chr(34)}" if imgs else ""}></video>'
    # badges
    badges = f'<span class="badge">{e(t["name"])}</span>'
    if f.get('edition'):
        badges += f'<span class="badge badge-y">{e(f["edition"])}</span>'
    badges += f'<span class="badge">{e(f.get("language", "EN"))}</span>'
    if f.get('badge'):
        badges += f'<span class="badge badge-y">{e(f["badge"])}</span>'
    # variants
    if len(vs) > 1:
        opts = ''.join(f'<label class="vopt"><input type="radio" name="variant" value="{e(v["key"])}"{" checked" if i == len(vs) - 1 else ""}><b>{e(v["name"])}</b><span>{eur(v["price_ex_vat"])} + VAT</span></label>'
                       for i, v in enumerate(vs))
        selector = f'<fieldset class="variants"><legend>Choose your edition</legend>{opts}</fieldset>'
    else:
        selector = ''
    panels = ''
    for i, v in enumerate(vs):
        extra = ''
        if v.get('includes'):
            head = v.get('includes_heading') or f'{v["name"]} includes'
            extra = f'<div class="box box-tint"><h3>{e(head)}</h3><ul class="checks">' + ''.join(f'<li>{ic("check", 18)}{e(x)}</li>' for x in v['includes']) + '</ul></div>'
        price = (f'<div class="row" style="align-items:baseline"><span class="price">{eur(v["price_ex_vat"])}</span><span class="vat">+ VAT (added at checkout for your country)</span></div>'
                 if f.get('status') == 'live' else '')
        name = f'<h3>{e(v["name"])}</h3>' if len(vs) > 1 else ''
        panels += f'<div class="vpanel" data-variant="{e(v["key"])}">{name}{price}{buy_button(f, v)}{extra}</div>'
    inc = ''.join(f'<li>{ic("check", 18)}{e(x)}</li>' for x in f['includes'])
    inc_head = 'What\'s inside (every edition)' if len(vs) > 1 else 'What\'s inside'
    note = f'<p class="note">{e(f["note"])}</p>' if f.get('note') else ''
    upgrade = f'<p class="note"><b>Upgrade note:</b> {e(f["upgrade_note"])}</p>' if f.get('upgrade_note') else ''
    # related
    bundles = containing_bundles(f)
    rel = [x for x in FAM if x is not f and x not in bundles and (in_topic(x, f['topic']) or set(x.get('tags', [])) & set(f.get('tags', [])))]
    rel = sorted(rel, key=lambda x: (x['topic'] != f['topic'], x.get('order', 99)))[:3]
    bund_html = ''
    if bundles:
        bund_html = f'<section class="section" aria-labelledby="bund-h"><div class="wrap"><h2 id="bund-h" style="font-size:26px;margin-bottom:20px">Save with the bundle</h2>{grid(bundles)}</div></section>'
    inside = ''
    if f.get('contains'):
        inside = '<div class="box"><h2>Packs in this bundle</h2><ul class="checks">' + ''.join(
            f'<li>{ic("box", 18)}<a href="{url_of(BYSLUG[s])}">{e(BYSLUG[s]["title"])}</a></li>' for s in f['contains'] if s in BYSLUG) + '</ul></div>'
    body = f'''
<section class="phero" style="--c:{c}">
<div class="wrap">
<div class="crumbs"><a href="/">Home</a> / <a href="{topic_url(f['topic'])}">{e(t['name'])}</a> / {e(f['title'])}</div>
<div class="badges">{badges}</div>
<h1>{e(f['title'])}</h1>
<p class="who">For {e(SITE['who_for'])}.</p>
{stats_html(f)}
{flogos(f['formats'])}
</div>
</section>
<div class="wrap">
<div class="pdp" id="buy" style="--c:{c}">
<div class="gallery">{gal}</div>
<div class="buy">
<p class="intro">{e(f['intro'])}</p>
{selector}
{panels}
<p class="note">Instant digital download. By buying you agree to our <a href="/legal/terms/">terms of sale</a> and <a href="/help/licence/">licence</a>, and ask for the download to start straight away. {e(SITE['refund_line'])} <a href="/help/refunds/">Refund policy</a>.</p>
<div class="box"><h2>{inc_head}</h2><ul class="checks">{inc}</ul>{flogos(f['formats'], sm=True)}{note}{upgrade}</div>
{inside}
<details><summary>Licence</summary><p>{e(SITE['licence_summary'])} <a href="/help/licence/">Full licence</a>.</p></details>
<details><summary>Delivery and payment</summary><p>Checkout is handled by Gumroad, our reseller and merchant of record. Gumroad adds the VAT or sales tax for your country, takes the payment and emails your receipt and download link.</p></details>
<details><summary>Important</summary><p>These are editable templates. A competent person must check them against your site, your people and the law where you work before use.</p></details>
</div>
</div>
</div>
{bund_html}
<section class="section section-alt" aria-labelledby="rel-h">
<div class="wrap"><h2 id="rel-h" style="font-size:26px;margin-bottom:20px">Related packs</h2>{grid(rel)}</div>
</section>
'''
    return page(f'{f["title"]} | Field Ready QHSE', f['short'], body, u, '', gum, imgs[0] if imgs else '')

def topic_page(k):
    t = TOPICS[k]
    fs = sorted([f for f in FAM if in_topic(f, k)], key=lambda x: x.get('order', 99))
    extra = ''
    if k == 'toolbox-talks':
        cs = live_courses()
        if cs:
            extra = ('<div class="group" style="margin-top:48px"><div class="group-head"><div><h3>Video courses</h3><p>Video lessons plus the downloadable packs to use on site.</p></div>'
                     '<a class="btn btn-outline btn-sm" href="/courses/">All courses</a></div>' +
                     courses_grid(cs) + '</div>')
    body = f'''
<section class="tband" style="--c:{t['colour']}"><div class="wrap">
<div class="crumbs"><a href="/">Home</a> / {e(t['name'])}</div>
<h1>{e(t['name'])}</h1><p>{e(t['blurb'])}</p></div></section>
<section class="section"><div class="wrap">
<div class="group-head" style="--c:{t['colour']};margin-bottom:22px"><div><h3>{len(fs)} pack{'s' if len(fs) != 1 else ''}</h3></div></div>
{grid(fs)}
{extra}
</div></section>'''
    gum = (k == 'toolbox-talks' and any(c.get('gumroad_url') for c in live_courses()))
    return page(f'{t["name"]} | Field Ready QHSE', t['blurb'], body, topic_url(k), k, gum)

def shop_page():
    groups = ''
    for t in [t for t in CAT['topics'] if t.get('kind') == 'topic']:
        fs = sorted([f for f in FAM if f['topic'] == t['key']], key=lambda x: x.get('order', 99))
        if not fs:
            continue
        groups += f'<div class="group" id="{t["key"]}" style="--c:{t["colour"]}"><div class="group-head"><div><h3>{e(t["name"])}</h3><p>{e(t["blurb"])}</p></div><a class="btn btn-outline btn-sm" href="{topic_url(t["key"])}">All {e(t["name"])} packs</a></div>{grid(fs)}</div>'
    body = f'''
<section class="tband" style="--c:#14254A"><div class="wrap"><div class="crumbs"><a href="/">Home</a> / All products</div>
<h1>All products</h1><p>{len(FAM)} editable QHSE packs for construction, sorted by topic. Each pack is listed once, under its main topic.</p></div></section>
<section class="section"><div class="wrap">{groups}</div></section>'''
    return page('All products | Field Ready QHSE', 'Every Field Ready QHSE pack, by topic.', body, '/shop/', 'shop')

def home_page():
    px_home = ''
    hb = os.path.join(SRC, 'praxterra', 'home_block.html')
    if os.path.isfile(hb):
        px_home = open(hb, encoding='utf-8').read()
    topics = [t for t in CAT['topics'] if t.get('kind') == 'topic']
    tiles = ''.join(f'<a class="tile" style="--c:{t["colour"]}" href="{topic_url(t["key"])}"><b>{e(t["name"])}</b><span>{e(t["tile"])}</span><em>{sum(1 for f in FAM if in_topic(f, t["key"]))} packs →</em></a>' for t in topics)
    ms = sorted([f for f in FAM if in_topic(f, 'management-systems')], key=lambda x: x.get('order', 99))
    bd = sorted([f for f in FAM if in_topic(f, 'bundles')], key=lambda x: x.get('order', 99))
    courses = courses_grid()
    hero_img = SITE.get('home_image')
    himg = f'<div class="hero-img"><img src="{hero_img}" alt="{e(SITE.get("home_image_alt", ""))}" width="900" height="900"></div>' if hero_img else ''
    body = f'''
<section class="hero">
<div class="wrap">
<div class="hero-text">
<span class="eyebrow">Construction QHSE documents</span>
<h1>Field-ready QHSE packs.<br>Edit, brand, deliver.</h1>
<p>{e(SITE['home_lead'])}</p>
<div class="row"><a class="btn btn-primary" href="/shop/">Browse all packs</a><a class="btn btn-ghost" href="{topic_url('management-systems')}">Management System Packs</a></div>
{flogos(['DOCX', 'XLSX', 'PPTX', 'PDF'])}
</div>
{himg}
</div>
</section>
<section class="trust" aria-label="Why buy here">
<div class="wrap">
<div class="trust-item">{ic('dl')}<div><strong>Instant download</strong><span>Your files are ready straight after payment.</span></div></div>
<div class="trust-item">{ic('edit')}<div><strong>Fully editable</strong><span>Add your logo, site details and procedures.</span></div></div>
<div class="trust-item">{ic('doc')}<div><strong>VAT handled at checkout</strong><span>Gumroad adds the tax for your country and emails your receipt.</span></div></div>
<div class="trust-item">{ic('lock')}<div><strong>Secure checkout</strong><span>Card and wallet payments through Gumroad.</span></div></div>
</div>
</section>
<section class="section" aria-labelledby="disc-h"><div class="wrap">
<h2 id="disc-h" style="margin-bottom:24px">Shop by topic</h2>
<div class="tiles">{tiles}</div>
</div></section>
<section class="section section-alt" aria-labelledby="ms-h"><div class="wrap">
<div class="section-head"><div><h2 id="ms-h">Management System Packs</h2><p class="lead">ISO 9001, ISO 45001 and ISO 14001 systems and transition packs.</p></div><a class="btn btn-outline btn-sm" href="{topic_url('management-systems')}">See all</a></div>
{grid(ms)}
</div></section>
<section class="section" aria-labelledby="bd-h"><div class="wrap">
<div class="section-head"><div><h2 id="bd-h">Bundles</h2><p class="lead">Several packs in one download, for less than buying them one by one.</p></div><a class="btn btn-outline btn-sm" href="{topic_url('bundles')}">See all</a></div>
{grid(bd)}
</div></section>
{px_home}
<section class="section section-alt" aria-labelledby="how-h"><div class="wrap">
<h2 id="how-h" style="margin-bottom:28px">How it works</h2>
<div class="steps">
<div class="step"><b>01</b><strong>Choose your pack</strong><span>See what's inside every pack before you buy.</span></div>
<div class="step"><b>02</b><strong>Pay securely</strong><span>Gumroad adds the VAT or sales tax for your country and emails your receipt.</span></div>
<div class="step"><b>03</b><strong>Download and brand</strong><span>Add your logo and site details, then use it on site.</span></div>
</div>
</div></section>
<section class="section" aria-labelledby="courses-h"><div class="wrap">
<div class="section-head"><div><h2 id="courses-h">Courses</h2>
<p class="lead">Learn to deliver inductions and toolbox talks with confidence. Each course includes the video lessons and a downloadable pack.</p></div>
<a class="btn btn-outline btn-sm" href="/courses/">All courses</a></div>
{courses}
<p class="note" style="margin-top:24px">These courses are training resources. Completion does not establish competence, accreditation or site authorisation.</p>
</div></section>
'''
    return page('Field Ready QHSE — Editable QHSE documents for construction', SITE['home_desc'], body, '/', 'home', gumroad=True)

def text_page(path, title, inner, current='', desc=''):
    return page(f'{title} | Field Ready QHSE', desc or f'{title} – Field Ready QHSE.', f'<article class="legal"><h1>{e(title)}</h1>{inner}</article>', path, current)

def free_page():
    # No free sample product exists yet. This page exists so older /free links
    # (emails, videos) land on a working page instead of a 404. It does not
    # offer a free download.
    inner = (
        '<p>A free sample pack is not available on this site at the moment.</p>'
        '<p>You can browse our toolbox talks and other packs in the shop. Nothing is given away from this page.</p>'
        '<p><a class="btn btn-primary btn-sm" href="/toolbox-talks/">Toolbox talks</a> '
        '<a class="btn btn-outline btn-sm" href="/shop/">All products</a></p>'
    )
    return text_page('/free/', 'Free sample', inner, '', 'A free sample pack is not available at the moment. Browse toolbox talks and other packs in the shop.')

# ---------------------------------------------------------------- static text pages (from catalogue.json "pages")
def build_text_pages():
    for p in CAT['pages']:
        inner = p['html'].replace('{EMAIL}', EMAIL).replace('{SELLER}', e(SITE['seller'])).replace('{LOCATION}', e(SITE['location'])).replace('{UPDATED}', e(SITE['legal_updated']))
        if p['path'] == '/help/':
            inner += '<div class="helpgrid">' + ''.join(f'<a href="{h}"><b>{e(n)}</b><span>{e(d)}</span></a>' for h, n, d in [
                ('/help/licence/', 'Licence', 'What you can and can’t do with the files'),
                ('/help/refunds/', 'Refunds', 'Faulty or missing files, and how to report a problem'),
                ('/help/faq/', 'FAQ', 'Software, formats, payment and delivery'),
                ('/help/contact/', 'Contact', EMAIL)]) + '</div>'
        write(p['path'], text_page(p['path'], p['title'], inner, p.get('current', ''), p.get('desc', '')))

def notfound():
    body = '<article class="legal"><h1>Page not found</h1><p>That page doesn’t exist or has moved. <a href="/">Go to the homepage</a> or <a href="/shop/">browse all products</a>.</p></article>'
    html_ = page('Page not found | Field Ready QHSE', 'Page not found.', body, '/404.html')
    WRITTEN.remove('/404.html')
    return html_

# ---------------------------------------------------------------- assets
def copy_assets():
    dst = os.path.join(OUT, 'assets')
    os.makedirs(dst, exist_ok=True)
    for root, _, files in os.walk(os.path.join(SRC, 'assets')):
        for fn in files:
            s = os.path.join(root, fn)
            d = os.path.join(dst, os.path.relpath(s, os.path.join(SRC, 'assets')))
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)
    # product media: src/media/<slug>/... -> /assets/media/<slug>/...
    msrc = os.path.join(SRC, 'media')
    if os.path.isdir(msrc):
        for root, _, files in os.walk(msrc):
            for fn in files:
                s = os.path.join(root, fn)
                d = os.path.join(dst, 'media', os.path.relpath(s, msrc))
                os.makedirs(os.path.dirname(d), exist_ok=True)
                if not os.path.exists(d) or os.path.getmtime(d) < os.path.getmtime(s):
                    shutil.copy2(s, d)

def check_catalogue():
    errs = []
    for f in CAT['families']:
        for k in ('slug', 'topic', 'title', 'short', 'intro', 'includes', 'formats', 'variants', 'status'):
            if k not in f:
                errs.append(f'{f.get("slug")}: missing {k}')
        if f.get('topic') not in TOPICS:
            errs.append(f'{f["slug"]}: unknown topic {f.get("topic")}')
        for t in f.get('tags', []):
            if t not in TOPICS:
                errs.append(f'{f["slug"]}: unknown tag {t}')
        for im in f.get('images', []) + ([f['video']] if f.get('video') else []):
            if not os.path.exists(os.path.join(SRC, im.replace('/assets/media/', 'media/').lstrip('/'))):
                errs.append(f'{f["slug"]}: media file not found {im}')
        for v in f.get('variants', []):
            if 'key' not in v or 'price_ex_vat' not in v:
                errs.append(f'{f["slug"]}: variant needs key and price_ex_vat')
    if errs:
        print('CATALOGUE ERRORS:\n  ' + '\n  '.join(errs))
        sys.exit(1)

# ---------------------------------------------------------------- main
def main():
    check_catalogue()
    copy_assets()
    write('/', home_page())
    write('/shop/', shop_page())
    write('/courses/', courses_page())
    for t in CAT['topics']:
        write(topic_url(t['key']), topic_page(t['key']))
    for f in FAM:
        write(url_of(f), product_page(f))
    build_text_pages()
    write('/free/', free_page())
    write('/404.html', notfound())
    px = os.path.join(SRC, 'praxterra', 'build_praxterra.py')
    if os.path.isfile(px):
        subprocess.check_call([sys.executable, px, '--site-root', OUT])
        for u in ['/praxterra/', '/praxterra/self-assessment-tool/', '/praxterra/records-pack/',
                  '/praxterra/starter-kit/', '/praxterra/professional-toolkit/', '/praxterra/licence/']:
            if u not in WRITTEN:
                WRITTEN.append(u)
    with open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8') as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                 ''.join(f'<url><loc>{DOMAIN}{u}</loc><lastmod>{TODAY}</lastmod></url>\n' for u in WRITTEN) + '</urlset>\n')
    with open(os.path.join(OUT, 'robots.txt'), 'w') as fh:
        fh.write(f'User-agent: *\nAllow: /\nDisallow: /src/\nSitemap: {DOMAIN}/sitemap.xml\n')
    with open(os.path.join(OUT, 'CNAME'), 'w') as fh:
        fh.write(DOMAIN.split('://', 1)[1] + '\n')
    open(os.path.join(OUT, '.nojekyll'), 'w').close()
    print(f'built {len(FAM)} product pages, {len(WRITTEN)} pages in total -> {OUT}')

if __name__ == '__main__':
    main()
