#!/usr/bin/env python3
"""Static site generator for elmgrovegaragedoor.com

Edit SITE below (phone, email, form endpoint, logo, favicon), then run:  python3 build.py
Output goes to ./public (served as static assets on Cloudflare Workers).
Copy lives in ./content/home.json and ./content/services/<slug>.json
"""
import json, html, re
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "public"
CONTENT = ROOT / "content"

SITE = {
    "name": "Elm Grove Garage Door",
    "domain": "https://elmgrovegaragedoor.com",
    "phone": "(262) 000-0000",          # TODO: replace with the real number
    "phone_href": "tel:+12620000000",    # TODO: replace with the real number
    "email": "hello@elmgrovegaragedoor.com",  # TODO: confirm
    "city": "Elm Grove", "state": "WI", "zip": "53122",
    "hours": "Mon–Sat 7am–7pm",
    "form_endpoint": "",   # e.g. https://formspree.io/f/xxxx  (blank = on-page confirmation only)
    "logo": "",            # e.g. /images/logo.webp (2x at /images/logo@2x.webp). Blank = built-in wordmark
    "logo_footer": "",     # optional light version for the dark footer
    "favicon": False,      # set True once favicon.ico, favicon-32.png, apple-touch-icon.png, icon-192/512.png are in /public
}
HOME_TITLE = "Same Day Garage Door Repair & Installation in Elm Grove, WI"
THEME = "#557f66"

CATS = ["Service & Repair", "Garage Doors", "Garage Door Openers"]

# slug, nav name, category, short blurb, primary image, secondary image, hero background, local-note background
SERVICES = [
    ("garage-door-repairs", "Garage Door Repair", "Service & Repair", "Noisy, crooked, slow or stuck. We trace the cause and fix it right.", "technician-repairing-garage-door", "technician-homeowner-garage-door", "colonial-home-garage", "elm-grove-creek-bridge"),
    ("same-day-garage-door-repair-service", "Same Day Repair", "Service & Repair", "Door stuck open or car trapped inside? Call early for same-day help.", "snow-shoveling-driveway", "family-snowy-day-driveway", "snowy-chalet-wood-garage", "autumn-village-street"),
    ("broken-garage-door-springs-repair", "Spring Replacement", "Service & Repair", "Torsion and extension springs sized to your door and balanced by hand.", "garage-door-spring-and-motor", "garage-door-springs-closeup", "ranch-home-double-garage", "autumn-park-gazebo"),
    ("garage-door-cable-repair", "Cable Replacement", "Service & Repair", "Frayed or snapped lift cables replaced and wound evenly on both drums.", "garage-door-lift-cable-closeup", "cable-pulley-closeup", "two-story-home-white-garage-door", "autumn-pond-reflections"),
    ("roller-replacement-repair", "Roller Replacement", "Service & Repair", "Quiet sealed-bearing rollers that end the grinding and ease the opener.", "garage-door-rollers", "garage-door-track-closeup", "tan-garage-door-home", "creek-footbridge-autumn"),
    ("garage-door-panel-replacement", "Panel Replacement", "Service & Repair", "Dented or cracked sections matched and replaced so the door seals again.", "raised-panel-garage-door", "white-garage-door-brick", "brick-building-white-garage-doors", "autumn-tree-lined-street"),
    ("garage-door-track-replacement", "Track Replacement", "Service & Repair", "Bent or loose tracks straightened or replaced and anchored square.", "garage-door-track-closeup", "technician-ladder-drill", "white-brick-garage-door", "elm-grove-aerial-autumn"),
    ("garage-door-drum-replacement", "Drum Replacement", "Service & Repair", "Worn cable drums replaced and set so both sides lift level.", "cable-drum-gears-closeup", "garage-door-technician-van", "detached-garage-door", "elm-grove-creek-bridge"),
    ("new-garage-door-installation", "Garage Door Installation", "Garage Doors", "Insulated new doors measured, installed, sealed and balanced.", "new-garage-door-installation", "colonial-home-garage", "luxury-home-two-car-garage", "autumn-village-street"),
    ("garage-door-materials", "Garage Door Materials", "Garage Doors", "Steel, wood, composite, fiberglass and glass, compared for Wisconsin.", "modern-glass-home-garage", "wood-garage-door-brick-facade", "modern-home-twilight", "autumn-pond-reflections"),
    ("garage-door-styles", "Garage Door Styles", "Garage Doors", "Raised panel, carriage house, flush modern and full-view glass.", "carriage-garage-doors-stone-shutters", "stone-home-wood-garage-doors", "twilight-estate-garage", "autumn-park-gazebo"),
    ("custom-garage-doors", "Custom Garage Doors", "Garage Doors", "Odd sizes, real wood, arched tops and finishes made for your home.", "custom-wood-door-panels", "arched-white-garage-door", "stone-home-wood-garage-doors", "creek-footbridge-autumn"),
    ("new-garage-door-opener-installation", "Opener Installation", "Garage Door Openers", "Quiet belt, chain and wall-mount openers with smart phone control.", "opener-installation-technician", "garage-interior-opener-door", "white-garage-door-modern-home", "autumn-tree-lined-street"),
    ("garage-door-opener-repair", "Opener Repair", "Garage Door Openers", "Remotes, keypads, sensors, gears and logic boards fixed on site.", "technician-opener-remote", "smart-garage-app", "black-garage-door-white-house", "elm-grove-aerial-autumn"),
]
SVC = {s[0]: s for s in SERVICES}

