"""Grafiken (SVG) und Bildplätze.

Bildplätze: assets/img/bild-<name>.webp, immer mit dem Hinweis "Symbolbild".
Fehlt eine Datei, bleibt der Farbverlauf. Startseiten-Hero: bild-hero.webp
"""
import os
import rahmen as R

INK, BROWN, CLAY, PEACH, TERRA, SAND = "#190301", "#573B24", "#E08D5F", "#FFB57F", "#B14F25", "#ECE8D7"


ALT = {
    "apherese": "Frau im Ledersessel während einer Apherese, Pfleger am Gerät", "ankommen": "Frau geht durch einen hellen Empfang",
    "gespraech": "Ärztin im Gespräch mit einem Patienten", "labor": "Pfleger mit Blutproben im Labor", "warten": "Mann mit Tee im Ledersessel am Fenster",
    "blutprobe": "Hand mit Blutröhrchen", "zuhoeren": "Ärztin hört aufmerksam zu", "blutdruck": "Ärztin misst den Blutdruck",
    "hero": "Ärztin und Patient im Gespräch am Empfang", "tresen": "Ärztin berät einen Patienten am Empfang",
    "beratung": "Beratung zu dritt mit Terminkalender", "beratung-nah": "Ärztin berät einen Patienten",
    "flur": "Heller Flur mit Olivenbaum", "wartebereich": "Wartebereich mit Ledersesseln und Pflanzen", "empfang": "Empfang mit Granittresen und Olivenbaum",
}

# Bild im Seitenkopf je Adresse.
KOPFBILD = {
    "inuspherese-zentrum-stuttgart": "apherese", "medizin/apherese-programm": "apherese", "medizin/help-apherese": "apherese", "longevity/apherese-reset": "apherese",
    "medizin": "blutdruck", "internistische-sprechstunde": "blutdruck", "ganzheitliche-sprechstunde": "zuhoeren", "darmgesundheit": "zuhoeren",
    "long-covid-sprechstunde": "beratung-nah", "sub-health-syndrom": "gespraech", "medizin/kinder": "wartebereich", "umweltmedizin": "labor",
    "labordiagnostik": "blutprobe", "energie-check": "blutprobe", "medizin/regenerationskuren": "wartebereich", "ganzkoerperhyperthermie": "wartebereich",
    "longevity": "ankommen", "longevity/check": "gespraech", "longevity/infusionen": "warten", "longevity/nad-infusion": "warten",
    "longevity/supplement-analyse": "labor", "longevity/regenerationskuren": "wartebereich", "longevity/preise": "empfang", "longevity/pflanzenwissen": "wartebereich",
    "leistungen": "blutdruck", "gutscheine": "wartebereich", "einloesen": "wartebereich", "terminvereinbarung": "beratung", "ihr-besuch": "flur", "kosten": "beratung-nah",
    "karriere-stellenangebote-jobs": "labor", "ueber-uns": "tresen", "praxis": "empfang",
}


def bild(name):
    """Pfad zum Bild oder None."""
    f = f"assets/img/bild-{name}.webp"
    return R.rel(f) if os.path.exists(os.path.join(R.ROOT, f)) else None


def bild_img(name, cls="slot", alt=None):
    p = bild(name)
    if not p:
        return ""
    return f'<img class="{cls} b-{name}" src="{p}" alt="{ALT.get(name, "") if alt is None else alt}" width="1600" height="1194"><span class="symbolbild">Symbolbild</span>'


def foto(name):
    """Bild im Text, 4:3."""
    i = bild_img(name)
    return f'<div class="foto">{i.replace("<img ", "<img loading=\'lazy\' ")}</div>' if i else ""


def hero_bild(line):
    n = KOPFBILD.get(R._current["path"])
    return bild_img(n) if n else ""


