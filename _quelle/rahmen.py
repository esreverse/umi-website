#!/usr/bin/env python3
"""
UMI Stuttgart – Seitengenerator

Erzeugt aus den Inhalten in seiten.py die fertigen HTML-Dateien im Hauptordner
des Repositorys. Die erzeugten Dateien sind eingecheckt, die Website braucht
also keinen Build, um zu laufen. Dieses Skript ist nur eine Hilfe, damit Kopf,
Fuß, Preise und Links überall gleich bleiben.

Wird über build.py aufgerufen.

Ohne --live entsteht die Vorschau: Jede Seite trägt "noindex", robots.txt sperrt
alle Suchmaschinen, oben steht ein Vorschau-Hinweis.
"""
import json
import os
import posixpath
import sys

sys.path.insert(0, os.path.dirname(__file__))
import config as C  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LIVE = "--live" in sys.argv
PREVIEW = not LIVE


# ---------------------------------------------------------------- Hilfen

class Page:
    def __init__(self, path, title, desc, body, line="dach", h1=None,
                 crumbs=None, jsonld=None, nav=None):
        self.path = path.strip("/")  # "" = Startseite, sonst "medizin/apherese-programm"
        self.title = title
        self.desc = desc
        self.body = body
        self.line = line
        self.crumbs = crumbs or []
        self.jsonld = jsonld or []
        self.nav = nav


_current = {"path": ""}


def rel(target):
    """Relativer Link vom aktuellen Seitenordner zum Ziel (z. B. "gutscheine/")."""
    if target.startswith(("http", "mailto:", "tel:", "#")):
        return target
    here = _current["path"]
    base = here if here else "."
    anchor = ""
    if "#" in target:
        target, anchor = target.split("#", 1)
        anchor = "#" + anchor
    is_dir = target == "" or target.endswith("/")
    t = target.strip("/") or "."
    r = posixpath.relpath(t, base)
    if is_dir:
        r = "./" if r == "." else r + "/"
    return r + anchor


def a(target, text, cls=None, extra=""):
    c = f' class="{cls}"' if cls else ""
    href = rel(target)
    ext = ' rel="noopener" target="_blank"' if target.startswith("http") else ""
    return f'<a href="{href}"{c}{ext}{extra}>{text}</a>'


def price(key, prefix="ab"):
    """Preis aus config.PREISE. Fehlt er, erscheint ein gut sichtbarer Platzhalter."""
    v = C.PREISE.get(key)
    if v is None:
        return (f'<span class="preis-offen" title="Preis folgt nach Freigabe">'
                f'{prefix + " " if prefix else ""}… €</span>')
    return f"{prefix + '&nbsp;' if prefix else ''}{v.replace(' €', '&nbsp;€')}"


def book(label="Termin buchen", cls="btn", url=None):
    u = url or C.DOCTOLIB
    return f'<a class="{cls}" href="{u}" rel="noopener" target="_blank">{label}</a>'


def shop(label="Gutschein online kaufen", cls="btn", value=None):
    if C.GUTSCHEIN_SHOP:
        return f'<a class="{cls}" href="{C.GUTSCHEIN_SHOP}" rel="noopener" target="_blank">{label}</a>'
    return (f'<a class="{cls}" href="#" aria-disabled="true" '
            f'title="Der Online-Shop wird gerade eingerichtet">{label} (in Kürze)</a>')


def tel(cls=None, text=None):
    c = f' class="{cls}"' if cls else ""
    return f'<a{c} href="tel:{C.TEL_LINK}">{text or C.TEL}</a>'


def faq(items, heading="Fragen und Antworten"):
    """items = [(frage, antwort_html)]. Gibt HTML und JSON-LD zurück."""
    html = [f'<section class="faq bg-paper"><div class="wrap narrow"><h2>{heading}</h2>']
    for q, ans in items:
        html.append(f"<details><summary>{q}</summary><div>{ans}</div></details>")
    html.append("</div></section>")
    import re
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q,
         "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", ans).replace("&nbsp;", " ")}}
        for q, ans in items]}
    return "".join(html), ld