GALLERY = [  # homepage horizontal "door styles" reel
    ("carriage-garage-doors-stone-shutters", "Carriage house", "Swing-out look, overhead operation"),
    ("wood-garage-door-brick-facade", "Natural wood", "Vertical cedar-tone boards"),
    ("black-garage-door-stone", "Flush modern", "Smooth black steel in stone"),
    ("raised-panel-garage-door", "Raised panel", "The classic Elm Grove ranch door"),
    ("modern-glass-home-garage", "Full-view glass", "Aluminum frame, frosted lites"),
    ("arched-white-garage-door", "Arched top", "Custom curve to match the opening"),
    ("stone-home-wood-garage-doors", "Stained wood", "Warm tones on a stone facade"),
    ("brown-modern-garage-door-brick", "Ribbed steel", "Low-maintenance, insulated"),
]

e = html.escape

# ---------------------------------------------------------------- icons
def svg(p, sw=1.8):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{p}</svg>'

ICON = {
    "phone": svg('<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>', 2),
    "tick": svg('<path d="M20 6 9 17l-5-5"/>', 2.6),
    "arrow": svg('<path d="M5 12h14M13 6l6 6-6 6"/>', 2),
    "arrowup": svg('<path d="M7 17 17 7M8 7h9v9"/>', 2),
    "chev": '<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>',
    "plus": svg('<path d="M12 5v14M5 12h14"/>', 2.2),
    "clock": svg('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'),
    "tag": svg('<path d="M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8z"/><circle cx="7.5" cy="7.5" r="1.5"/>'),
    "shield": svg('<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>'),
    "tool": svg('<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9z"/>'),
    "snow": svg('<path d="M12 2v20M4.9 4.9l14.2 14.2M2 12h20M4.9 19.1 19.1 4.9"/>'),
    "home": svg('<path d="M3 10.5 12 3l9 7.5V21H3z"/><path d="M7 21v-7h10v7M7 17.5h10"/>'),
    "pin": svg('<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>'),
    "mail": svg('<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 6-10 7L2 6"/>'),
    "bolt": svg('<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>'),
    "leaf": svg('<path d="M11 20A7 7 0 0 1 4 13c0-6 7-10 16-10 0 9-4 16-10 16"/><path d="M4 21c4-4 7-7 10-10"/>'),
    "sun": svg('<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>'),
    "flower": svg('<circle cx="12" cy="12" r="2.5"/><path d="M12 9.5V4M12 20v-5.5M9.5 12H4M20 12h-5.5M10.2 10.2 6.3 6.3M17.7 17.7l-3.9-3.9M13.8 10.2l3.9-3.9M6.3 17.7l3.9-3.9"/>'),
    "remote": svg('<rect x="7" y="2" width="10" height="20" rx="3"/><circle cx="12" cy="8" r="2"/><path d="M10 14h4M10 17h4"/>'),
    "door": svg('<rect x="3" y="6" width="18" height="15" rx="1"/><path d="M3 10h18M3 14h18M3 18h18M7 3h10l4 3H3z"/>'),
    "tree": svg('<path d="M12 22v-6"/><path d="M12 16c-4.4 0-7-2.6-7-6 0-2.5 1.6-4.4 3.6-5.2A4 4 0 0 1 12 2a4 4 0 0 1 3.4 2.8C17.4 5.6 19 7.5 19 10c0 3.4-2.6 6-7 6z"/>'),
}
SEASON = {"Winter": ("snow", "family-snowy-day-driveway"), "Spring": ("flower", "two-story-home-white-garage-door"),
          "Summer": ("sun", "family-driveway-basketball"), "Fall": ("leaf", "autumn-village-street")}
WHY_ICONS = ["clock", "tag", "tool", "shield", "home", "tree"]

MARK = '''<svg class="mark" viewBox="0 0 48 48" aria-hidden="true"><rect width="48" height="48" rx="14" fill="var(--grove)"/><circle cx="24" cy="18" r="10.5" fill="var(--elm-l)"/><circle cx="17" cy="21" r="6.5" fill="var(--elm)"/><circle cx="31" cy="21" r="6.5" fill="var(--elm)"/><rect x="11" y="27" width="26" height="12" rx="1.6" fill="#fff"/><path d="M11 31h26M11 35h26" stroke="var(--grove)" stroke-width="1.4"/><circle cx="35" cy="12" r="2.4" fill="var(--amber)"/></svg>'''

def phone_btn(cls="btn btn--elm", label=None):
    return f'<a class="{cls}" href="{SITE["phone_href"]}" data-magnetic><span class="btn__ico">{ICON["phone"]}</span><span>{e(label or SITE["phone"])}</span></a>'

def link_btn(href, label, cls="btn btn--ghost"):
    return f'<a class="{cls}" href="{href}" data-magnetic><span>{e(label)}</span><span class="btn__arrow">{ICON["arrow"]}</span></a>'

def tick_li(text):
    return f'<li><span class="tick">{ICON["tick"]}</span><span>{e(text)}</span></li>'

def h2(a, b, cls=""):
    return f'<h2 class="h2 {cls}" data-split>{e(a)} <em>{e(b)}</em></h2>'

def label(t, cls=""):
    return f'<p class="label {cls}" data-reveal><span class="label__leaf" aria-hidden="true">{ICON["leaf"]}</span>{e(t)}</p>'

def img(name, alt, cls="", eager=False, extra=""):
    load = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    return f'<img src="/images/{name}.webp" alt="{e(alt)}" {load} class="{cls}" {extra}>'

def bg(name, cls="bgimg", speed="0.12"):
    """Low-opacity photographic section background."""
    return f'<div class="{cls}" aria-hidden="true"><img src="/images/{name}.webp" alt="" loading="lazy" decoding="async" data-parallax="{speed}"></div>'

