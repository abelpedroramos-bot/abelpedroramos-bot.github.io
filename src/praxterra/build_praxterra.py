#!/usr/bin/env python3
"""PRAXTERRA section for fieldreadyqhse.com.

Writes a self-contained /praxterra/ folder (section page, four product pages,
licence page, CSS, fonts, images) into the site root, plus a homepage block.

    python3 build_praxterra.py --site-root ../repo            # real build
    python3 build_praxterra.py --site-root ../preview --preview

Buy buttons: fill "gumroad_url" in praxterra_catalogue.json
(e.g. https://fieldreadyqhse.gumroad.com/l/praxterra-self-assessment-tool).
Empty -> disabled "Available soon" button and no Gumroad script on the page.
Filled -> Gumroad overlay checkout; gumroad.js loads on that page only.
"""
import argparse, html, json, os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
DOMAIN = 'https://fieldreadyqhse.com'
# Links into the main Field Ready site, relative to the site root.
# Check these against the current generator when merging (link checker).
FRQ_LINKS = {
    'home': '',
    'packs': 'shop/',
    'contact': 'help/contact/',
    'terms': 'legal/terms/',
    'refund': 'help/refunds/',
    'privacy': 'legal/privacy/',
}
e = html.escape

ap = argparse.ArgumentParser()
ap.add_argument('--site-root', required=True)
ap.add_argument('--preview', action='store_true')
A = ap.parse_args()
CAT = json.load(open(os.path.join(HERE, 'praxterra_catalogue.json'), encoding='utf-8'))
SEC = CAT['section']
P = sorted(CAT['products'], key=lambda p: p['order'])
BASE = SEC['path']
OUT = os.path.join(A.site_root, BASE)


def eur(x):
    return '€' + (x[:-3] if x.endswith('.00') else x)


def ico(name, size=18):
    d = {
        'check': '<path d="M20 6 9 17l-5-5"/>',
        'dl': '<path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/>',
        'leaf': '<path d="M5 19c8 0 14-6 14-14-8 0-14 6-14 14z"/><path d="M5 19 13 11"/>',
        'lock': '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
        'doc': '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/>',
        'menu': '<path d="M4 7h16"/><path d="M4 12h16"/><path d="M4 17h16"/>',
        'dash': '<path d="M6 12h12"/>',
    }[name]
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{d}</svg>')


# Generic software symbols (no third-party logos): spreadsheet grid, text document, PDF page.
FMT = {
    'XLSX': ('#1E7B45', 'Excel workbook', '<rect x="3" y="3" width="18" height="18" rx="2.5" fill="#1E7B45"/>'
             '<path d="M7 8h10M7 12h10M7 16h10M12 8v8" stroke="#fff" stroke-width="1.6"/>'),
    'DOCX': ('#2B5797', 'Word document', '<rect x="3" y="3" width="18" height="18" rx="2.5" fill="#2B5797"/>'
             '<path d="M7 8h10M7 11.5h10M7 15h6" stroke="#fff" stroke-width="1.6" stroke-linecap="round"/>'),
    'PDF': ('#B3261E', 'PDF document', '<rect x="3" y="3" width="18" height="18" rx="2.5" fill="#B3261E"/>'
            '<path d="M8 17V7h4a3 3 0 0 1 0 6H8" stroke="#fff" stroke-width="1.8" fill="none"/>'),
}


def fmts(lst):
    return ('<ul class="px-formats" aria-label="File formats">' + ''.join(
        f'<li title="{FMT[f][1]}"><svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true">{FMT[f][2]}</svg>{f}</li>'
        for f in lst) + '</ul>')


DISCLOSURE = [
    'Digital product. Nothing physical is shipped.',
    'Licence for one organisation and all its own sites. Using the files with client organisations needs a separate licence, which is not yet available.',
    f'{SEC["standard_name"]} is a voluntary standard, written and published independently. It is not issued or endorsed by a standards body and it is not accredited.',
    "Results are self-assessments based on the organisation's own responses and evidence. No independent third-party verification is performed, and results are not evidence of legal compliance.",
    'Do not use results on product labels or in consumer advertising.',
    'The standard stays free to read and use at praxterra.com. Buying a tool never earns points or a level.',
]


