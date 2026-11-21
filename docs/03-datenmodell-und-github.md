# Datenmodell und Aufbau auf GitHub

| Pfad | Zweck |
|---|---|
| `README.md` | Einstiegsseite mit Stand, Aufruf und Links zur Methodik |
| `docs/` | Regeln für Aufnahme, Suche und Bewertung, Beispielkarten, Pilotplan und Nachweis |
| `data/goals/` | Feld, Ziel, versionierter Katalog mit stabilen Meilenstein-IDs und Erfüllungskriterien |
| `data/claims/` | Präzise Aussagen, Geltungsbereich und Zuordnung zu einem oder mehreren Meilensteinen |
| `data/studies/` | Studie, Team, Fassungen mit Link sowie Vermerk bei Korrektur oder Rückzug |
| `data/datasets/` | Grundlagen mit stabiler ID: Datensätze, Ereignisse, Versuchsreihen, klinische Studien und Beweise |
| `data/evidence/` | Einzelbefunde und ihre gerichteten Beziehungen zu Aussagen, mit Fundstellen und Datensatz-IDs |
| `data/decisions/` | Datierte Bewertungen mit Begründung, Prüfenden, Beleg-IDs und Verweis auf die frühere Entscheidung |
| `schemas/` | Ein JSON Schema je Datensatzart |
| `scripts/` | `atlas.py` prüft und wertet aus, `render.py` erzeugt die Seiten |
| `atlas.yaml` | Titel, Adresse des Repositorys und Fachprofile mit eigenen Bezeichnungen je Fach |
| `tests/` | Ein Test je Regel dieser Dokumentation |
| `.github/` | Vorlagen für neue Belege und Einwände, automatisierte Prüfung und Veröffentlichung |

**Veröffentlichungsweg.** Ein Beitrag beginnt als Issue oder Pull Request. Der Workflow „Daten prüfen“ prüft Pflichtfelder, eindeutige IDs, gültige Verweise, Quellenangaben und unzulässige Doppelzählungen. Ein fachliches Review entscheidet über Änderungen. Nach dem Merge auf `main` erzeugt `scripts/atlas.py build` aus den freigegebenen Entscheidungen `progress.json`, `history.json` und die Seiten. Der Workflow „Übersicht veröffentlichen“ stellt sie auf GitHub Pages bereit. Für einen späteren Anschluss an den Event Log Catalog genügen zunächst gemeinsame Datensatz-IDs und Links.

## Schlüsselwerte

Die Dateien verwenden feste Schlüsselwerte ohne Umlaute. Die Seiten zeigen die lesbare Form.

| Angabe | Feld | Schlüsselwerte |
|---|---|---|
| Beziehung von Beleg und Aussage | `relation` | `stuetzt` · `spricht_dagegen` · `nicht_entscheidend` |
| Prüfvermerk am Beleg | `review_status` | `vorgeschlagen` · `in_pruefung` · `freigegeben` · `erneut_zu_pruefen` |
| Stand einer Entscheidung | `status` | `vorgeschlagen` · `in_pruefung` · `freigegeben` |
| Ergebnis zu einem Meilenstein | `outcome` | `erreicht` · `nicht_erreicht` |
| Evidenzlage zu einer Aussage | `outcome` | `offen` · `vorlaeufig_gestuetzt` · `mehrfach_gestuetzt` · `widerspruechlich` · `spricht_dagegen` |
| Art der Absicherung | `assurance` | `quellenabgleich` · `nachrechnung` · `neue_daten` · `anderes_team` · `anderes_instrument` · `beweisreview` |

Der redaktionelle Stand einer Aussage wird berechnet. Ohne gültige Entscheidung lautet er „vorgeschlagen“ oder „in Prüfung“, mit gültiger Entscheidung „freigegeben“. Er wechselt auf „erneut zu prüfen“, sobald ein Beleg hinzukommt, den die gültige Entscheidung nicht nennt, oder eine zitierte Studie nach dem Entscheidungsdatum korrigiert oder zurückgezogen wurde.

## Beleg

Dieser Beleg liegt so in `data/evidence/`. Er ist ein Entwurf vor der fachlichen Zweitprüfung.

```yaml
id: ev-splitminer-bpic12-fscore
claim_id: cl-splitminer-bpic12-fscore
study_id: augusto-split-miner-journal
study_version: autorenfassung
locator: Tabelle 4, BPIC12, Zeilen SM und IM
dataset_id: bpic12
conditions: Standardparameter der Studie
metric: F-Score aus Fitness und Precision
values:
  split_miner: 0.88
  inductive_miner: 0.66
uncertainty: offen
relation: stuetzt
review_status: vorgeschlagen
```

Ein Beleg nennt seine Grundlage: einen Datensatz (`dataset_id`), Ereignisse (`event_ids`) oder allgemein eine Liste in `basis_ids`, etwa einen Beweis, eine Versuchsreihe oder die Registernummer einer klinischen Studie. Jede Grundlage hat einen Eintrag unter `data/datasets/` mit dem Feld `kind`. Ein Ausschnitt eines Rohlogs verweist dort mit `derived_from` auf seine Herkunft und zählt als dieselbe Grundlage.