def frame(name, alt, cls="", eager=False):
    """Photo in a rounded frame that wipes open on scroll."""
    return f'<figure class="frame {cls}" data-wipe>{img(name, alt, eager=eager)}</figure>'

def logo(footer=False):
    src = SITE["logo_footer"] if footer and SITE["logo_footer"] else SITE["logo"]
    if src:
        cls = "logo logo--img logo--footer" if footer else "logo logo--img"
        return f'<a class="{cls}" href="/" aria-label="{e(SITE["name"])} home"><img src="{src}" srcset="{src} 1x, {src.replace(".webp", "@2x.webp")} 2x" alt="{e(SITE["name"])} logo" width="240" height="96" class="logo__img"></a>'
    return f'<a class="logo" href="/" aria-label="{e(SITE["name"])} home">{MARK}<span class="logo__txt"><b>Elm Grove</b><small>Garage Door</small></span></a>'

# ---------------------------------------------------------------- chrome
def nav_html(current=None):
    cols = []
    for cat in CATS:
        items = "".join(
            f'<li><a href="/{s[0]}/"{" aria-current=page" if s[0]==current else ""}><b>{e(s[1])}</b><small>{e(s[3])}</small></a></li>'
            for s in SERVICES if s[2] == cat)
        cols.append(f'<div class="mega__col"><p class="mega__h">{e(cat)}</p><ul>{items}</ul></div>')
    mega = f'''<div class="mega" role="region" aria-label="All services"><div class="mega__in">{"".join(cols)}
<a class="mega__card" href="/same-day-garage-door-repair-service/"><img src="/images/snow-shoveling-driveway.webp" alt="" loading="lazy"><span><b>Door stuck right now?</b><small>Call early for same-day repair anywhere in Elm Grove.</small></span></a></div></div>'''
    return (f'<ul class="nav" id="nav"><li><a href="/"{" aria-current=page" if current=="home" else ""}>Home</a></li>'
            f'<li class="has-mega"><button type="button" aria-expanded="false">Services{ICON["chev"]}</button>{mega}</li>'
            '<li><a href="/new-garage-door-installation/">New Doors</a></li>'
            '<li><a href="/new-garage-door-opener-installation/">Openers</a></li>'
            '<li><a href="/#service-area">Service Area</a></li><li><a href="/#faq">FAQ</a></li></ul>')

def header(current=None):
    return f'''<div class="progress" aria-hidden="true"></div>
<div class="topbar"><div class="wrap topbar__in"><span class="topbar__live"><i></i>Same-day garage door service in Elm Grove, WI 53122</span><span class="hide-sm">{e(SITE["hours"])}<b>·</b><a href="{SITE["phone_href"]}">{e(SITE["phone"])}</a></span></div></div>
<header class="header"><div class="wrap header__in">
{logo()}
<nav aria-label="Main">{nav_html(current)}</nav>
<div class="header__cta">{phone_btn("btn btn--elm btn--sm")}<button class="burger" aria-label="Open menu" aria-expanded="false" aria-controls="nav"><span></span><span></span><span></span></button></div>
</div></header>'''

def quote_form(title="Get a fast, free quote", sub="Tell us what's going on. We reply quickly during business hours.", selected=None):
    opts = "".join(f'<option value="{e(s[1])}"{" selected" if s[0]==selected else ""}>{e(s[1])}</option>' for s in SERVICES)
    action = f' action="{e(SITE["form_endpoint"])}" method="POST"' if SITE["form_endpoint"] else ""
    return f'''<form class="qform" data-quote{action} novalidate>
<div class="qform__head"><span class="qform__ring" aria-hidden="true"><i></i><i></i><i></i></span><div><p class="qform__t">{e(title)}</p><p class="qform__s">{e(sub)}</p></div></div>
<div class="qform__grid">
<label class="fld"><span>Name</span><input name="name" autocomplete="name" required placeholder="Your name"></label>
<label class="fld"><span>Phone</span><input name="phone" type="tel" autocomplete="tel" required placeholder="(262) 555-0123"></label>
<label class="fld fld--full"><span>Service needed</span><select name="service" required><option value="">Choose a service</option>{opts}<option>Something else</option></select></label>
<label class="fld"><span>ZIP code</span><input name="zip" inputmode="numeric" autocomplete="postal-code" placeholder="53122"></label>
<label class="fld"><span>Best time</span><select name="time"><option>As soon as possible</option><option>Morning</option><option>Afternoon</option><option>Evening</option></select></label>
<label class="fld fld--full"><span>What's happening?</span><textarea name="message" rows="2" placeholder="e.g. loud bang, door won't open"></textarea></label>
</div>
<input type="text" name="_gotcha" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
<button class="btn btn--amber btn--block" type="submit"><span>Request my quote</span><span class="btn__arrow">{ICON["arrow"]}</span></button>
<p class="qform__note">{ICON["shield"]}No obligation. Price confirmed before any work starts.</p>
<div class="qform__ok" role="status" hidden><span class="qform__okmark">{ICON["tick"]}</span><p><b>Thanks, we've got it.</b><br>We'll call you shortly. If the door is stuck right now, call {e(SITE["phone"])}.</p></div>
</form>'''

def map_iframe():
    return ('<iframe title="Map of Elm Grove, Wisconsin" loading="lazy" referrerpolicy="no-referrer-when-downgrade" '
            'src="https://maps.google.com/maps?q=Elm%20Grove%2C%20WI%2053122&t=&z=13&ie=UTF8&iwloc=&output=embed"></iframe>')

