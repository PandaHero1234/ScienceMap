# Drei Fachgebiete als Prozesstest

**Stand vom 21. November 2026.** Der Atlas enthält je ein eng umrissenes Gebiet aus Physik, Mathematik und Biologie. Alle Einträge sind Vorschläge eines Sprachmodells. Kein Meilenstein gilt als erreicht, solange nicht zwei Personen die Belege und Einstufungen freigegeben haben.

| Fach | Gebiet | Meilensteine | Aussagen | Studien | Belege |
|---|---|---|---|---|---|
| Physik | Gravitationswellen von Verschmelzungen stellarer Schwarzer Löcher | 0 von 4 erreicht, 4 vorgeschlagen | 4 | 5 | 7 |
| Mathematik | Beschränkte Lücken zwischen Primzahlen | 0 von 5 erreicht, 4 vorgeschlagen | 3 | 3 | 5 |
| Biologie | Programmierbare Genom-Editierung mit CRISPR-Cas9 | 0 von 4 erreicht, 4 vorgeschlagen | 3 | 6 | 6 |
| Biologie | DNA-geführte Genom-Editierung mit NgAgo | 0 von 2 erreicht, 0 vorgeschlagen | 1 | 2 | 2 |

Die Gebiete sind so gewählt, dass jedes eine andere Regel des Atlas belastet.

- **Physik.** Drei Veröffentlichungen der Kollaboration berichten zwei Ereignisse. Der Atlas zeigt drei Quellen auf zwei Ereignissen und nennt Team und Instrument als gemeinsame Abhängigkeit. Die zweite Auswertung von GW150914 durch eine andere Gruppe zählt als weitere Quelle, aber nicht als neue Beobachtung.
- **Mathematik.** Die Grundlage eines Belegs ist hier ein Beweis. Zwei Beweise verschiedener Autoren stützen die endliche Schranke. Die Zwillingsprimzahlvermutung steht als fünfter Meilenstein ohne Beleg im Katalog. Eine Schranke unter einer unbewiesenen Vermutung steht als bedingte Aussage mit benannter Voraussetzung.
- **Biologie.** Drei Veröffentlichungen zu exa-cel stammen aus zwei registrierten klinischen Studien. Die Registernummern dienen als Grundlage und verhindern die Doppelzählung. Bei NgAgo ist die Erstveröffentlichung zurückgezogen. Sie bleibt sichtbar und zählt nicht mehr als Stütze.

## Wie die Einträge entstanden sind

Die bibliografischen Angaben und die Zahlenwerte wurden per Websuche mit den Abstracts in Literaturdatenbanken und Repositorien abgeglichen. Die Volltexte waren aus der Arbeitsumgebung nicht erreichbar. Die Fundstelle lautet deshalb fast überall „Abstract“. Tabelle, Abbildung oder Satznummer sind nachzutragen. Das steht im jeweiligen Beleg als Anmerkung.

Drei Angaben ließen sich nicht bestätigen und fehlen deshalb:

- die Editierungsraten je Zelltyp bei Mali et al.,
- die Nummer des Satzes bei Zhang,
- eine zweite Veröffentlichung zu fehlgeschlagenen NgAgo-Replikationen (Burgess et al.), deren DOI offen blieb.

## Was der Test am Prozess geändert hat

| Befund | Änderung |
|---|---|
| In der Mathematik gibt es weder Datensatz noch Ereignis. Ein Beleg ließ sich nicht anlegen | Belege nennen allgemein ihre Grundlagen in `basis_ids`. Einträge unter `data/datasets/` tragen eine Art: Datensatz, Ereignis, Versuchsreihe, klinische Studie oder Beweis |
| Die zurückgezogene NgAgo-Studie zählte als stützende Quelle | Ein Beleg aus einer zurückgezogenen Studie stützt nichts mehr. Er bleibt mit Vermerk sichtbar |
| Ein vollständig erfasstes Fach sah mit „0 von 4“ aus wie ein leeres | Vorschläge sind sichtbar: gestrichelte Station auf der Route und eigene Seite „Offene Prüfungen“. Der Zähler bleibt unverändert |
| Ein Sprachmodell ließ sich als eine der zwei Personen eintragen | Eigenes Feld `suggested_by`. Für die Freigabe zählen nur `extracted_by` und `reviewed_by` |
| Ein einzelner Beleg mit zwei Ereignissen genügte für „mehrfach gestützt“ | Verlangt werden zwei stützende Belege auf zwei verschiedenen Grundlagen |
| Auch ein Vorschlag konnte den Belegen widersprechen | Die Evidenzlage wird schon beim Vorschlag gegen die Belege geprüft |
| „Vorläufig gestützt“ passt nicht zu einem veröffentlichten Beweis | Fachprofile in `atlas.yaml` geben eigene Bezeichnungen vor, für die Mathematik „bewiesen (ein Beweis)“ |
| Aussage und Meilenstein mit gleichem Namensteil ergaben dieselbe Entscheidungs-ID. Die zweite Datei überschrieb die erste | Die ID einer Entscheidung enthält die vollständige ID ihres Gegenstands |

## Was offen bleibt

