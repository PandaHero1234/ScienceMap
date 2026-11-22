# Forschungsatlas

[![Meilensteine](https://pandahero1234.github.io/ScienceMap/badge.svg)](https://pandahero1234.github.io/ScienceMap/)

**Zur Übersicht:** https://pandahero1234.github.io/ScienceMap/

Der Forschungsatlas zeigt für jedes Forschungsziel, welche Meilensteine erreicht sind, welche Veröffentlichungen diese Einschätzung tragen und welche Prüfung als Nächstes ansteht. Vom Stand eines Ziels führt ein direkter Weg zur konkreten Tabelle, Abbildung oder Textstelle im Paper.

**Stand vom 22. November 2026.** Der Weg von den Daten zur Übersicht ist gebaut und getestet. Die Startseite ist ein Über-Atlas mit allen 42 Fachgebieten der Wissenschaft, von denen 26 Einträge haben. Der Atlas enthält 32 Ziele in allen sechs Bereichen. Alle Einträge außerhalb des Pilots sind Vorschläge, deren Zweitprüfung aussteht. Für Process Mining sind vier Meilensteine formuliert. Der Ausgangsbefund ist mit seiner Fundstelle erfasst. Die fachliche Zweitprüfung, die unabhängige Nachrechnung und die Übertragungsstudie stehen aus.

Das Vorbild AnyPS5 erzeugt aus versionierten Daten eine Übersicht, Detailansichten und eine Änderungshistorie. Für die Wissenschaft braucht dieses Prinzip eine redaktionelle Entscheidung zwischen Paper und Fortschrittsanzeige. Ein neuer Artikel kann ein Ziel näherbringen, Zweifel aufwerfen oder die Gültigkeit eines älteren Ergebnisses eingrenzen. Alle drei Veränderungen verdienen einen Eintrag. [AnyPS5 – Progress Reporting](https://github.com/boykopovar/AnyPS5/blob/main/docs/dev/PROGRESS.md)

## Einstieg

Wer den Forschungsstand lesen möchte, beginnt mit der Übersicht und den Beispielkarten. Wer ein Paper beitragen will, verwendet die Beitragsvorlage. Für die technische Umsetzung bilden Datenmodell und Pilotplan den Einstieg.

- [Fortschritt und Aufbau der Übersicht](docs/01-uebersicht.md)
- [Papers prüfen und Evidenz bewerten](docs/02-paper-validierung.md)
- [Datenmodell und Aufbau auf GitHub](docs/03-datenmodell-und-github.md)
- [Beispielkarten mit Primärquellen](docs/04-beispiele.md)
- [Pilotplan für Process Mining](docs/05-pilotplan.md)
- [Nachweis: Was funktioniert und was offen bleibt](docs/06-nachweis.md)
- [Drei Fachgebiete als Prozesstest](docs/07-fachgebiete.md)
- [Ein Paper oder eine Korrektur beitragen](CONTRIBUTING.md)

## Ausführen

```bash
pip install -r requirements.txt
python scripts/atlas.py validate     # prüft die Daten unter data/
python -m pytest -q                  # prüft jede Regel der Dokumentation
python scripts/atlas.py build        # schreibt die Übersicht nach public/
```

Danach `public/index.html` im Browser öffnen. Die Daten liegen als YAML unter `data/`, die Regeln dazu stehen in [Datenmodell und Aufbau auf GitHub](docs/03-datenmodell-und-github.md).