def disclosure_html():
    return ('<div class="px-note"><h2>Please note</h2><ul>' +
            ''.join(f'<li>{e(x)}</li>' for x in DISCLOSURE) + '</ul></div>')


ANY_GUMROAD = any(p['gumroad_url'] for p in P)
LEGALLINE = ('Checkout by Gumroad, merchant of record, which charges any VAT or sales tax and issues your receipt and invoice.' if ANY_GUMROAD
             else 'Purchases are completed on Etsy, which handles payment, VAT and your receipt.')


def page(title, desc, body, depth, canonical, gumroad=False):
    r = '../' * depth            # to site root
    s = '../' * (depth - 1)      # to /praxterra/
    ribbon = ('<div class="px-ribbon">PREVIEW for Abel\'s approval. Not published. '
              'Buy buttons connect once the Gumroad product URLs are added.</div>') if A.preview else ''
    gjs = '<script src="https://gumroad.com/js/gumroad.js"></script>' if gumroad else ''
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{DOMAIN}/{canonical}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<link rel="icon" type="image/png" href="{r}assets/favicon.png">
<link rel="stylesheet" href="{s}assets/praxterra.css">
{gjs}
</head>
<body class="px-body">
<a class="px-skip" href="#main">Skip to content</a>
{ribbon}
<header class="px-header">
<div class="px-wrap">
<a class="px-logo" href="{r}{FRQ_LINKS['home'] or './'}"><img src="{r}assets/logo.png" alt="Field Ready QHSE home" width="60" height="44"></a>
<nav class="px-nav" aria-label="Main">
<a href="{r}{FRQ_LINKS['packs']}">All packs</a>
<a href="{s}" aria-current="page">PRAXTERRA tools</a>
<a href="{r}{FRQ_LINKS['contact']}">Contact</a>
</nav>
</div>
</header>
<main id="main">
{body}
</main>
<footer class="px-footer">
<div class="px-wrap">
<div class="px-foot-brand"><img src="{s}assets/img/wordmark.png" alt="PRAXTERRA" width="208" height="26"><span>PRAXTERRA tools are sold through the Field Ready QHSE shop. The standard is free at <a href="https://praxterra.com">praxterra.com</a>.</span></div>
<nav aria-label="Footer">
<a href="{s}licence/">PRAXTERRA licence</a>
<a href="{r}{FRQ_LINKS['terms']}">Terms of sale</a>
<a href="{r}{FRQ_LINKS['refund']}">Refund policy</a>
<a href="{r}{FRQ_LINKS['privacy']}">Privacy policy</a>
<a href="mailto:{SEC['contact_email']}">{SEC['contact_email']}</a>
</nav>
</div>
<div class="px-wrap px-legalline">© 2026 Field Ready QHSE · {LEGALLINE}</div>
</footer>
</body>
</html>
'''


def mode(p):
    return 'gumroad' if p['gumroad_url'] else ('etsy' if p.get('etsy_listing') else 'none')


def buy_button(p, big=True):
    label = f'Buy now – {eur(p["price_eur_ex_vat"])} + VAT'
    cls = 'px-btn px-btn-buy' + (' px-btn-lg' if big else '')
    if mode(p) == 'etsy':
        return f'<a class="{cls}" href="https://www.etsy.com/listing/{p["etsy_listing"]}">{ico("dl")} Buy on Etsy – {eur(p["price_eur_ex_vat"])} + VAT</a>'
    if p['gumroad_url']:
        return f'<a class="{cls} gumroad-button" href="{e(p["gumroad_url"])}" data-gumroad-overlay-checkout="true">{ico("dl")} {label}</a>'
    if A.preview:
        return f'<span class="{cls}" role="link" aria-disabled="true">{ico("dl")} {label}</span>'
    return f'<span class="{cls} px-btn-off" aria-disabled="true">Available soon</span>'


def checkout_note(p, s):
    if mode(p) == 'etsy':
        return (f'<p class="px-small">You complete the purchase on Etsy, which handles payment, VAT and your receipt, and delivers the download. The <a href="{s}licence/">PRAXTERRA licence</a> applies to the files.</p>'
                f'<div class="px-assure"><span>{ico("lock")} Secure checkout on Etsy</span><span>{ico("doc")} Instant download after payment</span></div>')
    return (f'<p class="px-small">Instant download (one ZIP file). By buying you accept the <a href="{s}licence/">PRAXTERRA licence</a>, our <a href="../../{FRQ_LINKS["terms"]}">terms of sale</a> and <a href="../../{FRQ_LINKS["refund"]}">refund policy</a>.</p>'
            f'<div class="px-assure"><span>{ico("lock")} Secure checkout by Gumroad</span><span>{ico("doc")} Receipt and invoice by email</span></div>')


def card(p, s):
    url = f'{s}{p["slug"]}/'
    badge = f'<span class="px-badge">{e(p["badge"])}</span>' if p.get('badge') else ''
    return f'''<article class="px-card">