def mark(variant="dach", size=None):
    """UMI-Bildmarke (nachgezeichnet aus dem Linien-Design)."""
    cols = {
        "dach": ("#E08D5F", "#573B24", "#190301"),
        "med": ("#E08D5F", "#573B24", "#693916"),
        "lon": ("#FFB57F", "#E08D5F", "#D9774C"),
        "light": ("#FFFFFF", "#FFFFFF", "#FFFFFF"),
    }[variant]
    s = f' width="{size}" height="{size}"' if size else ""
    return (f'<svg viewBox="0 0 100 100"{s} aria-hidden="true" focusable="false">'
            f'<path d="M38 13 A39 39 0 0 0 44 89" fill="none" stroke="{cols[0]}" stroke-width="6" stroke-linecap="round"/>'
            f'<path d="M63 15 A39 39 0 0 1 72 82" fill="none" stroke="{cols[1]}" stroke-width="4" stroke-linecap="round"/>'
            f'<circle cx="52" cy="27" r="10" fill="{cols[2]}"/>'
            f'<path d="M12 33 C30 38 44 44 52 46 C62 42 78 32 94 22 C76 40 60 60 54 97 C46 66 30 46 12 33 Z" fill="{cols[2]}"/></svg>')


# ---------------------------------------------------------------- Rahmen

NAV = [
    ("medizin/", "UMI Medizin", "med"),
    ("longevity/", "UMI Longevity", "lon"),
    ("therapien", "Therapien", "ther"),
    ("diagnostik", "Diagnostik", "dia"),
    ("gutscheine/", "Gutscheine", "gut"),
    ("ueber-uns/", "Über uns", "ueber"),
]

# Ausklappmenüs: (Gruppe oder None, [(Ziel, Text)])
DROPDOWNS = {
    "therapien": [
        ("Apherese", [("inuspherese-zentrum-stuttgart/", "INUSpherese®"), ("medizin/help-apherese/", "H.E.L.P.-Apherese"),
                      ("medizin/apherese-programm/", "Apherese-Programm")]),
        ("Wärme, Sauerstoff, Licht", [("ganzkoerperhyperthermie/", "Ganzkörperhyperthermie"),
                                      ("medizin/regenerationskuren/#oxyvenierung", "Oxyvenierung"),
                                      ("medizin/regenerationskuren/#farblaser", "Farblaser")]),
        ("Infusionen", [("longevity/infusionen/", "Infusionsmenü"), ("longevity/nad-infusion/", "NAD+-Infusion")]),
        ("Naturheilkunde", [("medizin/#therapien", "Akupunktur und Neuraltherapie"), ("medizin/#heilpraktikerin", "Bei unserer Heilpraktikerin"),
                            ("medizin/kinder/", "Kinder")]),
    ],
    "diagnostik": [
        ("Labor", [("labordiagnostik/", "Alle Laboruntersuchungen"), ("labordiagnostik/#basisdiagnostik", "Basisdiagnostik"),
                   ("labordiagnostik/#erweitertediagnostik", "Erweiterte Diagnostik"), ("labordiagnostik/#umwelt", "Umweltdiagnostik")]),
        ("Checks und Pakete", [("internistische-sprechstunde/#check-up", "Gesundheits-Check-up"), ("energie-check/", "Energie-Check"),
                               ("longevity/check/", "Longevity-Check"), ("longevity/supplement-analyse/", "Supplement-Analyse")]),
        ("Schwerpunkte", [("umweltmedizin/", "Umweltmedizin"), ("darmgesundheit/", "Darm und Mikrobiom")]),
    ],
}