def footer():
    cols = []
    for cat in CATS:
        cols.append(f'<div class="fcol"><p class="fcol__h">{e(cat)}</p><ul>' + "".join(f'<li><a href="/{s[0]}/">{e(s[1])}</a></li>' for s in SERVICES if s[2]==cat) + "</ul></div>")
    return f'''<section class="prefoot"><div class="wrap prefoot__in" data-reveal>
<div><p class="prefoot__k">Elm Grove · Brookfield · Wauwatosa · New Berlin</p><p class="prefoot__t">Garage door trouble? <em>We're close by.</em></p></div>
<div class="prefoot__cta">{phone_btn("btn btn--amber")}{link_btn("/#quote", "Get a quote", "btn btn--light")}</div></div></section>
<footer class="footer">{bg("elm-grove-aerial-autumn", "bgimg bgimg--footer", "0.06")}
<div class="wrap footer__grid">
<div class="footer__brand">{logo(True)}<p>Local garage door repair, replacement and opener service for Elm Grove, WI and the surrounding Waukesha County and west Milwaukee suburbs.</p>
<ul class="footer__contact"><li>{ICON["phone"]}<a href="{SITE["phone_href"]}">{e(SITE["phone"])}</a></li><li>{ICON["mail"]}<a href="mailto:{e(SITE["email"])}">{e(SITE["email"])}</a></li><li>{ICON["clock"]}<span>{e(SITE["hours"])}</span></li><li>{ICON["pin"]}<span>Serving Elm Grove, WI 53122</span></li></ul></div>
{"".join(cols)}
<div class="footer__map"><p class="fcol__h">Find us in Elm Grove</p><div class="map">{map_iframe()}</div></div>
</div>
<div class="wrap footer__bot"><span>© <span data-year>2026</span> {e(SITE["name"])}. All rights reserved.</span><span><a href="/sitemap.xml">Sitemap</a> · Elm Grove, Wisconsin</span></div>
</footer>
<a class="mobilebar" href="{SITE["phone_href"]}">{ICON["phone"]}<span>Call now · {e(SITE["phone"])}</span></a>
<button class="totop" aria-label="Back to top"><svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="21" class="totop__track"/><circle cx="24" cy="24" r="21" class="totop__ring"/></svg>{ICON["arrowup"]}</button>'''

def head(title, desc, path, extra_ld=""):
    url = SITE["domain"] + path
    fav = ('<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">'
           '<link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">') if SITE["favicon"] else ""
    biz = {"@context": "https://schema.org", "@type": "HomeAndConstructionBusiness", "name": SITE["name"], "url": SITE["domain"],
           "telephone": SITE["phone"], "email": SITE["email"], "image": SITE["domain"] + "/images/elm-grove-brick-home-garage-hero.webp",
           "address": {"@type": "PostalAddress", "addressLocality": SITE["city"], "addressRegion": SITE["state"], "postalCode": SITE["zip"], "addressCountry": "US"},
           "areaServed": ["Elm Grove, WI", "Brookfield, WI", "Wauwatosa, WI", "New Berlin, WI", "West Allis, WI", "Menomonee Falls, WI"],
           "openingHours": "Mo-Sa 07:00-19:00"}
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{SITE["domain"]}/images/elm-grove-brick-home-garage-hero.webp">
<meta name="theme-color" content="{THEME}">{fav}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Onest:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/site.css?v=1">
<script type="application/ld+json">{json.dumps(biz)}</script>{extra_ld}
</head><body>'''

def faq_ld(faqs):
    d = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in faqs]}
    return f'<script type="application/ld+json">{json.dumps(d)}</script>'

def crumbs_ld(name, slug):
    d = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE["domain"] + "/"},
        {"@type": "ListItem", "position": 2, "name": name, "item": f'{SITE["domain"]}/{slug}/'}]}
    return f'<script type="application/ld+json">{json.dumps(d)}</script>'

def tail():
    return '<script src="/assets/js/site.js?v=1" defer></script></body></html>'

def faq_list(faqs):
    return "".join(f'''<details class="faq" data-reveal><summary><span>{e(f["q"])}</span><i>{ICON["plus"]}</i></summary><div class="faq__a"><p>{e(f["a"])}</p></div></details>''' for f in faqs)

def marquee(items):
    row = "".join(f'<span>{e(t)}</span><i aria-hidden="true">{ICON["leaf"]}</i>' for t in items)
    return f'<div class="marquee" aria-hidden="true"><div class="marquee__track">{row}{row}</div></div>'

def rings():
    return '<svg class="rings" viewBox="0 0 200 200" aria-hidden="true">' + "".join(
        f'<circle cx="100" cy="100" r="{r}" style="--d:{i}"/>' for i, r in enumerate([12, 24, 37, 49, 62, 74, 87, 98])) + '</svg>'

def leaves_canvas():
    return '<canvas class="leaves" aria-hidden="true"></canvas>'

# ---------------------------------------------------------------- homepage
def home():
    H = json.loads((CONTENT / "home.json").read_text())
    title = HOME_TITLE
    desc = "Same-day garage door repair, spring and opener service, and new garage door installation in Elm Grove, WI 53122. Upfront pricing, local technicians."

    cards = []
    for i, s in enumerate(SERVICES):
        cards.append(f'''<a class="scard" href="/{s[0]}/" style="--i:{i}" data-tilt>
