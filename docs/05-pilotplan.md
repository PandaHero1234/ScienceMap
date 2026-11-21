# Pilotplan für Process Mining

**Vorgeschlagener Pilot für Process Mining.** Ziel ist zu klären, wie gut sich der in einer Publikation berichtete F-Score-Vorteil von Split Miner gegenüber Inductive Miner nachvollziehen und übertragen lässt. Der Ausgangspunkt ist Tabelle 4 der Autorenfassung von Augusto et al. Die folgenden Kriterien sind ein Vorschlag für den Atlas. [Paper](https://doi.org/10.1007/s10115-018-1214-x) · [Autorenfassung mit Tabelle 4](https://kodu.ut.ee/~dumas/pubs/SplitMinerKAIS.pdf)

| Meilenstein | Vorab vereinbartes Kriterium | Stand dieses Entwurfs |
|---|---|---|
| 1. Ausgangsbefund belegen | Zwei Personen gleichen Metrik, Log, Parameter und beide Vergleichswerte mit der Tabelle ab. | Werte und Fundstelle erfasst, Zweitprüfung offen. |
| 2. Rechnung reproduzieren | Eine andere Person erhält mit ursprünglichen Daten, Implementierungen und Einstellungen beide Werte auf die publizierte Genauigkeit. Artefakte und Laufprotokoll sind verlinkt. | Eigener Rechenlauf offen. |
| 3. Übertragbarkeit testen | Auf drei vorab ausgewählten, voneinander unabhängigen Datenquellen wird der F-Score-Unterschied samt Unsicherheit und vorab vereinbarter Auswertung berichtet. | Auswahl und Test offen. |
| 4. Geltungsbereich bestimmen | Die Synthese beurteilt, unter welchen Logeigenschaften und Parametern sich die Rangfolge hält oder ändert. Sie benennt Abweichungen und methodische Grenzen. | Synthese offen. |

Meilenstein 3 verlangt einen aussagekräftigen Test. Auch ein präzises Nullergebnis kann diesen Meilenstein erfüllen. Die Karte zeigt dann etwa „Übertragbarkeit untersucht“ und daneben „Vorteil auf neuen Logs nicht nachweisbar“. Für ein anderes Ziel, etwa den Nachweis eines bestimmten Effekts, kann das vorher definierte Kriterium ausdrücklich einen Effekt bestimmter Größe verlangen.

## Umfang und Abnahme

1. Ein Pilotfeld **Process Mining** und ein klar abgegrenztes Ziel auswählen. Drei bis fünf Meilensteine und zehn bis fünfzehn prüfbare Aussagen vor der Literatursichtung als ersten Katalog festlegen.
2. Zu Beginn etwa fünfzehn bis fünfundzwanzig einschlägige Papers sichten. Suchdatum und Auswahl dokumentieren. Ein Gegenbefund oder eine Einschränkung erhält dieselbe Detailtiefe wie ein bestätigendes Ergebnis.
3. Eine Zielseite, eine Evidenzmatrix und den Änderungsverlauf veröffentlichen. Der Pilot ist technisch abgenommen, wenn jede Zahl bis zu den zugrunde liegenden Entscheidungen und Fundstellen nachvollziehbar ist.
4. Mit einer zweiten fachkundigen Person eine gemeinsame Stichprobe unabhängig bewerten. Abweichungen in den Regeln ausräumen. Anschließend die Physik-Beispiele als Test für das nächste Fachprofil verwenden.

**Erfolgskriterium für den Pilotbetrieb.** Eine außenstehende Person kann von der Startseite aus eine Aussage auswählen, die Tabelle oder Passage im Original finden, die Bewertung nachvollziehen und einen begründeten Einwand einreichen. Das ist ein überprüfbarer erster Release.

## Verbindung mit dem Event Log Catalog

Jeder verwendete Log erhält eine stabile Datensatz-ID sowie einen Verweis auf Quelle, Version und Vorverarbeitung. Verschiedene Ausschnitte desselben Rohlogs verweisen auf dieselbe Herkunft. Für Meilenstein 3 wird die Auswahl der unabhängigen Datenquellen vor dem Vergleich festgehalten. So lässt sich später nachvollziehen, welche zusätzlichen Prozessumgebungen der Test tatsächlich abdeckt.