<a href="{url}" tabindex="-1" aria-hidden="true" class="px-card-img"><img src="{s}assets/img/{p['slug']}-1.jpg" alt="" loading="lazy" width="800" height="600"></a>
<div class="px-card-body">
{badge}
<h3><a href="{url}">{e(p['name'])}</a></h3>
<p>{e(p['card'])}</p>
<div class="px-card-foot"><span class="px-price">{eur(p['price_eur_ex_vat'])}<small> + VAT</small></span><a class="px-btn px-btn-sm" href="{url}">View tool</a></div>
</div>
</article>'''


def compare_table(s):
    head = ''.join(f'<th scope="col"><a href="{s}{p["slug"]}/">{e(p["short_name"])}</a><span>{eur(p["price_eur_ex_vat"])} + VAT</span></th>' for p in P)
    rows = ''
    for label, marks in CAT['compare']:
        cells = ''.join(f'<td>{ico("check", 20) if m else ico("dash", 16)}<span class="px-sr">{"Included" if m else "Not included"}</span></td>' for m in marks)
        rows += f'<tr><th scope="row">{e(label)}</th>{cells}</tr>'
    return f'<div class="px-table-wrap"><table class="px-compare"><thead><tr><th scope="col">What is in the download</th>{head}</tr></thead><tbody>{rows}</tbody></table></div>'


def section_page():
    s = ''
    cards = ''.join(card(p, s) for p in P)
    body = f'''
