# Fortschritt und Aufbau der Übersicht

| Ansicht | Inhalt | Beispiel oder Frage |
|---|---|---|
| Startseite (Über-Atlas) | Das Ganze: Gesamtstand mit Balken, Karte aller Wissenschaften, Tabelle je Fachgebiet und die fehlende Arbeit | Wie weit ist der Atlas insgesamt, und welche Fachgebiete haben schon Einträge? |
| Bereich | Zwischenkarte eines der sechs Bereiche mit seinen Fachgebieten, auch denen ohne Einträge | Welche Naturwissenschaften sind schon erfasst? |
| Fachgebiet | Zwischenkarte eines Fachgebiets: Stand, seine Teilgebiete und die Tabelle je Ziel | Wie steht es in der Physik? |
| Teilgebiet | Zwischenkarte eines Teilgebiets: Stand, Karte der Einträge und die Ziele als Routen | Welche Ziele gibt es zur Genom-Editierung? |
| Alle Ziele | Karte aller Einträge und jedes Ziel als Route aus Meilenstein-Stationen. Suche und Fachfilter durchsuchen Ziele, Aussagen und Quellen | Wo kommt eine bestimmte Quelle vor? |
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

Die Startseite ist der Über-Atlas. Sie zeigt den Stand des Ganzen und folgt dem Aufbau der Fortschrittsseite von AnyPS5: Gesamtzahl, Karte, Tabelle, offene Arbeit, Verlauf und Abzeichen. Wie dort die Karte alle Bibliotheken zeigt, auch die unfertigen, zeigt hier die Karte alle Fachgebiete, auch die ohne Einträge.

| Baustein | Inhalt |
|---|---|
| Gesamtstand | Erreichte von allen Meilensteinen als Zahl und Anteil, dazu geprüfte Aussagen, geprüfte Belege und offene Prüfungen. Ein Balken teilt alle Meilensteine nach Zustand |
| Rechnung | Ein Satz nennt, wo der Zähler stünde, wenn alle offenen Vorschläge freigegeben würden. Er ist als Rechnung gekennzeichnet und zählt nicht als Stand |
| Karte der Wissenschaften | Alle 42 Fachgebiete der Systematik in 6 Bereichen. Ein Fachgebiet mit Einträgen zeigt seinen Stand und führt zu seinem eigenen Atlas, die übrigen sind als „noch kein Eintrag“ gezeichnet |
| Karte der Einträge | Auf der Seite eines Fachgebiets und unter „Alle Ziele“: je Ziel eine Kachel für jeden Meilenstein, jede Aussage und jeden Beleg. Jede Kachel führt zu ihrem Eintrag |
| Tabelle | Je Fachgebiet und gesamt, auf der Seite eines Fachgebiets je Ziel: erreichte und vorgeschlagene Meilensteine, geprüfte Aussagen und geprüfte Belege |
| Was noch fehlt | Meilensteine, die auf die Zweitprüfung warten, Meilensteine ohne Vorschlag, Aussagen, die erneut zu prüfen sind, und die Zahl der Fachgebiete ohne Eintrag |
| Verlauf | Erreichte Meilensteine über die Zeit als Linie, die Zahl der Meilensteine im Katalog gestrichelt. Die Kurve erscheint ab zwei Tagen mit Änderungen |
| Abzeichen | `badge.svg` mit dem Gesamtstand und ein Abzeichen je Fach, etwa `badge-physik.svg`, zum Einbinden in andere Seiten |

Dieselben Zahlen stehen in `progress.json` unter `totals`, `coverage`, `realms`, `fields` und `series`.

Die Gliederung liegt in `data/taxonomy.yaml` und folgt der Österreichischen Systematik der Wissenschaftszweige (ÖFOS 2012) mit 6 Hauptgruppen und 42 Gruppen. Jedes Ziel nennt im Feld `area` den Code seines Fachgebiets. Aus dem Anteil der Fachgebiete mit Einträgen lässt sich nicht ablesen, wie weit die Forschung dort ist. Er zeigt nur, wo der Atlas schon arbeitet.

## Ebenen: hinein und hinaus

Der Atlas hat sechs Ebenen. Jede Ebene ist eine eigene Karte mit demselben Aufbau.

| Ebene | Karte | Führt hinein zu |
|---|---|---|
| 1 | Über-Atlas mit allen Wissenschaften | den sechs Bereichen und ihren Fachgebieten |
| 2 | Bereich, etwa Naturwissenschaften | seinen Fachgebieten |
| 3 | Fachgebiet, etwa Biologie | seinen Teilgebieten |
| 4 | Teilgebiet, etwa Genom-Editierung | seinen Zielen |
| 5 | Ziel | seinen Meilensteinen und Aussagen |
| 6 | Aussage | den Belegen und von dort zur Fundstelle im Original |

Hinein geht es über die Felder und Kacheln der Seite. Hinaus führt oben auf jeder Seite ein Knopf zur nächsten äußeren Ebene. Daneben steht der ganze Weg nach außen, jede Ebene als Link, und die Angabe „Ebene 4 von 6“. Unten nennt jede Seite ihre Nachbarn auf derselben Ebene.

Das Teilgebiet eines Ziels steht im Feld `topic`. Fehlt es, gilt das Fach aus `field`. Auch ein Bereich ohne Einträge hat eine Karte. Sie zeigt seine Fachgebiete und sagt, dass noch nichts erfasst ist.

## Gestaltung der Seiten

Jede Station einer Route hat einen von fünf Zuständen: erreicht, als erreicht vorgeschlagen, offen, nicht erreicht und als nicht erreicht vorgeschlagen. Symbol und Text tragen die Bedeutung, die Farbe unterstützt sie nur. Ein Vorschlag ist immer gestrichelt gezeichnet und als Vorschlag beschriftet.

Titel und Aussagen stehen im Wortlaut auf den Seiten. Die technischen IDs erscheinen nur dort, wo Prüfende sie brauchen. Von jeder Aussage führt ein Weg zurück zu ihrem Meilenstein und Ziel.

Alle Inhalte stehen im HTML und sind ohne JavaScript lesbar. Suche, Fachfilter und der Wechsel zwischen hellem und dunklem Design kommen mit JavaScript hinzu. Die Seiten laden keine Schriften oder Skripte von fremden Servern.
