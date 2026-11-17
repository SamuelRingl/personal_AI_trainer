# Prompt für Claude Code

In Claude Code im Repo-Ordner im Plan-Modus (Shift+Tab) einfügen:

---

Setze das Design aus `design/` als Frontend im Ordner `frontend/` um.
Lies zuerst `design/README.md` und dann alle Dateien in `design/screens/`.
Die `.dc.html`-Dateien sind die Spezifikation: übernimm Struktur, Texte,
Farben, Abstände und Verhalten möglichst genau. Sie rendern nicht direkt im
Browser, kopiere also kein Markup 1:1, sondern baue saubere React-Komponenten.

Stack: React + Vite + TypeScript, Tailwind CSS, shadcn/ui, TanStack Query,
react-router, vite-plugin-pwa. Kein Next.js.

Anforderungen:
- Design-Tokens aus der README zentral in der Tailwind-Config.
- Barlow Condensed über Google Fonts, sonst System-Schrift.
- Eine responsive App: Handy-Layout mit Tab-Leiste, ab ca. 900px
  Seitennavigation links und Coach-Panel rechts (siehe Web-Screens).
- Wiederverwendbare Komponenten: Wochenleiste, Belastungsskala,
  Übungsliste, Satz-Eingabe, Coach-Nachricht, Vorschlagskarte,
  Bestätigungsdialog für externe Anfragen.
- Daten vorerst als typisierte Mock-Daten in `src/mocks/`. API-Aufrufe
  später gegen FastAPI unter `/api`: Vite-Proxy bereits einrichten.
- Barrierefreiheit wie im Design: echte Buttons und Labels, sichtbarer
  Fokus, Tap-Ziele ≥ 44px.

Vorgehen: Zeig mir zuerst den Plan (Ordnerstruktur, Komponenten, Routen).
Danach Screen für Screen umsetzen, ein Commit pro Screen.