<section class="px-hero">
<div class="px-wrap px-hero-in">
<div>
<img class="px-wordmark" src="assets/img/wordmark.png" alt="PRAXTERRA" width="312" height="39">
<h1>Sustainability tools for the PRAXTERRA standard</h1>
<p class="px-lead">Excel tools, records and training material that make the PRAXTERRA sustainability management standard easier to apply. The standard itself is free, and buying a tool never earns points or a level.</p>
<div class="px-row"><a class="px-btn" href="#tools">See the four tools</a><a class="px-btn px-btn-ghost" href="{SEC['standard_url']}">Read the free standard</a></div>
</div>
<img class="px-hero-img" src="assets/img/how-it-works.jpg" alt="How PRAXTERRA works: read the free standard, self-assess with the tool, run it with the records" width="800" height="600">
</div>
</section>
<section class="px-section" id="tools">
<div class="px-wrap">
<h2>Choose your tool</h2>
<p class="px-sub">Instant download. One licence covers one organisation and all its own sites.</p>
<div class="px-grid">{cards}</div>
</div>
</section>
<section class="px-section px-alt" aria-labelledby="cmp-h">
<div class="px-wrap">
<h2 id="cmp-h">Compare the tools</h2>
{compare_table(s)}
<p class="px-small">Prices exclude VAT. {'Gumroad adds VAT or sales tax at checkout for your country.' if ANY_GUMROAD else 'Purchases are completed on Etsy, which shows the total including VAT for your country.'}</p>
</div>
</section>
<section class="px-section">
<div class="px-wrap px-narrow">
<h2>The standard is free</h2>
<p>{e(SEC['standard_name'])} is free to read and use. Download it from <a href="{SEC['standard_url']}">praxterra.com</a>. A copy is also included in every tool download. The tools only save time: they never add requirements and never influence a result.</p>
{disclosure_html()}
</div>
</section>'''
    return page('PRAXTERRA sustainability tools | Field Ready QHSE',
                'Optional Excel tools, records and training material for the free PRAXTERRA sustainability management standard. Instant download.',
                body, 1, f'{BASE}/')


def product_page(p):
    s = '../'
    imgs = [f'{p["slug"]}-1.jpg', f'{p["slug"]}-2.jpg', 'how-it-works.jpg']
    alts = p['alts'] + ['How PRAXTERRA works: read the free standard, self-assess with the tool, run it with the records']
    main = f'<img class="px-main" src="{s}assets/img/{imgs[0]}" alt="{e(alts[0])}" width="800" height="600">'
    thumbs = '<div class="px-thumbs">' + ''.join(
        f'<button type="button" aria-pressed="{"true" if i == 0 else "false"}" aria-label="Show image {i+1}" data-src="{s}assets/img/{k}" data-alt="{e(alts[i])}"><img src="{s}assets/img/{k}" alt=""></button>'
        for i, k in enumerate(imgs)) + '</div>'
    does = ''.join(f'<li>{ico("check")}{e(x)}</li>' for x in p['does'])
    does_note = f'<p class="px-small">{e(p["does_note"])}</p>' if p.get('does_note') else ''
    inc = ''.join(f'<li>{ico("check")}{e(x)}</li>' for x in p['includes'])
    upsell = ''
    if p.get('upsell'):
        tgt = 'starter-kit' if p['slug'] in ('self-assessment-tool', 'records-pack') else 'professional-toolkit'
        upsell = f'<p class="px-upsell">{e(p["upsell"])} <a href="{s}{tgt}/">See it</a></p>'
    others = ''.join(card(x, s) for x in P if x['slug'] != p['slug'])
    badge = f'<span class="px-badge">{e(p["badge"])}</span>' if p.get('badge') else ''
    body = f'''