def header(page):
    items = []
    for target, label, key in NAV:
        cur = ' aria-current="page"' if page.nav == key else ""
        if target in DROPDOWNS:
            groups = "".join(f'<div class="dd-group"><span class="dd-h">{g}</span>' +
                             "".join(f'<a href="{rel(t)}">{x}</a>' for t, x in links) + "</div>"
                             for g, links in DROPDOWNS[target])
            items.append(f'<div class="dd"><button class="dd-btn" aria-expanded="false" aria-controls="dd-{target}">{label}</button>'
                         f'<div class="dd-menu" id="dd-{target}">{groups}</div></div>')
            continue
        cls = ' class="hl"' if key == "gut" else ""
        items.append(f'<a href="{rel(target)}"{cur}{cls}>{label}</a>')
    preview = ('<div class="preview-bar">Vorschau der neuen Website · nicht öffentlich · '
               'einzelne Preise folgen</div>') if PREVIEW else ""
    return f"""{preview}<header class="site-header"><div class="wrap">
<a class="brand" href="{rel('')}" aria-label="UMI Stuttgart, zur Startseite">{mark('dach')}<div><b>UMI</b><span>Stuttgart</span></div></a>
<button class="menu-toggle" aria-expanded="false" aria-controls="hauptmenue">Menü</button>
<nav class="nav" id="hauptmenue" aria-label="Hauptmenü">{''.join(items)}<a href="{rel('terminvereinbarung/')}" class="mob-only">Termin und Kontakt</a><div class="nav-cta">{tel('btn ghost', 'Anrufen')}{book('Termin buchen')}</div></nav>
<div class="head-actions">{tel('tel')}{book('Termin buchen', 'btn small')}</div>
</div></header>"""


def footer():
    y = C.JAHR
    return f"""<footer class="site-footer"><div class="wrap">
<div class="cols">
<div><a class="brand" href="{rel('')}">{mark('dach')}<div><b>UMI</b><span>Stuttgart</span></div></a>
<p class="small" style="margin-top:16px">{C.NAME_LANG}<br>{C.STRASSE}<br>{C.PLZ} {C.ORT_LANG}</p>
<p class="small">Telefon {tel()}<br>E-Mail <a href="mailto:{C.MAIL}">{C.MAIL}</a></p></div>
<div><h4>UMI Medizin</h4><ul>
<li>{a('medizin/', 'Übersicht')}</li><li>{a('medizin/#schwerpunkte', 'Schwerpunkte')}</li>
<li>{a('medizin/apherese-programm/', 'Apherese-Programm')}</li><li>{a('medizin/help-apherese/', 'H.E.L.P.-Apherese')}</li><li>{a('umweltmedizin/', 'Umweltmedizin')}</li><li>{a('darmgesundheit/', 'Darm und Verdauung')}</li><li>{a('energie-check/', 'Energie-Check')}</li>
<li>{a('ganzkoerperhyperthermie/', 'Ganzkörperhyperthermie')}</li><li>{a('labordiagnostik/', 'Diagnostik')}</li></ul></div>
<div><h4>UMI Longevity</h4><ul>
<li>{a('longevity/', 'Übersicht')}</li><li>{a('longevity/check/', 'Longevity-Check')}</li>
<li>{a('longevity/nad-infusion/', 'NAD+')}</li><li>{a('longevity/infusionen/', 'Infusionsmenü')}</li>
<li>{a('longevity/apherese-reset/', 'Apherese Reset')}</li><li>{a('longevity/preise/', 'Preise')}</li></ul></div>
<div><h4>Praxis</h4><ul>
<li>{a('terminvereinbarung/', 'Termin und Kontakt')}</li><li>{a('ihr-besuch/', 'Ihr Besuch bei uns')}</li>
<li>{a('kosten/', 'Kosten und Erstattung')}</li><li>{a('gutscheine/', 'Gutscheine')}</li>
<li>{a('ueber-uns/', 'Team')}</li><li>{a('praxis/', 'Unsere Räume')}</li>
<li>{a('karriere-stellenangebote-jobs/', 'Karriere')}</li></ul></div>
</div>
<p class="small" style="margin-top:28px">Öffnungszeiten: {C.OEFFNUNGSZEITEN}</p>
<div class="legal"><span>© {y} UMI Stuttgart GmbH</span>
<span>{a('impressum/', 'Impressum')} · {a('datenschutzerklaerung-umi-stuttgart-gmbh/', 'Datenschutz')} · {a('gutscheinbedingungen/', 'Gutscheinbedingungen')} · <a href="{C.INSTAGRAM}" rel="noopener" target="_blank">Instagram</a> · <a href="{C.FACEBOOK}" rel="noopener" target="_blank">Facebook</a></span></div>
</div></footer>"""