Ein freigegebener Beleg nennt in `extracted_by` und `reviewed_by` zwei verschiedene Personen. Schlägt ein Sprachmodell einen Beleg oder eine Entscheidung vor, steht es in `suggested_by`. Dieses Feld zählt für die Freigabe nicht. Ein Beleg aus einer zurückgezogenen Studie bleibt sichtbar und zählt nicht mehr als Stütze.

## Entscheidung

Eine Entscheidung bewertet entweder einen Meilenstein oder eine Aussage. Nur freigegebene Entscheidungen verändern Zähler und Verlauf. Vorschläge erscheinen auf den Seiten als Vorschlag und im Balken schraffiert. Die ID einer Entscheidung enthält die vollständige ID ihres Gegenstands, etwa `dec-2026-11-21-ms-gw-erstnachweis`. Das folgende Beispiel zeigt die Form. Im Pilot liegt noch keine Entscheidung vor.

```yaml
id: dec-2026-12-01-ms-bpic12-quellenabgleich
date: 2026-12-01
kind: meilenstein          # oder: aussage
target_id: ms-bpic12-quellenabgleich
catalog_version: 1
outcome: erreicht
assurance: [quellenabgleich]
rationale: Beide Personen fanden Metrik, Log, Parameter und beide Werte in Tabelle 4.
extracted_by: Erste Person
reviewed_by: Zweite Person
evidence_ids: [ev-splitminer-bpic12-fscore]
status: freigegeben
# supersedes: dec-…       # ID der Entscheidung, die diese ersetzt
```

Eine neue Bewertung nennt in `supersedes` ihre Vorgängerin. Die alte Datei bleibt unverändert im Repository und erscheint im Verlauf. Ersetzen zwei Entscheidungen dieselbe Vorgängerin, liegt ein Konflikt vor. Gültig bleibt dann die Vorgängerin. Eine klärende Entscheidung nennt beide in `supersedes` als Liste und löst den Konflikt auf.

## Wie die Einträge zusammenhängen

Ein Forschungsziel enthält einen versionierten Meilensteinkatalog. Eine Aussage kann zu mehreren Meilensteinen beitragen. Eine Studie kann mehrere Befunde liefern, bei Bedarf zu unterschiedlichen Aussagen. Dafür erhält jede Zuordnung von Fundstelle und Aussage einen Belegeintrag. In einer Entscheidung verweisen die Prüfenden auf die betreffenden Beleg-IDs und den früheren Bewertungsstand.

| Datensatz | Beispiel | Wofür die ID gebraucht wird |
|---|---|---|
| Ziel | `goal-discovery-fscore` | Identifiziert den Katalog für den Methodenvergleich |
| Meilenstein | `ms-bpic12-quellenabgleich` | Definiert das Kriterium für den publizierten Ausgangsbefund |
| Aussage | `cl-splitminer-bpic12-fscore` | Bezeichnet genau den Vergleich auf BPIC12 mit Standardparametern |
| Studie | `augusto-split-miner-journal` | Verbindet Literaturangabe und benutzte Fassung |
| Datensatz | `bpic12` | Macht wiederverwendete Daten über mehrere Studien hinweg erkennbar |
| Beleg | `ev-splitminer-bpic12-fscore` | Verbindet Tabelle 4 der Originalarbeit mit der Aussage |
| Entscheidung | `dec-2026-12-01-ms-bpic12-quellenabgleich` | Hält fest, wer wann was mit welcher Begründung eingestuft hat |

Die ID jeder Datei entspricht ihrem Dateinamen.

## Prüfungen beim Erzeugen der Übersicht

- Ein Verweis auf eine unbekannte Studien-, Aussage-, Datensatz-, Beleg- oder Meilenstein-ID stoppt die Aktualisierung. Die bisherige Übersicht bleibt stehen.
- Jede freigegebene Entscheidung nennt die Begründung, das Prüfdatum, zwei verschiedene Personen, die Art der Absicherung und ihre Beleg-IDs. Die genannten Belege sind selbst freigegeben und gehören zum bewerteten Gegenstand.
- Die Evidenzlage passt zu den Belegen, auch bei einem Vorschlag. „Evidenz spricht dagegen“ braucht einen Gegenbeleg, „widersprüchlich“ braucht beide Richtungen.
- Mehrere Publikationen mit derselben Datensatz- oder Ereignis-ID bleiben als Quellen sichtbar. Die Auswertung zählt die zugrunde liegende Beobachtung einmal. „Mehrfach gestützt“ verlangt mindestens zwei stützende Belege auf zwei verschiedenen Grundlagen. Ein gemeinsames Team oder Instrument wird angezeigt.
- Liegen zwei widersprechende Nachfolgeentscheidungen vor, bleibt die letzte eindeutige Freigabe gültig, bis eine klärende Entscheidung beide ersetzt. Die Übersicht zeigt den Konflikt an.

Der Nachweis zu jeder dieser Regeln steht in [Nachweis](06-nachweis.md).