- **Eine Stufe fehlt.** GW150914 ist ein einzelnes Ereignis und wurde von einer zweiten Gruppe ausgewertet. Die Evidenzlage kennt dafür nur „vorläufig gestützt“. Die zweite Auswertung erscheint allein unter „Art der Absicherung“.
- **Unabhängigkeit bleibt ein Urteil.** Das Skript zeigt gemeinsame Teams und Instrumente. Drei Fragen kann es nicht entscheiden: ob die Autorengruppe von 1-OGC unabhängig von der Kollaboration ist, ob zwei Beweise auf demselben Ansatz als unabhängig gelten und wie zwei Studien desselben Sponsors zu werten sind.
- **Die Kataloge sind nachträglich entstanden.** Kapitel 1 verlangt vorab definierte Meilensteine. Für abgeschlossene Forschung geht das nicht. Der Katalog selbst hat im Datenmodell keinen Prüfstand und wurde von niemandem freigegeben.
- **Qualitative Befunde.** Die Felder für Ergebnis und Unsicherheit sind auf Zahlen ausgelegt. Befunde aus Zellkulturexperimenten stehen dort als Text.
- **Der Verlauf beginnt heute.** Er zeigt das Datum der Atlasentscheidung. Die historische Abfolge von Befund, Widerlegung und Rückzug bei NgAgo erscheint nur über die Daten der Studien.

## Ausbau in alle sechs Bereiche

**Stand vom 22. November 2026.** Zwölf weitere Ziele erweitern die Karte in drei Richtungen: nach außen in alle sechs Bereiche, zur Seite in neue Fachgebiete und nach innen mit einem zweiten Teilgebiet in Mathematik, Informatik, Physik und Biologie. Der Atlas hat damit 17 Ziele in 12 von 42 Fachgebieten. Alle neuen Einträge sind Vorschläge.

| Fachgebiet | Teilgebiet | Ziel | Was der Fall zeigt |
|---|---|---|---|
| Mathematik | Kugelpackungen | Kepler-Vermutung beweisen und formal prüfen | Zwei Veröffentlichungen, ein Beweis: Die formale Prüfung zählt nicht als zweiter Beweis |
| Informatik | Quantenüberlegenheit | Rechenvorteil eines Quantenprozessors belegen | Eine Schätzung, die eine spätere Nachrechnung überholt |
| Physik, Astronomie | Higgs-Boson | Higgs-Boson nachweisen und Masse bestimmen | Zwei Experimente mit eigenen Detektoren am selben Beschleuniger |
| Chemie | Superschwere Elemente | Element 117 erzeugen und bestätigen | Bestätigung in einem zweiten Labor mit eigener Anlage |
| Geowissenschaften | Massenaussterben am Ende der Kreidezeit | Einschlag belegen und datieren | Drei Belege verschiedener Art für eine Kette von Meilensteinen |
| Biologie | Proteinstrukturvorhersage | Strukturen aus der Sequenz vorhersagen | Verblindeter Vergleich als gemeinsame Grundlage zweier Verfahren |
| Werkstofftechnik | Supraleitung bei Raumtemperatur | LK-99 unabhängig bestätigen | Erstmeldung als Preprint, zwei Gruppen finden nichts |
| Klinische Medizin | mRNA-Impfstoffe gegen COVID-19 | Wirksamkeit belegen | Zwei Studien verschiedener Sponsoren, dazu eine Beobachtungsstudie |
| Agrarbiotechnologie | Biofortifikation von Reis | Provitamin A anreichern und Wirkung belegen | Eine zurückgezogene Studie lässt den letzten Meilenstein unerreicht |
| Psychologie | Selbstkontrolle | Ego-Depletion-Effekt replizieren | Erstbefund gegen zwei große, vorab registrierte Replikationen |
| Wirtschaftswissenschaften | Staatsverschuldung und Wachstum | Wachstumseinbruch nachrechnen | Nachrechnung auf demselben Datensatz mit anderem Ergebnis |
| Geschichte, Archäologie | Identifizierung historischer Personen | Skelett als Richard III. identifizieren | Eine Quelle, ein offener Meilenstein ohne Beleg |

Diese Angaben ließen sich per Websuche nicht bestätigen. Sie fehlen oder sind im Beleg als offen vermerkt:

- die Konfidenzintervalle der beiden Phase-3-Studien zu den Impfstoffen,
- die Anreicherungsfaktoren des Iridiums bei Alvarez et al.,
- die Seitenzahlen der CMS-Veröffentlichung,
- die Nummer des Hauptsatzes bei Hales und die Zahlenwerte zu RoseTTAFold,
- die Angaben zur Veröffentlichung bei Ye et al., Baumeister et al. und Reinhart und Rogoff,
- die DOI der zurückgezogenen Studie von Tang et al. und die Kennung des Preprints zu LK-99.

Bei drei Studien verweist der Link deshalb auf einen Nachweis in einer Datenbank oder auf ein Arbeitspapier statt auf die Zeitschrift: Hildebrand et al., Hagger et al. sowie Herndon, Ash und Pollin.

Der Ausbau hat den Prozess nicht mehr verändert. Alle neuen Fälle ließen sich mit dem bestehenden Datenmodell erfassen, auch der zurückgezogene, der widersprüchliche und der bedingte.

## Der Weg zur Freigabe

1. Eine Person prüft einen Beleg gegen den Volltext, trägt die genaue Fundstelle nach und setzt sich in `extracted_by` ein.
2. Eine zweite Person prüft Fundstelle, Richtung und Grenzen, setzt sich in `reviewed_by` ein und stellt `review_status` auf `freigegeben`.
3. Dieselben zwei Schritte folgen für die Entscheidung. Sie erhält zusätzlich die Art der Absicherung und den Status `freigegeben`.

`tests/test_fachgebiete.py` spielt diesen Weg für alle Vorschläge durch. Das Ergebnis wäre 4 von 4 in der Physik, 4 von 5 in der Mathematik, 4 von 4 bei CRISPR-Cas9 und 0 von 2 bei NgAgo.