def clinic_ld():
    return {
        "@context": "https://schema.org", "@type": "MedicalClinic",
        "name": "UMI Stuttgart", "alternateName": C.NAME_LANG,
        "url": C.DOMAIN + "/", "telephone": C.TEL_INTL, "email": C.MAIL,
        "address": {"@type": "PostalAddress", "streetAddress": C.STRASSE,
                    "postalCode": C.PLZ, "addressLocality": "Stuttgart",
                    "addressRegion": "Baden-Württemberg", "addressCountry": "DE"},
        "openingHours": C.OEFFNUNGSZEITEN_LD,
        "medicalSpecialty": ["Umweltmedizin", "Innere Medizin"],
        "availableService": [
            {"@type": "MedicalTherapy", "name": "INUSpherese", "alternateName": "Blutwäsche"},
            {"@type": "MedicalTherapy", "name": "H.E.L.P.-Apherese"},
            {"@type": "MedicalTherapy", "name": "Ganzkörperhyperthermie",
             "alternateName": ["Fieberbett", "Fiebertherapie"]}],
        "sameAs": [C.INSTAGRAM, C.FACEBOOK, C.DOCTOLIB],
    }


def crumbs_html(page):
    if not page.crumbs:
        return ""
    parts = [a("", "Start")]
    for target, label in page.crumbs:
        parts.append(a(target, label) if target is not None else label)
    return '<nav class="crumbs" aria-label="Brotkrumen">' + " › ".join(parts) + "</nav>"


def crumbs_ld(page):
    if not page.crumbs:
        return None
    items = [{"@type": "ListItem", "position": 1, "name": "Start", "item": C.DOMAIN + "/"}]
    for i, (target, label) in enumerate(page.crumbs, start=2):
        it = {"@type": "ListItem", "position": i, "name": label}
        t = target if target is not None else page.path + "/"
        it["item"] = C.DOMAIN + "/" + t
        items.append(it)
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}


def render(page):
    _current["path"] = "" if page.path == "404" else page.path
    body = page.body() if callable(page.body) else page.body
    extra_ld = []
    if isinstance(body, tuple):
        body, extra_ld = body
    robots = '<meta name="robots" content="noindex, nofollow">' if PREVIEW else '<meta name="robots" content="index, follow">'
    canonical = C.DOMAIN + "/" + (page.path + "/" if page.path else "")
    lds = [clinic_ld()] if page.path == "" else []
    lds += page.jsonld + extra_ld
    cl = crumbs_ld(page)
    if cl:
        lds.append(cl)
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
    title = page.title
    body = body.replace("{{CRUMBS}}", crumbs_html(page))
    base = ""
    if page.path == "404":
        base = f'<base href="{C.BASIS_LIVE if LIVE else C.BASIS_VORSCHAU}">\n'
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
{base}<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{page.desc}">
{robots}
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:locale" content="de_DE">
<meta property="og:site_name" content="UMI Stuttgart">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{page.desc}">
<link rel="icon" href="{rel('assets/img/favicon.svg')}" type="image/svg+xml">
<link rel="preload" href="{rel('assets/fonts/season-sans-vf.woff2')}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{rel('assets/css/umi.css')}">
<meta name="theme-color" content="#FBF9F4">
{ld_html}
</head>
<body class="{page.line}{' home' if page.path == '' else ''}">
<a class="skip" href="#inhalt">Zum Inhalt springen</a>
{header(page)}
<main id="inhalt">
{body}
</main>
{footer()}
<script src="{rel('assets/js/umi.js')}" defer></script>
</body>
</html>
"""
    out = os.path.join(ROOT, page.path, "index.html") if page.path != "404" else os.path.join(ROOT, "404.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return out


def redirect(old, new):
    """Weiterleitung für Server ohne .htaccess (z. B. GitHub Pages)."""
    _current["path"] = old
    target = rel(new)
    html = f"""<!DOCTYPE html><html lang="de"><head><meta charset="utf-8">
