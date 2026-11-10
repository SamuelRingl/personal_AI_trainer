# ADR-001: Planungsansatz – wer erzeugt den Wochenplan?

**Status:** Proposed
**Date:** 2026-11-10
**Deciders:** Felix Walter, Samuel Ringl, Lukas Herk

## Context

Offene Entscheidung #1 aus `Project_idea.pdf`, muss vor M1 (15.12.2026) fallen.

Kräfte:

- **LV-Regeln:** Die KI muss Perception, Reasoning und Action zeigen und sich an neue Information anpassen. Das LLM soll dabei sichtbar mehr sein als ein Textgenerator.
- **Sicherheit:** Ein Plan darf nie gegen die Guardrails verstoßen (+10 % Umfang, Ruhetag, keine zwei harten Einheiten hintereinander, Long Run ≤ 30 %, Schmerz → Last runter).
- **Modelle:** 7–8B-Modelle lokal über Ollama. Bei Arithmetik (Kilometer summieren, Prozente) und beim Einhalten mehrerer harter Constraints gleichzeitig sind sie unzuverlässig. Bei einer Verletzung gibt es max. 2 Retries, danach einen deterministischen Fallback-Plan.
- **Erklärbarkeit:** Die App muss erklären, *warum* sich der Plan geändert hat und wie sicher sie ist. Die Konfidenz wird bereits deterministisch berechnet.
- **Tests:** Personas × 8 Wochen × 3 Modelle. Gemessen werden JSON-Validität, Guardrail-Verletzungen, Latenz und Erklärungsqualität.
- **Wichtig:** Der deterministische Fallback-Plan ist ohnehin eingeplant. Ein algorithmischer Planer muss also in jeder Variante gebaut werden.

## Decision

**Option C (Hybrid) wird vorgeschlagen:** Ein deterministischer Planer berechnet aus dem Profil einen **Rahmen** (Envelope) und einen gültigen Default-Plan. Das LLM **verteilt und variiert** die Einheiten innerhalb dieses Rahmens und begründet seine Wahl. Die Guardrails prüfen das Ergebnis. Nach 2 Fehlversuchen wird der Default-Plan ausgeliefert.

## Options Considered

### Option A: LLM plant, Guardrails prüfen (Stand der Folien)

| Dimension | Assessment |
|-----------|------------|
| Complexity | Mittel. Prompt-Engineering und Retry-Loop sind viel Tuning-Arbeit |
| Cost / Latenz | Hoch. Ganzer Plan als JSON, im Fehlerfall bis 3 Calls |
| Robustheit | Niedrig. 7B-Modelle verletzen Summen- und Prozent-Constraints häufig |
| HAI-Story | Stark. Das LLM ist sichtbar „der Coach“ |

**Pros:** Entspricht den Folien. Maximale Flexibilität. Das LLM kann Chat-Wünsche („Dienstag keine Zeit“) direkt einbauen.
**Cons:** Hohe Fallback-Quote ist zu erwarten, dann sieht der User oft den Fallback statt den „KI-Plan“. Die Begründung kann halluziniert sein (das LLM nennt Gründe, die nicht in den Daten stehen). Schwer testbar.

### Option B: Algorithmus plant, LLM erklärt nur

| Dimension | Assessment |
|-----------|------------|
| Complexity | Niedrig |
| Cost / Latenz | Niedrig. Ein Call nur für den Text |
| Robustheit | Hoch. Guardrails gelten per Konstruktion |
| HAI-Story | Schwach. Das LLM ist nur Formulierer, „Reasoning“ steckt im Regelcode |

**Pros:** Sicher, deterministisch und einfach zu testen.
**Cons:** Das Reasoning der KI ist kaum noch LLM-basiert. Das ist im LV-Kontext angreifbar, und die Präsentation müsste umgeschrieben werden. Chat-Wünsche lassen sich nur über vordefinierte Parameter umsetzen.

### Option C: Hybrid – Algorithmus setzt Rahmen, LLM füllt aus (empfohlen)

| Dimension | Assessment |
|-----------|------------|
| Complexity | Mittel. Der Algorithmus wird für den Fallback ohnehin gebaut |
| Cost / Latenz | Mittel. Kleinere, enger gefasste JSON-Ausgabe |
| Robustheit | Hoch. Die harten Zahlen kommen vom Code, das LLM wählt nur innerhalb erlaubter Werte |
| HAI-Story | Gut. Das LLM trifft echte Entscheidungen (Verteilung, Einheitentyp, Reaktion auf Chat/RPE) und erklärt sie |