<span class="scard__img">{img(s[4], s[1] + " in Elm Grove, WI")}</span>
<span class="scard__body"><small>{e(s[2])}</small><b>{e(s[1])}</b><span>{e(s[3])}</span></span><span class="scard__go">{ICON["arrowup"]}</span></a>''')
    cats_tabs = "".join(f'<button type="button" class="chip{" is-on" if i==0 else ""}" data-filter="{["all","Service & Repair","Garage Doors","Garage Door Openers"][i]}">{t}</button>' for i, t in enumerate(["All services", "Repair", "Garage doors", "Openers"]))
    for i, s in enumerate(SERVICES):
        cards[i] = cards[i].replace('class="scard"', f'class="scard" data-cat="{e(s[2])}"', 1)

    problems = "".join(f'''<article class="stack__card" style="--n:{i}">
<div class="stack__txt"><span class="stack__num">0{i+1}</span><p class="stack__lbl">{e(p["label"])}</p><h3>{e(p["title"])}</h3><p>{e(p["text"])}</p>{link_btn("/"+p["slug"]+"/", SVC[p["slug"]][1], "btn btn--ghost btn--sm")}</div>
<div class="stack__img">{img(SVC[p["slug"]][4], p["title"])}</div></article>''' for i, p in enumerate(H["problems"]))

    why = "".join(f'<article class="why" data-reveal style="--d:{i}" data-glow><span class="why__ico">{ICON[WHY_ICONS[i%6]]}</span><h3>{e(w["title"])}</h3><p>{e(w["text"])}</p></article>' for i, w in enumerate(H["whyUs"]))
    steps = "".join(f'<li class="step" data-reveal><span class="step__n">{i+1}</span><div><h3>{e(p["title"])}</h3><p>{e(p["text"])}</p></div></li>' for i, p in enumerate(H["process"]))
    reel = "".join(f'<figure class="reel__item"><div class="reel__img">{img(n, t + " garage door style")}</div><figcaption><b>{e(t)}</b><span>{e(c)}</span></figcaption></figure>' for n, t, c in GALLERY)

    seasons_tabs = "".join(f'<button type="button" role="tab" class="season__tab{" is-on" if i==0 else ""}" aria-selected="{"true" if i==0 else "false"}" data-season="{i}">{ICON[SEASON[s["label"]][0]]}<span>{e(s["label"])}</span></button>' for i, s in enumerate(H["seasons"]))
    seasons_panes = "".join(f'''<div class="season__pane{" is-on" if i==0 else ""}" role="tabpanel" data-pane="{i}"><div class="season__img">{img(SEASON[s["label"]][1], s["label"] + " in Elm Grove")}</div><div class="season__txt"><p class="season__lbl">{e(s["label"])}</p><h3>{e(s["title"])}</h3><p>{e(s["text"])}</p></div></div>''' for i, s in enumerate(H["seasons"]))

    cost = "".join(f'<li data-reveal><span class="cost__n">{i+1:02d}</span><div><h3>{e(c["title"])}</h3><p>{e(c["text"])}</p></div></li>' for i, c in enumerate(H["costFactors"]["items"]))
    maint = "".join(tick_li(b) for b in H["maintenance"]["bullets"])
    places = "".join(f'<li>{ICON["pin"]}{e(p)}</li>' for p in H["area"]["places"])
    intro_p = "".join(f'<p data-reveal>{e(p)}</p>' for p in H["intro"]["paragraphs"])
    doors_p = "".join(f'<p data-reveal>{e(p)}</p>' for p in H["doors"]["paragraphs"])
    open_p = "".join(f'<p data-reveal>{e(p)}</p>' for p in H["openers"]["paragraphs"])

    body = f'''{header("home")}
<main id="main">
<section class="hero" id="quote">
{bg("elm-grove-brick-home-garage-hero", "bgimg bgimg--hero", "0.18")}<div class="dapple" aria-hidden="true"></div>{leaves_canvas()}
<div class="wrap hero__in">
<div class="hero__copy">
<p class="pill" data-reveal><span class="pill__dot"></span>{e(H["heroKicker"])} · Elm Grove, WI</p>
<h1 class="h1" data-split>Same Day Garage Door Repair <em>&amp; Installation</em> in Elm Grove, WI</h1>
<p class="hero__lead" data-reveal>{e(H["heroIntro"])}</p>
<div class="hero__btns" data-reveal>{phone_btn("btn btn--elm btn--lg")}{link_btn("#services", "Explore services", "btn btn--ghost btn--lg")}</div>
<ul class="hero__facts" data-reveal><li>{ICON["clock"]}<span><b>Same day</b>when you call early</span></li><li>{ICON["tag"]}<span><b>Upfront</b>price before work</span></li><li>{ICON["tool"]}<span><b>Stocked</b>trucks, common parts</span></li></ul>
</div>
<div class="hero__form" data-reveal>{quote_form()}</div>
</div>
<div class="hero__badge" aria-hidden="true">{rings()}<span>Elm Grove<br><em>53122</em></span></div>
</section>

{marquee(["Spring replacement", "Opener repair", "New garage doors", "Cable and drum repair", "Same-day service", "Panel replacement", "Track repair", "Smart openers"])}

<section class="sec sec--intro">
<div class="wrap split split--stick">
<div class="split__media">{frame("technician-homeowner-garage-door", "Technician talking with an Elm Grove homeowner about a garage door repair", "frame--tall")}
<div class="float-card" data-float><span>{ICON["tree"]}</span><p><b>Tree City USA since 1989</b><small>Leafy lots mean more debris in tracks and seals. We plan for it.</small></p></div>
{frame("family-driveway-basketball", "Family playing basketball in front of a two-car garage", "frame--small")}</div>
<div class="split__txt">{label(H["intro"]["eyebrow"])}{h2(H["intro"]["h2a"], H["intro"]["h2b"])}{intro_p}
<div class="hero__btns" data-reveal>{link_btn("/garage-door-repairs/", "Garage door repair", "btn btn--elm")}{link_btn("/new-garage-door-installation/", "New door options")}</div></div>
</div></section>