<title>Weiterleitung</title><meta name="robots" content="noindex">
<link rel="canonical" href="{C.DOMAIN}/{new}">
<meta http-equiv="refresh" content="0; url={target}"></head>
<body><p>Diese Seite ist umgezogen: <a href="{target}">weiter</a>.</p></body></html>
"""
    out = os.path.join(ROOT, old, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)


def extras(pages):
    # robots.txt
    with open(os.path.join(ROOT, "robots.txt"), "w") as f:
        if PREVIEW:
            f.write("# Vorschau: nicht indexieren\nUser-agent: *\nDisallow: /\n")
        else:
            f.write(f"User-agent: *\nAllow: /\n\nSitemap: {C.DOMAIN}/sitemap.xml\n")
    # sitemap.xml
    urls = "".join(f"<url><loc>{C.DOMAIN}/{p.path + '/' if p.path else ''}</loc></url>\n"
                   for p in pages if p.path != "404")
    with open(os.path.join(ROOT, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")
    # .htaccess für Host Europe (Apache)
    rules = "\n".join(f"Redirect 301 /{o}/ /{n}" for o, n in C.WEITERLEITUNGEN)
    with open(os.path.join(ROOT, ".htaccess"), "w") as f:
        f.write("# UMI Stuttgart – Apache-Einstellungen für Host Europe\n"
                "ErrorDocument 404 /404.html\n\n"
                "# Dauerhafte Weiterleitungen alter Adressen\n" + rules + "\n\n"
                "# Alles auf https und ohne www\n"
                "RewriteEngine On\n"
                "RewriteCond %{HTTPS} off [OR]\n"
                "RewriteCond %{HTTP_HOST} ^www\\. [NC]\n"
                "RewriteRule ^ https://umi-stuttgart.de%{REQUEST_URI} [L,R=301]\n\n"
                + ("# Vorschau: nicht indexieren\nHeader set X-Robots-Tag \"noindex, nofollow\"\n" if PREVIEW else "")
                + "<IfModule mod_expires.c>\nExpiresActive On\n"
                "ExpiresByType text/css \"access plus 1 month\"\n"
                "ExpiresByType application/javascript \"access plus 1 month\"\n"
                "ExpiresByType font/woff2 \"access plus 1 year\"\n"
                "ExpiresByType image/jpeg \"access plus 1 month\"\n"
                "ExpiresByType image/svg+xml \"access plus 1 month\"\n</IfModule>\n")


def main():
    import seiten
    pages = seiten.PAGES
    for p in pages:
        render(p)
    for o, n in C.WEITERLEITUNGEN:
        redirect(o, n)
    extras(pages)
    with open(os.path.join(ROOT, "assets/img/favicon.svg"), "w") as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" fill="#FBF9F4"/>'
                '<circle cx="52" cy="27" r="11" fill="#190301"/><path d="M12 33 C30 38 44 44 52 46 C62 42 78 32 94 22 C76 40 60 60 54 97 C46 66 30 46 12 33 Z" fill="#190301"/></svg>')
    print(f"{len(pages)} Seiten erzeugt ({'LIVE' if LIVE else 'Vorschau, noindex'}).")


if False:
    main()
