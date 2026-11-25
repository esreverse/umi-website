# UMI Stuttgart – Website

Neue, statische Website für [umi-stuttgart.de](https://umi-stuttgart.de): reines HTML, CSS und etwas JavaScript, ohne WordPress und ohne Build-Zwang. Alle Links sind relativ, die Seite läuft deshalb auf GitHub Pages (Vorschau) genauso wie später auf dem Webspace bei Host Europe.

## Aufbau

| Ordner / Datei | Inhalt |
| --- | --- |
| `index.html`, `medizin/`, `longevity/`, `gutscheine/` … | die fertigen Seiten, eine `index.html` je Adresse. Die alten Adressen (z. B. `/inuspherese-zentrum-stuttgart/`) bleiben gleich. |
| `assets/` | Schriften (Season Mix, Season Sans, selbst gehostet), Farben und Layout (`css/umi.css`), Bilder, Skript |
| `_quelle/` | Werkzeug, das die Seiten erzeugt. Wird **nicht** auf den Server hochgeladen. |
| `_quelle/config.py` | **Preise, Doctolib-Link, Gutschein-Shop, Kontakt, Öffnungszeiten** an einer Stelle |
| `_quelle/seiten_*.py` | Texte der Seiten (Dach, Medizin, Longevity) |
| `.htaccess` | Weiterleitungen (301) und Einstellungen für den Apache-Server bei Host Europe |
| `robots.txt`, `sitemap.xml`, `llms.txt`, `404.html` | für Suchmaschinen und KI-Suchen |

## Preise oder Links ändern

1. In `_quelle/config.py` den Wert eintragen, z. B. `"longevity_check": "449 €",`. Steht dort `None`, zeigt die Seite den Platzhalter „ab … €“.
2. Im Hauptordner `python3 _quelle/build.py` ausführen (nur Python 3, keine weiteren Pakete).
3. Änderungen committen.

## Vorschau und Veröffentlichung

- **Vorschau** (Standard): `python3 _quelle/build.py`. Jede Seite trägt `noindex` und `robots.txt` sperrt alle Suchmaschinen. So macht die Vorschau der alten Seite keine Konkurrenz.
- **Livegang**: `python3 _quelle/build.py --live` erzeugt dieselben Seiten ohne Sperre. Danach alles außer `_quelle/`, `README.md` und `.git` per SFTP in den Webspace-Ordner von umi-stuttgart.de bei Host Europe laden. Vorher die alte WordPress-Installation sichern.

## Vor dem Livegang offen

- Preise nach Freigabe in `config.py` eintragen
- Link zum Gutschein-Shop in `config.py` (`GUTSCHEIN_SHOP`)
- Doctolib: ein Profil für alle Knöpfe bestätigen
- Öffnungszeiten (heute widersprüchlich: Fr bis 16:30 oder 12:00)
- Fotos der Räume und fehlende Teamfotos ergänzen
- Impressum, Datenschutz und Gutscheinbedingungen rechtlich prüfen lassen
- Bei Einbau von Analytics: Cookie-Banner mit Consent Mode und Datenschutz ergänzen