<section class="sec sec--tint" id="services">{bg("wood-carriage-door-texture", "bgimg bgimg--soft", "0.08")}
<div class="wrap">
<div class="head head--row"><div>{label("What we do")}{h2("Fourteen services,", "one local crew")}</div><p class="head__lead" data-reveal>{e(H["servicesLead"])}</p></div>
<div class="chips" role="tablist" aria-label="Filter services">{cats_tabs}</div>
<div class="scards">{"".join(cards)}</div>
</div></section>

<section class="sec sec--stack">
<div class="wrap">
<div class="head head--center">{label("The calls we get most")}{h2("Four problems,", "handled the same day")}</div>
<div class="stack">{problems}</div>
</div></section>

<section class="band" aria-label="{e(H["fullwidth"]["title"])}">
<div class="band__media" data-iris>{img("elm-grove-red-maples-road", "Red maples lining a quiet road in autumn")}</div>
<div class="band__shade" aria-hidden="true"></div>
<div class="wrap band__in">
<p class="band__eyebrow" data-reveal>{e(H["fullwidth"]["eyebrow"])}</p>
<h2 class="band__title" data-split>{e(H["fullwidth"]["title"])}</h2>
<p class="band__text" data-reveal>{e(H["fullwidth"]["text"])}</p>
<div class="hero__btns" data-reveal>{phone_btn("btn btn--amber")}{link_btn("/same-day-garage-door-repair-service/", "Same day repair", "btn btn--light")}</div>
</div>
<p class="band__word" aria-hidden="true" data-drift>Elm Grove</p>
</section>

<section class="sec">
<div class="wrap">
<div class="head head--row"><div>{label("Why Elm Grove calls us")}{h2("Straight answers,", "careful work")}</div>{frame("garage-door-team", "Two friendly garage door technicians", "frame--chip")}</div>
<div class="whys">{why}</div>
</div></section>

<section class="sec sec--tint">{bg("ranch-home-double-garage", "bgimg bgimg--soft", "0.1")}
<div class="wrap split split--rev">
<div class="split__txt">{label("How a visit works")}{h2("Four steps,", "no surprises")}
<ol class="steps" data-branch><svg class="steps__line" aria-hidden="true" preserveAspectRatio="none" viewBox="0 0 4 100"><line x1="2" y1="0" x2="2" y2="100"/></svg>{steps}</ol></div>
<div class="split__media">{frame("garage-door-technician-van", "Garage door technician standing by the service van", "frame--tall")}</div>
</div></section>

<section class="sec sec--reel">
<div class="wrap head head--row"><div>{label("New garage doors")}{h2(H["doors"]["h2a"], H["doors"]["h2b"])}</div><p class="head__lead" data-reveal>Scroll the reel for styles that suit Elm Grove ranches, Colonials and newer custom homes.</p></div>
<div class="reel" data-reel><div class="reel__sticky"><div class="reel__track">{reel}</div></div></div>
<div class="wrap split split--top">
<div class="split__txt">{doors_p}</div>
<div class="split__txt"><ul class="ticks" data-reveal>{"".join(tick_li(b) for b in H["doors"]["bullets"])}</ul>
<div class="hero__btns" data-reveal>{link_btn("/new-garage-door-installation/", "Garage door installation", "btn btn--elm")}{link_btn("/garage-door-styles/", "See all styles")}</div></div>
</div></section>

<section class="sec sec--dark">{bg("garage-interior-opener-door", "bgimg bgimg--dark", "0.1")}
<div class="wrap split">
<div class="split__media">{frame("smart-garage-app", "Smartphone app controlling a garage door opener", "frame--tall")}
<div class="float-card float-card--dark" data-float><span>{ICON["remote"]}</span><p><b>Remotes, keypads, apps</b><small>Programmed and tested before we leave.</small></p></div></div>
<div class="split__txt">{label("Garage door openers", "label--light")}{h2(H["openers"]["h2a"], H["openers"]["h2b"])}{open_p}
<ul class="ticks ticks--light" data-reveal>{"".join(tick_li(b) for b in H["openers"]["bullets"])}</ul>
<div class="hero__btns" data-reveal>{link_btn("/new-garage-door-opener-installation/", "Opener installation", "btn btn--amber")}{link_btn("/garage-door-opener-repair/", "Opener repair", "btn btn--light")}</div></div>
</div></section>

<section class="sec">
<div class="wrap">
<div class="head head--center">{label("Four seasons in Elm Grove")}{h2("What each season", "does to your door")}</div>
<div class="season" data-seasons><div class="season__tabs" role="tablist">{seasons_tabs}<span class="season__ink" aria-hidden="true"></span></div><div class="season__panes">{seasons_panes}</div></div>
</div></section>

<section class="sec sec--tint">{bg("brick-building-white-garage-doors", "bgimg bgimg--soft", "0.1")}
<div class="wrap split split--top">
<div class="split__txt">{label("Pricing, explained")}{h2("What shapes", "the price")}<p data-reveal>{e(H["costFactors"]["intro"])}</p>{frame("luxury-home-two-car-garage", "Two-car garage on a landscaped suburban home", "frame--wide")}</div>
<ol class="cost">{cost}</ol>
</div></section>

