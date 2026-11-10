# Architektur-Review – Personal AI Running Coach

**Stand:** 2026-11-10 · **Grundlage:** `architecture.drawio`, `Project_idea.pdf`, `AI_HAI-Presentation.pptx`

## Gesamturteil

Der Stack ist für einen Prototyp gut gewählt: lokal, wenig bewegliche Teile, SQLite + FastAPI + Ollama, PWA über Tailscale. Die Grundsatzentscheidungen tragen. Die Schwächen liegen nicht im Stack, sondern im **Datenfluss**. Das Diagramm zeigt die Komponenten, aber nicht den **Adaptions-Loop**, also genau das, was die LV-Regeln verlangen („Methode zur Anpassung an neue Information“).

## Was gut ist

- **Provider-neutraler `LLMClient`**: Modellvergleich und Cloud-Fallback hängen am selben Interface.
- **Konfidenz deterministisch statt vom LLM geschätzt**: ehrlich, erklärbar und testbar.
- **Cloud-Fallback hinter Feature-Flag mit PII-Filter, Payload-Dialog und Audit-Log**: starkes HAI-Element (Transparenz + Kontrolle).
- **SQLite + SQLModel**: passend für einen Schreiber und eine Datei. Ein späterer Wechsel bleibt offen.
- **OpenAPI → TS-Client**: ein Vertrag zwischen Backend und Frontend, wenig Drift.

## Befunde im Diagramm

| # | Befund | Warum relevant | Vorschlag |
|---|--------|----------------|-----------|
| 1 | **Adaptions-Loop nicht sichtbar.** Ingest → DB und Profil-Updater → DB existieren, aber nichts verbindet „neue Session“ mit „Profil neu berechnen“ und „Plan neu planen“. | Kernanforderung der LV. In der Präsentation ist das das wichtigste Bild. | Eine nummerierte Kette einzeichnen: Log/Upload → Ingest → Profil-Updater → Planner → Guardrails → Plan + Begründung → PWA. |
| 2 | **Guardrails stecken im Planner-Kasten.** | Auch ein Plan-Änderungswunsch aus dem Chat (`plan_change`) muss durch die Guardrails. | Guardrails als eigene Komponente, die Planner *und* Chat-Router nutzen. Zusätzlich die Kante Chat-Router → Planner für `plan_change`. |
| 3 | **Chat-Router hat keine Verbindung zur DB.** | `chat_messages` muss gespeichert werden, und der Router braucht Profil/Historie als Kontext. | Kante Chat-Router ↔ SQLite. |
| 4 | **Planner liest kein Profil.** Die Pfeile laufen nur Planner → DB. | Reasoning-Input fehlt im Bild. | Pfeil bidirektional, oder Profil-Updater → Planner. |
| 5 | **Konfidenz-Berechnung und Erklärungs-/Diff-Erzeugung fehlen als Bausteine.** | Beide sind Pflicht-Outputs („wie sicher“, „warum geändert“). | Ein kleiner Kasten „Konfidenz + Change-Reasons (deterministisch)“ zwischen Profil-Updater und Planner. |
| 6 | **Offline-Logging (offene Entscheidung #6) hat keinen Platz.** | Der Laptop ist der Server. Ist er zu, kann am Handy nichts geloggt werden, und ein Lauf passiert genau dann, wenn man unterwegs ist. | In der PWA eine IndexedDB-Queue plus Sync beim nächsten Kontakt einzeichnen (gestrichelt, falls optional). Die Sync-Logik muss idempotent sein (Client-UUID pro Session). |
| 7 | **Cloud-Fallback nur aus dem Chat erreichbar.** | Das ist korrekt so, sollte aber explizit gesagt werden: Der Planner geht *nie* in die Cloud. | Das in der Legende vermerken, denn es ist ein gutes Privacy-Argument. |

## Risiken

| Risiko | Wahrscheinlichkeit | Wirkung | Gegenmaßnahme |
|--------|-------------------|---------|---------------|
| 7B-Modelle verletzen oft Guardrails, die Demo zeigt hauptsächlich den Fallback | Hoch (bei Option A) | Hoch | ADR-001: Hybrid-Planung mit Envelope |
| Latenz: Plan-JSON + Retries auf dem Laptop dauern 10–60 s | Mittel | Mittel | Planung asynchron nach dem Log (Job + Status), Chat per SSE streamen, Plan nicht streamen |
| LLM-Begründungen nennen Gründe, die nicht in den Daten stehen | Hoch | Hoch (HAI-Glaubwürdigkeit) | Gründe deterministisch berechnen, das LLM formuliert nur (ADR-001, Schritt 5) |
| Intent-Klassifikation durch das 7B-Modell ist unzuverlässig (z. B. Schmerz im Chat wird übersehen) | Mittel | Hoch | Schmerz-Keywords zusätzlich regelbasiert erkennen, vor dem LLM. Safety darf nicht nur am Classifier hängen |
| **Repo liegt in iCloud** (`~/Library/Mobile Documents/...`). Das eigene Dokument rät davon ab | Bereits eingetreten | Mittel (korruptes `.git`, Konflikt-Kopien, Sync von `node_modules`/`.venv`) | Repo nach `~/dev/running-coach` klonen, iCloud-Kopie nur für Dokumente nutzen |
| Folien widersprechen dem Stack (Streamlit, „nur Laptop“) | Sicher | Niedrig | Offene Entscheidung #7 abarbeiten, siehe ADR-001 Action Item 6 |

## Zu den offenen Entscheidungen

1. **Planungsansatz** → [ADR-001](adr/ADR-001-planungsansatz.md), Empfehlung Hybrid.
2. **Frontend:** React. Der Stack ist bereits darauf ausgelegt (shadcn/ui, TanStack Query), und es gibt mehr Beispiele für PWA + SSE.
3. **Externer Anbieter:** nachrangig, weil hinter `LLMClient` austauschbar. Erst in M2 entscheiden.
4. **Plan-Rhythmus:** fester Wochenplan, der nach jedem Log neu bewertet wird. Bereits gelaufene Tage sind eingefroren, nur der Rest der Woche wird angepasst. Das kombiniert das verständliche UI eines Wochenplans mit echter Adaption, ohne den Overhead eines rollierenden Plans.
5. **Herzfrequenz:** importieren und speichern, wenn vorhanden, aber nicht für die Planung nutzen (die Datenlage ist bei Personas und Usern uneinheitlich). Höchstens als Plausibilitäts-Check gegen RPE.
6. **Offline-Logging:** für M1 ein einfaches Formular mit IndexedDB-Queue. GPX/FIT-Upload erst bei Verbindung.
7. **Folien:** nach der Bestätigung von ADR-001 aktualisieren.

## Nächste Schritte

1. ADR-001 in der Gruppe entscheiden.
2. `architecture.drawio` um Befunde 1–6 ergänzen.
3. Repo aus iCloud nach `~/dev/running-coach` verschieben und die Monorepo-Struktur `backend/`, `frontend/` mit `.gitignore` anlegen.
4. Schemas (`Envelope`, `WeeklyPlan`, `SessionLog`, `ChangeReason`) als Erstes definieren, denn alles andere hängt daran.
