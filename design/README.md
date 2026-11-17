# Trainingscoach – Design-Übergabe

Design-Original (Canvas): https://claude.ai/artifact/RYT7ymMaHbVPJ6Q7VHvFUt

Die Dateien in `screens/` sind die Referenz für die Umsetzung. Sie sind im
Format des Design-Editors (`.dc.html`) und rendern **nicht** direkt im Browser.
Lies sie als Spezifikation: Struktur, Texte, Farben, Abstände und Verhalten
stehen vollständig als HTML mit Inline-Styles darin. Der `<script type="text/x-dc">`
-Block am Ende enthält jeweils die Interaktionslogik (State, Handler).

## Screens

| Datei | Gerät | Inhalt |
|---|---|---|
| `Main.dc.html` | Handy | Heute: Einheit des Tages, Begründung, Wochenleiste, Plan-Sicherheit |
| `Log.dc.html` | Handy | Lauf eintragen: GPX/FIT, Sprache, Werte, Anstrengung 1–10, Schmerzen |
| `Plan.dc.html` | Handy | Wochenplan mit Änderung des Coaches und Rückgängig |
| `Kraft.dc.html` | Handy | Vorgeschlagenes Krafttraining mit Begründungen pro Übung |
| `KraftLog.dc.html` | Handy | Krafttraining Satz für Satz eintragen, Reserve, Steigerungs-Feedback |
| `Coach.dc.html` | Handy | Chat mit Begründungen, Plan-Vorschlag annehmen/ablehnen |
| `Freigabe.dc.html` | Handy | Bestätigung vor externer Anfrage (exakter Inhalt, entfernte Daten) |
| `Verlauf.dc.html` | Handy | km pro Woche, Belastungsskala, letzte Läufe |
| `WebHeute.dc.html` | Laptop/PC | Heute mit Seitennavigation und dauerhaftem Coach-Panel |
| `WebKraft.dc.html` | Laptop/PC | Krafttraining als Tabelle mit Eingaben pro Satz, Verlauf, Regeln |

`canvas.json` zeigt nur die Anordnung auf der Canvas; für die App irrelevant.

## Design-Tokens

### Farben
| Token | Hex | Verwendung |
|---|---|---|
| `ground` | `#EEF0EB` | Seitenhintergrund (kühles Kalkstein-Grau) |
| `surface` | `#FFFFFF` | Karten, Listen, Navigation |
| `ink` | `#17302A` | Text, dunkle Buttons (Fichtengrün) |
| `ink-soft` | `#2B3F39` | Fließtext in Karten |
| `muted` | `#56635E` | Nebentexte, Labels |
| `line` | `#D5DBD3` / `#E3E7E1` | Rahmen, Trennlinien |
| `field-border` | `#C9D0C7` | Eingabefelder, Sekundär-Buttons |
| `marker` | `#C8102E` | **Einziger Akzent**: Hauptbutton, „heute“, Logo (rot-weiß-rot) |

### Trainingsarten (semantisch, je Typ fest)
| Typ | Voll (erledigt) | Hell (geplant) |
|---|---|---|
| Locker | `#B9CC85` | `#E6EDD3` + Rand `#B9CC85` |
| Tempo | `#D9A441` | `#F5E7C6` + Rand `#D9A441` |
| Intervalle | `#C8102E` | – |
| Lang | `#2F5D50` | `#D3E0DC` + Rand `#2F5D50` |
| Kraft | `#5C7186` | `#DDE3EA` + Rand `#5C7186`, Hantel-Symbol |

Laufeinheiten sind Balken (Höhe = km), Krafteinheiten quadratische Blöcke.

### Status
| Zweck | Hintergrund | Text |
|---|---|---|
| Warnung / Schmerz / Knie | `#FFF1DD` | `#7A3A05` |
| Plan geändert | `#FBF0D9` | `#4A3D24` |
| Positiv / Steigerung | `#E6EDD3` | `#2F4A1A` |
| Vorschlag-Rahmen | Rand `#D9A441` | Titel `#6B4A00` |

### Typografie
- **Barlow Condensed** (Google Fonts, 500/600/700): Überschriften, alle Zahlen
  (km, kg, Pace). Heute-Titel Handy 76px, Web 104px; Seitentitel 44px.
- **System-Schrift** (`system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif`):
  Fließtext 15px, Nebentext 13px, Labels 12–14px.
- Zahlen in Spalten mit `font-variant-numeric: tabular-nums`.
- Satzschreibung, keine Großbuchstaben-Labels.

### Formen und Abstände
- Radien: Karten 16px, Buttons 12–14px, Chips 10–22px, Balken 6–8px.
- Seitenrand Handy 20px, Web 32px, Inhalt max. 1180px breit.
- Tap-Ziele mindestens 44 × 44 px.
- Fokus: `outline: 3px solid #C8102E; outline-offset: 2px`.
- Keine Schatten, keine Verläufe.

## Layout-Regeln
- **Eine App, responsive**: unter ca. 900px Tab-Leiste unten (Heute, Plan,
  Coach, Verlauf); darüber Seitennavigation links (+ Krafttraining) und
  Coach-Panel rechts.
- Hauptaktion pro Screen als roter Button, am Handy unten fixiert.
- Krafttraining-Eintragen am Handy ohne Tab-Leiste (Fokus-Modus).

## Verhalten, das umgesetzt werden muss
- Anstrengung 1–10 mit Beschreibungstext je Stufe (siehe `Log.dc.html`).
- Schmerzen: Ja/Nein, bei Ja Körperstellen als Mehrfachauswahl.
- Plan-Änderung rückgängig machen und wieder übernehmen (`Plan.dc.html`).
- Coach-Vorschlag: Übernehmen / Ablehnen mit Bestätigungstext.
- Satz-Eingabe mit +/- für Gewicht (2,5 kg) und Wiederholungen, Reserve 0–4+.
- Steigerungsregel nach dem letzten Satz: alle Sätze volle Wiederholungen und
  Reserve ≥ 1 → nächstes Mal +2,5 kg, sonst gleiches Gewicht.
- Externe Anfrage nur nach Bestätigung, mit exakt angezeigtem Inhalt.