<section class="sec">
<div class="wrap split">
<div class="split__txt">{label("Homeowner care")}{h2("Simple habits,", "longer door life")}<p data-reveal>{e(H["maintenance"]["intro"])}</p><ul class="ticks ticks--2" data-reveal>{maint}</ul><p data-reveal>{e(H["maintenance"]["outro"])}</p></div>
<div class="split__media">{frame("technician-ladder-drill", "Technician on a ladder servicing garage door hardware", "frame--tall")}</div>
</div></section>

<section class="sec sec--area" id="service-area">{bg("elm-grove-aerial-autumn", "bgimg bgimg--area", "0.1")}
<div class="wrap split">
<div class="split__txt">{label("Service area")}{h2("Elm Grove first,", "and the towns around it")}{"".join(f'<p data-reveal>{e(p)}</p>' for p in H["area"]["paragraphs"])}<ul class="places" data-reveal>{places}</ul></div>
<div class="split__media"><div class="mapcard" data-reveal><div class="map map--tall">{map_iframe()}</div><p>{ICON["pin"]}Village of Elm Grove, Waukesha County, WI 53122</p></div></div>
</div></section>

<section class="sec" id="faq">
<div class="wrap split split--top">
<div class="split__txt sticky">{label("Questions")}{h2("Garage door questions,", "answered")}<p data-reveal>Still unsure? Call and talk to a real person. We'll tell you honestly whether it's a repair, a replacement or something you can handle yourself.</p>{phone_btn("btn btn--elm")}</div>
<div class="faqs">{faq_list(H["faqs"])}</div>
</div></section>

<section class="cta">{bg("twilight-estate-garage", "bgimg bgimg--cta", "0.12")}
<div class="wrap cta__in"><div>{label("Ready when you are", "label--light")}<h2 class="h2" data-split>{e(H["cta"]["title"])}</h2><p data-reveal>{e(H["cta"]["text"])}</p>
<div class="hero__btns" data-reveal>{phone_btn("btn btn--amber btn--lg")}{link_btn("#quote", "Request a quote", "btn btn--light btn--lg")}</div></div>
<div class="cta__rings" aria-hidden="true">{rings()}</div></div></section>
</main>
{footer()}'''
    return head(title, desc, "/", faq_ld(H["faqs"])) + body + tail()

# ---------------------------------------------------------------- service pages
def service(slug):
    S = json.loads((CONTENT / "services" / f"{slug}.json").read_text())
    s = SVC[slug]
    name, cat, blurb, im1, im2, herobg, localbg = s[1], s[2], s[3], s[4], s[5], s[6], s[7]
    hl = "".join(f'<li data-reveal style="--d:{i}"><small>{e(h["label"])}</small><b>{e(h["value"])}</b></li>' for i, h in enumerate(S["highlights"]))
    secs = []
    imgs = [im1, im2, im1, im2]
    for i, sec in enumerate(S["sections"]):
        paras = "".join(f'<p data-reveal>{e(p)}</p>' for p in sec["paragraphs"])
        bul = f'<ul class="ticks ticks--2" data-reveal>{"".join(tick_li(b) for b in sec["bullets"])}</ul>' if sec.get("bullets") else ""
        if i in (0, 2):
            media = frame(imgs[i], f'{name} in Elm Grove, WI' if i == 0 else f'{name} detail', "frame--tall")
            secs.append(f'''<section class="sec{" sec--tint" if i==2 else ""}">{bg(herobg if i==2 else localbg, "bgimg bgimg--soft", "0.08") if i==2 else ""}<div class="wrap split{" split--rev" if i==2 else ""}">
<div class="split__media sticky">{media}</div>
<div class="split__txt">{label(sec["eyebrow"])}{h2(sec["h2a"], sec["h2b"])}{paras}{bul}</div></div></section>''')
        else:
            secs.append(f'''<section class="sec sec--narrow"><div class="wrap narrow">{label(sec["eyebrow"])}{h2(sec["h2a"], sec["h2b"])}<div class="cols2">{paras}</div>{bul}</div></section>''')
    signs = "".join(f'<article class="sign" data-reveal style="--d:{i}" data-glow><span class="sign__n">{i+1:02d}</span><h3>{e(x["title"])}</h3><p>{e(x["text"])}</p></article>' for i, x in enumerate(S["signs"]))
    steps = "".join(f'<li class="step" data-reveal><span class="step__n">{i+1}</span><div><h3>{e(p["title"])}</h3><p>{e(p["text"])}</p></div></li>' for i, p in enumerate(S["process"]))
    cost = "".join(f'<li data-reveal><span class="cost__n">{i+1:02d}</span><div><h3>{e(c["title"])}</h3><p>{e(c["text"])}</p></div></li>' for i, c in enumerate(S["costFactors"]))
    related = [x for x in SERVICES if x[2] == cat and x[0] != slug][:3]
    if len(related) < 3:
        related += [x for x in SERVICES if x[0] not in [r[0] for r in related] and x[0] != slug][:3-len(related)]
    rel = "".join(f'''<a class="scard" href="/{r[0]}/" data-tilt><span class="scard__img">{img(r[4], r[1])}</span><span class="scard__body"><small>{e(r[2])}</small><b>{e(r[1])}</b><span>{e(r[3])}</span></span><span class="scard__go">{ICON["arrowup"]}</span></a>''' for r in related)

    body = f'''{header(slug)}