**Ablauf:**

1. `Profil-Updater` → Wochenumfang, ACWR, RPE-Trend, Schmerz-Zähler.
2. `Envelope` (deterministisch): Ziel-km (≤ +10 %), max. Long Run, Anzahl Lauftage, max. harte Einheiten, Pflicht-Ruhetage, Sperrtage aus Constraints/Chat. Dazu ein gültiger **Default-Plan**.
3. LLM bekommt Envelope + Default + letzte Sessions + Chat-Wünsche und gibt Plan-JSON nach Schema aus (Ollama `format` mit JSON-Schema). Pro Einheit erlaubte Typen sind Enums.
4. Guardrails validieren. Bei Verletzung bekommt das LLM die konkrete Verletzung zurück (max. 2×), danach Default-Plan.
5. **Begründung:** Der Diff „alter Plan → neuer Plan“ und die auslösenden Kennzahlen werden deterministisch als `reasons[]` berechnet. Das LLM formuliert daraus den Text. So bleibt die Erklärung an echte Daten gebunden.

**Pros:** Es wird nur ein Planer-Algorithmus gebaut, der Envelope- und Fallback-Lieferant zugleich ist. Die Fallback-Quote sinkt deutlich. Die Erklärungen sind überprüfbar. Option A bleibt als Experiment möglich: man lässt das LLM ohne Envelope planen und vergleicht in den Persona-Tests.
**Cons:** Zwei Planer-Pfade, die konsistent bleiben müssen. Es muss klar definiert werden, was das LLM entscheiden darf. Wenn der Rahmen zu eng ist, wird das LLM zum reinen Formatierer (Option B durch die Hintertür).

## Trade-off Analysis

Die zentrale Spannung liegt zwischen **sichtbarer KI-Leistung** (für die LV) und **Zuverlässigkeit** (für den User und die Tests). Option A optimiert das Erste und riskiert, dass in der Demo oft der Fallback greift. Option B optimiert das Zweite und schwächt das Reasoning-Argument. Option C verschiebt die Grenze so, dass Zahlen dem Code gehören und Entscheidungen dem LLM. Das passt zu den Stärken eines 7B-Modells: Sprache, Abwägen, Kontext aus dem Chat. Die Schwächen (Arithmetik, viele harte Constraints gleichzeitig) übernimmt der Code.

Für die Persona-Tests bietet C außerdem einen sauberen Vergleich: die Guardrail-Verletzungsrate von *LLM frei* (A) gegen *LLM im Envelope* (C) pro Modell. Daraus wird eine interessante Ergebnisfolie.

## Consequences

- **Einfacher:** Tests (der Default-Plan ist deterministisch und als Snapshot testbar), Demo-Stabilität, Erklärungen ohne Halluzination, Modellwechsel.
- **Schwieriger:** Envelope-Schema und Plan-Schema müssen früh und gemeinsam definiert werden (Backend und Frontend hängen daran).
- **Neu zu klären:** Was passiert, wenn der User im Chat etwas verlangt, das den Envelope sprengt („nächste Woche 60 km“)? Vorschlag: Der Router markiert das als `plan_change`, der Envelope bleibt hart, und das LLM erklärt die Ablehnung.
- **Revisit:** Nach den ersten Persona-Läufen. Ist die Verletzungsrate im freien Modus nahe 0, kann der Envelope gelockert werden.

## Action Items

1. [ ] Gruppe bestätigt Option C (oder entscheidet anders) und setzt Status auf *Accepted*.
2. [ ] Pydantic-Schemas definieren: `Envelope`, `WeeklyPlan`, `PlannedSession`, `ChangeReason`.
3. [ ] Deterministischen Planer + Guardrails in Python implementieren, mit pytest-Fällen für jede Guardrail.
4. [ ] Prompt + Ollama-Structured-Output für die drei Modelle aufsetzen und die JSON-Validität messen.
5. [ ] Persona-Testharness mit Modus `free` vs. `envelope` als Parameter.
6. [ ] Folien anpassen (Reasoning-Folie: „Algorithmus setzt Rahmen, LLM entscheidet innerhalb“).
