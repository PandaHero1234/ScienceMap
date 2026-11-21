# Fortschritt und Aufbau der Übersicht

| Ansicht | Inhalt | Beispiel oder Frage |
|---|---|---|
| Startseite | Zuerst das Ganze: Gesamtstand mit Balken, Karte aus Kacheln, Tabelle je Fach und Ziel und die fehlende Arbeit. Darunter je Forschungsziel eine Route aus Meilenstein-Stationen mit Suche und Fachfilter | Wie weit ist der Atlas insgesamt, und wo steht eine Prüfung an? |
| Zielseite | Die Route senkrecht: je Meilenstein Erfüllungskriterium, Status, Begründung und die verknüpften Aussagen im Wortlaut | Welche Evidenz fehlt für die Übertragbarkeit eines Verfahrens? |
| Aussage | Präziser Satz mit Geltungsbereich, drei Angaben zur Einordnung, einer Matrix aus Quellen und ihren Grundlagen sowie den Belegen, getrennt nach Richtung | Für welche Logversion und Parameter gilt der gemessene Vorsprung? |
| Beleg | Konkretes Ergebnis aus einer Arbeit, genaue Fundstelle, Version, Datenherkunft und Prüfvermerk | Welche Zeilen in welcher Tabelle tragen den Vergleich? |
| Offene Prüfungen | Jeder Beleg und jede Einstufung ohne Freigabe, nach Ziel geordnet, mit direktem Weg zur Datei im Repository | Was kann ich als zweite Person heute prüfen? |
| Verlauf | Alter und neuer Status, Datum der wissenschaftlichen Veröffentlichung, Datum der Atlasentscheidung, Grund und Quelle | Kam ein neuer Datensatz hinzu, wurde ein Messfehler gefunden oder hat sich der Zielkatalog erweitert? |

**Die Zähleinheit ist der vorab definierte Meilenstein.** Die Route eines Ziels trägt einen lesbaren Nenner, etwa „2 von 4 Meilensteinen erreicht · Zielkatalog v1“ (fiktives Layoutbeispiel). Ein zweiter Wert wie „7 von 10 erfassten Aussagen geprüft“ beschreibt die Arbeit am Atlas. Ein neuer Meilenstein erhöht den Nenner und erhält einen eigenen Änderungseintrag. Unterschiedlich große Ziele behalten ihre eigenen Routen. Eine feldübergreifende Liste lässt sich nach Fach, offenen Fragen oder Änderungen durchsuchen.

## Zählregel für die Startseite

Der Nenner zählt die aktiven Meilensteine der gewählten Zielkatalog-Version. Jeder Meilenstein hat eine stabile ID und zählt höchstens einmal. Der Zähler enthält die Meilensteine, für die eine gültige, fachlich freigegebene Entscheidung das Erfüllungskriterium als erreicht einstuft. Ein Ziel ohne definierte Meilensteine erhält die Anzeige „Katalog offen“. Bei einer neuen fachlichen Bewertung bleiben ältere Stände mit ihrer damaligen Katalogversion abrufbar.

| Beispiel einer Zielzeile | Stand im Pilotentwurf |
|---|---|
| Fach und Ziel | Process Mining · F-Score-Vorteil von Split Miner nachvollziehen und seine Übertragbarkeit untersuchen |
| Meilensteine | **0 von 4** nach den vorgeschlagenen Freigabekriterien |
| Letzte dokumentierte Arbeit | Vergleichswerte und Fundstelle für BPIC12 erfasst |
| Nächste offene Prüfung | Zweite Person prüft die Zeilen für beide Verfahren und die verwendete Metrik |

Die Anzeige bezieht sich auf die Arbeit an diesem Zielkatalog. Aus „0 von 4“ lässt sich keine Aussage zum gesamten Forschungsstand von Process Mining ableiten.


## Gesamtübersicht

Die Startseite beginnt mit dem Stand des ganzen Atlas. Sie folgt dem Aufbau der Fortschrittsseite von AnyPS5: Gesamtzahl, Karte, Tabelle, offene Arbeit, Verlauf und Abzeichen.

| Baustein | Inhalt |
|---|---|
| Gesamtstand | Erreichte von allen Meilensteinen als Zahl und Anteil, dazu geprüfte Aussagen, geprüfte Belege und offene Prüfungen. Ein Balken teilt alle Meilensteine nach Zustand |
| Rechnung | Ein Satz nennt, wo der Zähler stünde, wenn alle offenen Vorschläge freigegeben würden. Er ist als Rechnung gekennzeichnet und zählt nicht als Stand |
| Karte | Je Ziel eine Kachel für jeden Meilenstein, jede Aussage und jeden Beleg. Jede Kachel führt zu ihrem Eintrag |
| Tabelle | Je Ziel und gesamt: erreichte und vorgeschlagene Meilensteine, geprüfte Aussagen und geprüfte Belege |
| Was noch fehlt | Meilensteine, die auf die Zweitprüfung warten, Meilensteine ohne Vorschlag und Aussagen, die erneut zu prüfen sind |
| Verlauf | Erreichte Meilensteine über die Zeit als Linie, die Zahl der Meilensteine im Katalog gestrichelt. Die Kurve erscheint ab zwei Tagen mit Änderungen |
| Abzeichen | `badge.svg` mit dem Gesamtstand und ein Abzeichen je Fach, etwa `badge-physik.svg`, zum Einbinden in andere Seiten |

Dieselben Zahlen stehen in `progress.json` unter `totals`, `fields` und `series`.

## Gestaltung der Seiten

Jede Station einer Route hat einen von fünf Zuständen: erreicht, als erreicht vorgeschlagen, offen, nicht erreicht und als nicht erreicht vorgeschlagen. Symbol und Text tragen die Bedeutung, die Farbe unterstützt sie nur. Ein Vorschlag ist immer gestrichelt gezeichnet und als Vorschlag beschriftet.

Titel und Aussagen stehen im Wortlaut auf den Seiten. Die technischen IDs erscheinen nur dort, wo Prüfende sie brauchen. Von jeder Aussage führt ein Weg zurück zu ihrem Meilenstein und Ziel.

Alle Inhalte stehen im HTML und sind ohne JavaScript lesbar. Suche, Fachfilter und der Wechsel zwischen hellem und dunklem Design kommen mit JavaScript hinzu. Die Seiten laden keine Schriften oder Skripte von fremden Servern.