<div class="px-wrap">
<div class="px-crumbs"><a href="../../{FRQ_LINKS['home']}">Home</a> / <a href="{s}">PRAXTERRA tools</a> / {e(p['short_name'])}</div>
<div class="px-pdp">
<div class="px-gallery">{main}{thumbs}</div>
<div class="px-buy">
<img class="px-wordmark-sm" src="{s}assets/img/wordmark.png" alt="PRAXTERRA" width="160" height="20">
{badge}
<h1>{e(p['name'])}</h1>
<p class="px-intro">{e(p['intro'])}</p>
<div class="px-pricerow"><span class="px-price px-price-lg">{eur(p['price_eur_ex_vat'])}<small> + VAT</small></span><span class="px-vat">{'Etsy shows the total including VAT for your country.' if mode(p) == 'etsy' else 'VAT or sales tax is added at checkout for your country.'}</span></div>
{buy_button(p)}
{checkout_note(p, s)}
<div class="px-box"><h2>{e(p['does_title'])}</h2><ul class="px-checks">{does}</ul>{does_note}</div>
<div class="px-box"><h2>What's in the download</h2><ul class="px-checks">{inc}</ul>{fmts(p['formats'])}</div>
<div class="px-box"><h2>Good for</h2><p>{e(p['good_for'])}</p></div>
<div class="px-box"><h2>Software</h2><p>Built and tested in LibreOffice. The workbooks use standard formulas only and no macros, so they should work in Microsoft Excel desktop. Check them in your own software before you rely on them.</p></div>
{upsell}
{disclosure_html()}
<p class="px-small">Free standard: the PRAXTERRA standard is free to read and use at <a href="{SEC['standard_url']}">praxterra.com</a>, and a copy is included in this download. This page is for the optional tool that makes it easier to apply. Questions about the tools: <a href="mailto:{SEC['contact_email']}">{SEC['contact_email']}</a>.</p>
</div>
</div>
</div>
<section class="px-section px-alt" aria-labelledby="oth-h">
<div class="px-wrap"><h2 id="oth-h">Other PRAXTERRA tools</h2><div class="px-grid px-grid-3">{others}</div></div>
</section>
<script>
(function(){{var m=document.querySelector('.px-main');document.querySelectorAll('.px-thumbs button').forEach(function(b){{b.addEventListener('click',function(){{m.src=b.getAttribute('data-src');m.alt=b.getAttribute('data-alt');document.querySelectorAll('.px-thumbs button').forEach(function(o){{o.setAttribute('aria-pressed','false')}});b.setAttribute('aria-pressed','true')}})}})}})();
</script>'''
    return page(f'{p["name"]} | PRAXTERRA tools | Field Ready QHSE', p['card'], body, 2,
                f'{BASE}/{p["slug"]}/', gumroad=bool(p['gumroad_url']))


def licence_page():
    txt = open(os.path.join(HERE, 'LICENCE_web.txt'), encoding='utf-8').read().strip().split('\n')
    out, para = [], []
    def flush():
        if para:
            out.append('<p>' + e(' '.join(x.strip() for x in para)) + '</p>'); para.clear()
    for line in txt[2:]:
        st = line.strip()
        if not st:
            flush(); continue
        if st[:2] in [f'{i}.' for i in range(1, 10)]:
            flush(); out.append(f'<h2>{e(st)}</h2>'); continue
        if st.startswith('- '):
            flush(); out.append(f'<p class="px-li">• {e(st[2:])}</p>'); continue
        para.append(line)
    flush()
    body = (f'<div class="px-wrap px-narrow px-legal"><div class="px-crumbs"><a href="../../{FRQ_LINKS["home"]}">Home</a> / <a href="../">PRAXTERRA tools</a> / Licence</div>'
            f'<h1>PRAXTERRA toolkit licence terms</h1><p class="px-small">{e(txt[0])}. A copy is included in every download (LICENCE.txt).</p>'
            + ''.join(out) + '</div>')
    return page('PRAXTERRA toolkit licence | Field Ready QHSE', 'Licence terms for the paid PRAXTERRA tools.', body, 2, f'{BASE}/licence/')


def home_block():
    s = f'{BASE}/'
    mini = ''.join(f'<a class="px-mini" href="{s}{p["slug"]}/"><img src="{s}assets/img/{p["slug"]}-1.jpg" alt="" loading="lazy" width="400" height="300"><b>{e(p["short_name"])}</b><span>{eur(p["price_eur_ex_vat"])} + VAT</span></a>' for p in P)
    return f'''<!-- PRAXTERRA block for the homepage: paste after the last product group. Needs praxterra/assets/praxterra.css -->