<main id="main">
<section class="hero hero--svc" id="quote">
{bg(herobg, "bgimg bgimg--hero", "0.18")}<div class="dapple" aria-hidden="true"></div>{leaves_canvas()}
<div class="wrap hero__in">
<div class="hero__copy">
<nav class="crumbs" aria-label="Breadcrumb" data-reveal><a href="/">Home</a><span>/</span><span>{e(cat)}</span><span>/</span><span aria-current="page">{e(name)}</span></nav>
<p class="pill" data-reveal><span class="pill__dot"></span>{e(S["kicker"])}</p>
<h1 class="h1 h1--svc" data-split>{e(S["h1"])}</h1>
<p class="hero__lead" data-reveal>{e(S["intro"])}</p>
<div class="hero__btns" data-reveal>{phone_btn("btn btn--elm btn--lg")}{link_btn("#details", "Read the details", "btn btn--ghost btn--lg")}</div>
</div>
<div class="hero__form" data-reveal>{quote_form(f"Quote for {name.lower()}", "Fast reply during business hours. No obligation.", slug)}</div>
</div>
<div class="hero__badge" aria-hidden="true">{rings()}<span>Elm Grove<br><em>53122</em></span></div>
</section>
<section class="hl"><div class="wrap"><ul class="hl__list">{hl}</ul></div></section>
<div id="details"></div>
{"".join(secs[:2])}
<section class="sec sec--dark">{bg(im2, "bgimg bgimg--dark", "0.1")}
<div class="wrap"><div class="head head--center">{label("Warning signs", "label--light")}{h2(S["signsHeading"][0], S["signsHeading"][1])}</div><div class="signs">{signs}</div></div></section>
{"".join(secs[2:])}
<section class="sec">
<div class="wrap split split--top">
<div class="split__txt">{label("Our process")}{h2("How we handle", name.lower())}<ol class="steps" data-branch><svg class="steps__line" aria-hidden="true" preserveAspectRatio="none" viewBox="0 0 4 100"><line x1="2" y1="0" x2="2" y2="100"/></svg>{steps}</ol></div>
<div class="split__txt">{label("Pricing, explained")}{h2("What affects", "the cost")}<ol class="cost cost--1">{cost}</ol></div>
</div></section>
<section class="local">
<div class="local__media" data-iris>{img(localbg, "Autumn scenery around Elm Grove, Wisconsin")}</div><div class="band__shade" aria-hidden="true"></div>
<div class="wrap local__in"><div class="local__card" data-reveal><p class="band__eyebrow">{ICON["pin"]} Local to Elm Grove</p><h2 class="h2">{e(S["localNote"]["title"])}</h2><p>{e(S["localNote"]["text"])}</p>{phone_btn("btn btn--amber")}</div></div>
</section>
<section class="sec" id="faq">
<div class="wrap split split--top">
<div class="split__txt sticky">{label("FAQ")}{h2(name, "questions")}<p data-reveal>Have a question we didn't cover? Call us and ask. Honest answers, no pressure.</p>{phone_btn("btn btn--elm")}</div>
<div class="faqs">{faq_list(S["faqs"])}</div>
</div></section>
<section class="sec sec--tint"><div class="wrap"><div class="head head--row"><div>{label("Related services")}{h2("You might", "also need")}</div>{link_btn("/#services", "All services")}</div><div class="scards scards--3">{rel}</div></div></section>
<section class="cta">{bg(herobg, "bgimg bgimg--cta", "0.12")}
<div class="wrap cta__in"><div>{label("Elm Grove, WI", "label--light")}<h2 class="h2" data-split>{e(S["ctaTitle"])}</h2><p data-reveal>{e(S["ctaText"])}</p>
<div class="hero__btns" data-reveal>{phone_btn("btn btn--amber btn--lg")}{link_btn("#quote", "Request a quote", "btn btn--light btn--lg")}</div></div>
<div class="cta__rings" aria-hidden="true">{rings()}</div></div></section>
</main>
{footer()}'''
    return head(S["metaTitle"], S["metaDescription"], f"/{slug}/", faq_ld(S["faqs"]) + crumbs_ld(name, slug)) + body + tail()

def page404():
    body = f'''{header()}<main id="main"><section class="hero hero--404">{bg("elm-grove-creek-bridge", "bgimg bgimg--hero", "0.15")}<div class="wrap" style="position:relative;text-align:center;padding:120px 0">
<p class="pill" style="margin:auto"><span class="pill__dot"></span>Page not found</p><h1 class="h1" style="margin:24px auto">This path wandered <em>off the trail.</em></h1>
<p class="hero__lead" style="margin:0 auto 28px">The page you're looking for isn't here. Head home or call us if your garage door needs help.</p>
<div class="hero__btns" style="justify-content:center">{link_btn("/", "Back to home", "btn btn--elm")}{phone_btn("btn btn--ghost")}</div></div></section></main>{footer()}'''
    return head("Page not found | " + SITE["name"], "Page not found.", "/404") + body + tail()

def visible_words(h):
    h = re.sub(r"<(script|style|svg|iframe)[\s\S]*?</\1>", " ", h)
    h = re.sub(r"<[^>]+>", " ", h)
    return len(html.unescape(h).split())

def main():
    pages = {"index.html": home(), "404.html": page404()}
    for s in SERVICES:
        pages[f"{s[0]}/index.html"] = service(s[0])
    for p, h in pages.items():
        f = OUT / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(h)
        if p != "404.html":
            print(f"{p:58s} {visible_words(h):5d} words")
    urls = [SITE["domain"] + "/"] + [f'{SITE["domain"]}/{s[0]}/' for s in SERVICES]
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE['domain']}/sitemap.xml\n")
    (OUT / "site.webmanifest").write_text(json.dumps({"name": SITE["name"], "short_name": "Elm Grove GD", "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}], "theme_color": THEME, "background_color": "#f8f6f0", "display": "standalone"}))

if __name__ == "__main__":
    main()