def kreislauf():
    def box(x, y, w, h, fill, t, sub="", col=INK):
        s = f'<text x="{x+w/2}" y="{y+h/2+24}" text-anchor="middle" font-size="14" fill="{col}">{sub}</text>' if sub else ""
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>'
                f'<text x="{x+w/2}" y="{y+h/2+(2 if sub else 6)}" text-anchor="middle" font-size="18" style="font-weight:600" fill="{col}">{t}</text>{s}')

    def nr(x, y, n):
        return f'<text x="{x}" y="{y}" font-size="14" fill="{TERRA}">0{n}</text>'
    return f"""<svg class="grafik" viewBox="0 0 640 430" role="img" aria-label="Kreislauf der Apherese: Blut wird entnommen, das Plasma abgetrennt, im Filter gereinigt und zusammen mit den Blutzellen zurückgegeben. Die Filterrückstände können als Eluat analysiert werden.">
<defs><marker id="pf" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M1 1 L9 5 L1 9" fill="none" stroke="context-stroke" stroke-width="1.8"/></marker></defs>
<g fill="none" stroke-width="3">
<path d="M110 158 V75 H206" stroke="{TERRA}" marker-end="url(#pf)"/>
<path d="M370 75 H446" stroke="{CLAY}" marker-end="url(#pf)"/>
<path d="M530 120 V210 H530 V346 H206" stroke="{CLAY}" marker-end="url(#pf)"/>
<path d="M290 120 V346" stroke="{TERRA}"/>
<path d="M206 346 H110 V272" stroke="{TERRA}" marker-end="url(#pf)"/>
<path d="M560 120 V196" stroke="{INK}" stroke-dasharray="4 5" stroke-width="2"/></g>
<circle cx="290" cy="346" r="6" fill="{TERRA}"/>
{box(30, 160, 160, 110, SAND, 'Sie', 'liegen bequem')}
{box(210, 30, 160, 90, PEACH, 'Trennung', 'Plasma und Zellen')}
{box(450, 30, 160, 90, CLAY, 'Filter', 'Plasma gereinigt')}
{box(544, 200, 90, 60, INK, 'Eluat', '', '#fff')}
<text x="544" y="280" font-size="13" fill="{BROWN}">auf Wunsch</text><text x="544" y="297" font-size="13" fill="{BROWN}">Analyse</text>
{nr(30, 150, 1)}{nr(210, 20, 2)}{nr(450, 20, 3)}
<g font-size="14" fill="{BROWN}"><text x="122" y="62">Blut</text><text x="384" y="62">Plasma</text>
<text x="300" y="215">Blutzellen</text><text x="350" y="334">gereinigtes Plasma</text><text x="30" y="384">zurück in den Körper</text></g>
<text x="30" y="416" font-size="13" fill="{BROWN}">Vereinfachte Darstellung</text></svg>"""


def filterprinzip():
    gross = [(70, 90), (140, 190), (95, 270), (205, 120), (225, 260), (155, 60)]
    klein = [(60, 150), (120, 130), (180, 225), (110, 220), (235, 190), (200, 60), (250, 80), (60, 230)]
    durch = [(400, 80), (450, 140), (385, 180), (510, 100), (560, 180), (430, 240), (500, 220), (570, 270), (380, 280), (480, 290)]
    b = "".join(f'<circle cx="{x}" cy="{y}" r="22" fill="{INK}"/><circle cx="{x+15}" cy="{y-15}" r="6" fill="{CLAY}"/>' for x, y in gross)
    k = "".join(f'<circle cx="{x}" cy="{y}" r="6" fill="{PEACH}" stroke="{TERRA}"/>' for x, y in klein + durch)
    m = "".join(f'<rect x="308" y="{y}" width="14" height="24" fill="{INK}"/>' for y in range(36, 310, 38))
    return f"""<svg class="grafik" viewBox="0 0 640 400" role="img" aria-label="Prinzip des Filters: Kleine Bestandteile wie Wasser, Salze und die meisten Nährstoffe gehen durch den Filter, große Eiweiße und Fette mit daran gebundenen Stoffen werden zurückgehalten.">
<rect x="20" y="30" width="288" height="290" fill="{SAND}"/><rect x="322" y="30" width="298" height="290" fill="#FDFAEE"/>
{b}{k}{m}
<g fill="none" stroke="{TERRA}" stroke-width="2"><path d="M268 174 H358 M350 167 L358 174 L350 181"/></g>
<g font-size="14" fill="{INK}"><text x="20" y="20">Plasma vor dem Filter</text><text x="340" y="20">Gereinigtes Plasma, zurück zu Ihnen</text></g>
<g font-size="13" fill="{BROWN}"><circle cx="30" cy="351" r="9" fill="{INK}"/><text x="48" y="356">große Eiweiße und Fette</text>
<circle cx="30" cy="381" r="5" fill="{CLAY}"/><text x="48" y="386">daran gebundene Stoffe</text>
<circle cx="336" cy="351" r="5" fill="{PEACH}" stroke="{TERRA}"/><text x="354" y="356">Wasser, Salze, die meisten Nährstoffe</text>
<text x="336" y="386">Vereinfachte Darstellung</text></g></svg>"""


# Lucide-Icons (lucide.dev, ISC-Lizenz)
ICONS = {
    'gespraech': '<path d="M16 10a2 2 0 0 1-2 2H6.828a2 2 0 0 0-1.414.586l-2.202 2.202A.71.71 0 0 1 2 14.286V4a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/> <path d="M20 9a2 2 0 0 1 2 2v10.286a.71.71 0 0 1-1.212.502l-2.202-2.202A2 2 0 0 0 17.172 19H10a2 2 0 0 1-2-2v-1"/>',
    'diagnostik': '<path d="M14 2v6a2 2 0 0 0 .245.96l5.51 10.08A2 2 0 0 1 18 22H6a2 2 0 0 1-1.755-2.96l5.51-10.08A2 2 0 0 0 10 8V2"/> <path d="M6.453 15h11.094"/> <path d="M8.5 2h7"/>',
    'plan': '<path d="M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2z"/> <path d="M14 2v5a1 1 0 0 0 1 1h5"/> <path d="M10 9H8"/> <path d="M16 13H8"/> <path d="M16 17H8"/>',
    'begleitung': '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/> <path d="M16 3.128a4 4 0 0 1 0 7.744"/> <path d="M22 21v-2a4 4 0 0 0-3-3.87"/> <circle cx="9" cy="7" r="4"/>',
}


def icon(name):
    return f'<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{ICONS[name]}</svg>'