<link rel="stylesheet" href="{s}assets/praxterra.css">
<section class="px-homeblock" id="praxterra" aria-labelledby="px-home-h">
<div class="px-wrap">
<div class="px-homehead">
<div><img src="{s}assets/img/wordmark.png" alt="PRAXTERRA" width="208" height="26"><h2 id="px-home-h">PRAXTERRA sustainability tools</h2>
<p>Optional tools for the free PRAXTERRA sustainability management standard. The standard is free at praxterra.com; the tools make it easier to apply.</p></div>
<a class="px-btn" href="{s}">See all four tools</a>
</div>
<div class="px-minis">{mini}</div>
</div>
</section>
'''


CSS = r'''
@font-face{font-family:"Archivo";src:url("fonts/archivo-var.woff2") format("woff2");font-weight:100 900;font-stretch:62% 125%;font-display:swap}
@font-face{font-family:"Public Sans";src:url("fonts/public-sans-var.woff2") format("woff2");font-weight:100 900;font-display:swap}
:root{--px-green:#214E3B;--px-green-2:#2D5E48;--px-ink:#292E2B;--px-muted:#5B635D;--px-ivory:#F4F0E6;--px-surface:#FBF9F3;--px-line:#D8D4C7;--px-terra:#BC6949;--px-terra-ink:#9A4F33;--frq-navy:#14254A;--frq-yellow:#F5B400}
.px-body{margin:0;font-family:"Public Sans",system-ui,-apple-system,"Segoe UI",sans-serif;color:var(--px-ink);background:var(--px-surface);line-height:1.55;-webkit-font-smoothing:antialiased}
.px-body *{box-sizing:border-box}
.px-body img{max-width:100%;height:auto;display:block}
.px-body h1,.px-body h2,.px-body h3,.px-homeblock h2{font-family:"Archivo","Public Sans",sans-serif;line-height:1.15;margin:0;color:var(--px-green)}
.px-body a{color:var(--px-green)}
.px-wrap{max-width:1200px;margin:0 auto;padding:0 24px}
.px-narrow{max-width:860px}
.px-skip{position:absolute;left:-999px;top:8px;background:var(--frq-yellow);color:var(--frq-navy);padding:10px 14px;border-radius:8px;font-weight:700;z-index:99}
.px-skip:focus{left:8px}
.px-body :focus-visible{outline:3px solid var(--px-terra);outline-offset:2px}
.px-ribbon{background:#FFF3C4;color:#5A4500;text-align:center;font-size:14px;font-weight:700;padding:8px 16px;border-bottom:1px solid #E8D27A}
.px-header{background:var(--frq-navy);position:sticky;top:0;z-index:20}
.px-header .px-wrap{display:flex;align-items:center;justify-content:space-between;gap:20px;min-height:72px;flex-wrap:wrap}
.px-logo{display:flex;background:#fff;border-radius:8px;padding:4px 8px}
.px-logo img{height:44px;width:auto}
.px-nav{display:flex;gap:24px;font-weight:600;font-size:15px;flex-wrap:wrap}
.px-nav a{color:#D9DFEA;text-decoration:none;padding:10px 0}
.px-nav a:hover,.px-nav a[aria-current="page"]{color:#fff;box-shadow:inset 0 -3px 0 var(--frq-yellow)}
.px-btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:48px;padding:0 22px;border-radius:8px;font-weight:700;font-size:16px;text-decoration:none;border:2px solid var(--px-green);background:var(--px-green);color:#fff!important;cursor:pointer;font-family:inherit}
.px-btn:hover{background:var(--px-green-2)}
.px-btn-ghost{background:transparent;color:var(--px-green)!important}
.px-btn-ghost:hover{background:#E7EDE7}
.px-btn-sm{min-height:40px;padding:0 16px;font-size:15px}
.px-btn-lg{min-height:56px;font-size:18px;width:100%}
.px-btn-buy{background:var(--px-terra);border-color:var(--px-terra)}
.px-btn-buy:hover{background:var(--px-terra-ink);border-color:var(--px-terra-ink)}
.px-btn-off{background:#C9C5BA;border-color:#C9C5BA;cursor:not-allowed}
.px-row{display:flex;gap:12px;flex-wrap:wrap}
.px-hero{background:var(--px-ivory);padding:56px 0;border-bottom:1px solid var(--px-line)}
.px-hero-in{display:grid;grid-template-columns:1.1fr 1fr;gap:48px;align-items:center}
.px-hero h1{font-size:clamp(32px,4.2vw,48px);font-weight:800;margin:18px 0 16px}
.px-wordmark{width:260px;height:auto}
.px-wordmark-sm{width:150px;height:auto;margin-bottom:10px}
.px-lead{font-size:19px;color:var(--px-muted);margin:0 0 24px}
.px-hero-img{border-radius:12px;box-shadow:0 18px 40px rgba(33,78,59,.18);aspect-ratio:4/3;object-fit:contain;background:var(--px-green)}
.px-section{padding:56px 0}
.px-alt{background:var(--px-ivory)}
.px-section h2{font-size:30px;font-weight:800;margin-bottom:8px}
.px-sub{color:var(--px-muted);margin:0 0 24px}
.px-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}
.px-grid-3{grid-template-columns:repeat(3,1fr);margin-top:20px}
.px-card{background:#fff;border:1px solid var(--px-line);border-radius:12px;overflow:hidden;display:flex;flex-direction:column}
.px-card-img img{aspect-ratio:4/3;object-fit:contain;background:var(--px-ivory);width:100%}
.px-card-body{padding:16px;display:flex;flex-direction:column;gap:8px;flex:1}
.px-card h3{font-size:18px;font-weight:700}
.px-card h3 a{text-decoration:none}
.px-card p{margin:0;color:var(--px-muted);font-size:15px;flex:1}
.px-card-foot{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:6px}
.px-badge{align-self:flex-start;display:inline-block;background:#F6E3DA;color:var(--px-terra-ink);font-weight:700;font-size:12px;letter-spacing:.04em;text-transform:uppercase;padding:4px 8px;border-radius:4px}
.px-price{font-family:"Archivo",sans-serif;font-weight:800;font-size:22px;color:var(--px-green)}
.px-price small{font-family:"Public Sans",sans-serif;font-weight:600;font-size:14px;color:var(--px-muted)}
.px-price-lg{font-size:36px}
.px-table-wrap{overflow-x:auto;margin-top:16px;border:1px solid var(--px-line);border-radius:12px;background:#fff}
.px-compare{border-collapse:collapse;width:100%;min-width:720px;font-size:15px}
.px-compare th,.px-compare td{padding:14px 12px;border-bottom:1px solid var(--px-line);text-align:center;vertical-align:middle;height:58px}
.px-compare thead th{background:var(--px-green);color:#fff;font-weight:700}
.px-compare thead th a{color:#fff;text-decoration:none;display:block}
.px-compare thead th span{display:block;font-weight:500;font-size:13px;color:#D7E7DB}
.px-compare th[scope=row],.px-compare thead th:first-child{text-align:left}
.px-compare td svg{color:var(--px-green);margin:auto}
.px-compare td svg[width="16"]{color:#B9B5AA}
.px-compare tbody tr:nth-child(even){background:var(--px-surface)}
.px-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.px-small{font-size:14px;color:var(--px-muted);margin:12px 0 0}
.px-note{background:#fff;border:1px solid var(--px-line);border-left:5px solid var(--px-terra);border-radius:10px;padding:18px 20px;margin-top:24px}
.px-note h2{font-size:18px!important;margin-bottom:8px}
.px-note ul{margin:0;padding-left:20px;color:var(--px-ink);font-size:15px}
.px-note li{margin:4px 0}
.px-crumbs{font-size:14px;color:var(--px-muted);padding:20px 0}
.px-crumbs a{color:var(--px-muted)}
.px-pdp{display:grid;grid-template-columns:1.05fr 1fr;gap:40px;align-items:start;padding-bottom:56px}
.px-gallery{position:sticky;top:96px}
.px-main{border-radius:12px;border:1px solid var(--px-line);aspect-ratio:4/3;object-fit:contain;background:var(--px-ivory);width:100%}
.px-thumbs{display:flex;gap:10px;margin-top:12px}
.px-thumbs button{border:2px solid var(--px-line);border-radius:8px;padding:0;background:none;cursor:pointer;width:96px;overflow:hidden}
.px-thumbs button[aria-pressed="true"]{border-color:var(--px-terra)}
.px-thumbs img{aspect-ratio:4/3;object-fit:contain;width:100%}
.px-buy h1{font-size:clamp(28px,3vw,36px);font-weight:800;margin:8px 0 12px}
.px-intro{font-size:18px;color:var(--px-muted);margin:0 0 16px}
.px-pricerow{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;margin-bottom:14px}
.px-vat{font-size:14px;color:var(--px-muted)}
.px-assure{display:flex;gap:18px;flex-wrap:wrap;font-size:14px;color:var(--px-muted);margin:14px 0 6px}
.px-assure span{display:inline-flex;align-items:center;gap:6px}
.px-box{border-top:1px solid var(--px-line);padding:18px 0 4px;margin-top:14px}
.px-box h2{font-size:20px;margin-bottom:10px}
.px-box p{margin:0}
.px-checks{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:8px}
.px-checks li{display:flex;gap:10px;align-items:flex-start}
.px-checks svg{flex:0 0 auto;color:var(--px-green);margin-top:3px}
.px-formats{list-style:none;display:flex;gap:10px;flex-wrap:wrap;padding:0;margin:14px 0 0}
.px-formats li{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--px-line);background:#fff;border-radius:6px;padding:4px 10px 4px 6px;font-weight:700;font-size:13px}
.px-upsell{background:#E7EDE7;border-radius:10px;padding:14px 16px;margin-top:18px}
.px-upsell a{font-weight:700}
.px-legal h1{font-size:34px;margin:8px 0}
.px-legal h2{font-size:20px;margin:22px 0 6px}
.px-legal p{margin:6px 0}
.px-li{padding-left:12px}
.px-footer{background:var(--px-green);color:#E3E6DD;padding:36px 0 18px;margin-top:0}
.px-footer .px-wrap{display:flex;gap:28px;justify-content:space-between;flex-wrap:wrap}
.px-footer a{color:#fff}
.px-foot-brand{display:flex;flex-direction:column;gap:10px;max-width:440px;font-size:14px}
.px-foot-brand img{width:180px;filter:brightness(0) invert(1)}
.px-footer nav{display:flex;flex-direction:column;gap:6px;font-size:14px}
.px-legalline{display:block!important;border-top:1px solid rgba(255,255,255,.18);margin-top:22px;padding-top:14px;font-size:13px;color:#C9D6CC}
.px-homeblock{background:#F4F0E6;padding:48px 0;font-family:"Public Sans",system-ui,sans-serif;color:#292E2B}
.px-homeblock img{max-width:100%;height:auto;display:block}
.px-homeblock *{box-sizing:border-box}
.px-homeblock .px-wrap{max-width:1200px;margin:0 auto;padding:0 24px}
.px-homehead{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;flex-wrap:wrap;margin-bottom:22px}
.px-homehead img{width:180px;height:auto;margin-bottom:10px}
.px-homehead h2{font-family:"Archivo",sans-serif;font-size:30px;font-weight:800;color:#214E3B;margin:0 0 6px}
.px-homehead p{margin:0;color:#5B635D;max-width:640px}
.px-homeblock .px-btn{color:#fff}
.px-minis{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.px-mini{background:#fff;border:1px solid #D8D4C7;border-radius:10px;overflow:hidden;text-decoration:none;color:#292E2B;display:flex;flex-direction:column}
.px-mini img{aspect-ratio:4/3;object-fit:contain;width:100%;background:#F4F0E6}
.px-mini b{padding:10px 12px 0;color:#214E3B;font-size:16px}
.px-mini span{padding:2px 12px 12px;color:#5B635D;font-size:14px}
@media (max-width:980px){.px-grid,.px-minis{grid-template-columns:repeat(2,1fr)}.px-grid-3{grid-template-columns:repeat(2,1fr)}.px-hero-in,.px-pdp{grid-template-columns:1fr}.px-gallery{position:static}}
@media (max-width:560px){.px-grid,.px-grid-3,.px-minis{grid-template-columns:1fr}.px-nav{gap:14px;font-size:14px}.px-section h2{font-size:26px}}
'''

# ---- write
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(os.path.join(OUT, 'assets'))
shutil.copytree(os.path.join(HERE, 'assets', 'img'), os.path.join(OUT, 'assets', 'img'))
shutil.copytree(os.path.join(HERE, 'assets', 'fonts'), os.path.join(OUT, 'assets', 'fonts'))
open(os.path.join(OUT, 'assets', 'praxterra.css'), 'w', encoding='utf-8').write(CSS.strip() + '\n')
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(section_page())
for p in P:
    os.makedirs(os.path.join(OUT, p['slug']))
    open(os.path.join(OUT, p['slug'], 'index.html'), 'w', encoding='utf-8').write(product_page(p))
os.makedirs(os.path.join(OUT, 'licence'))
open(os.path.join(OUT, 'licence', 'index.html'), 'w', encoding='utf-8').write(licence_page())
open(os.path.join(HERE, 'home_block.html'), 'w', encoding='utf-8').write(home_block())
urls = [f'{DOMAIN}/{BASE}/'] + [f'{DOMAIN}/{BASE}/{p["slug"]}/' for p in P] + [f'{DOMAIN}/{BASE}/licence/']
open(os.path.join(HERE, 'sitemap_urls.txt'), 'w').write('\n'.join(urls) + '\n')
print('built', len(P), 'product pages into', OUT)
for u in urls: print(' ', u)
