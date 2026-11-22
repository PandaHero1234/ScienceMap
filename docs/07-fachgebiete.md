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

## Zweite Ausbaustufe: 26 von 42 Fachgebieten

**Stand vom 22. November 2026.** Fünfzehn weitere Ziele bringen vierzehn neue Fachgebiete auf die Karte und ein zweites Teilgebiet in die Klinische Medizin. Der Atlas hat damit 32 Ziele in 26 von 42 Fachgebieten. Jeder der sechs Bereiche hat mindestens drei Fachgebiete mit Zielen. Alle neuen Einträge sind Vorschläge.

| Fachgebiet | Teilgebiet | Ziel | Was der Fall zeigt |
|---|---|---|---|
| Elektrotechnik, Elektronik, Informationstechnik | Memristor | Den vorhergesagten Memristor als Bauelement nachweisen | Streit um die Einordnung derselben Bauelemente, ohne neue Messung |
| Industrielle Biotechnologie | Enzymatischer Abbau von PET | PET schnell genug für die Wiederverwertung abbauen | Ein Meilenstein mit Schwelle: 90 % in unter einem Tag |
| Nanotechnologie | Graphen | Atomar dünne Schichten herstellen, Dirac-Fermionen nachweisen | Zwei Gruppen mit eigenen Proben im selben Band der Zeitschrift |
| Klinische Medizin | Helicobacter pylori und Geschwüre | Bakterium als Ursache wiederkehrender Geschwüre belegen | Befund bestätigt, Zahlen fehlen noch: Der Beleg bleibt bewusst unvollständig |
| Gesundheitswissenschaften | Rauchen und Lungenkrebs | Rauchen als Ursache von Lungenkrebs belegen | Drei Grundlagen verschiedener Art, zwei davon vom selben Team |
| Medizinische Biotechnologie | CAR-T-Zell-Therapie | Remissionen bei Leukämie erreichen | Zwei Studien derselben Arbeitsgruppe: Die Seite nennt die Abhängigkeit |
| Land- und Forstwirtschaft, Fischerei | Neonicotinoide und Bestäuber | Schaden an Bienen klären | Dieselbe Studie stützt eine Aussage und spricht gegen eine andere |
| Tierzucht, Tierproduktion | Klonen durch Kerntransfer | Säugetier aus erwachsener Körperzelle klonen | Genetische Prüfung der Herkunft, eine Analyse davon nicht unabhängig |
| Veterinärmedizin | BSE und Creutzfeldt-Jakob-Krankheit | Herkunft der neuen Variante klären | Zwei Gruppen mit eigenen Übertragungsversuchen |
| Erziehungswissenschaften | Growth Mindset | Wirkung einer kurzen Intervention klären | Eine Meta-Analyse als nicht entscheidender Beleg |
| Soziologie | Benachteiligung bei Bewerbungen | Benachteiligung mit Feldexperimenten messen | Meta-Analyse, die ein erfasstes Experiment enthalten kann |
| Politikwissenschaften | Einstellungswandel durch Gespräche | Dauerhafte Wirkung eines Haustürgesprächs zeigen | Zurückgezogene Erststudie, Nachfolgestudie der Kritiker |
| Sprach- und Literaturwissenschaften | Autorschaft der Federalist Papers | Autorschaft der zwölf umstrittenen Texte klären | Eine Quelle, Bestätigung durch ein zweites Verfahren offen |
| Philosophie, Ethik, Religion | Experimentelle Philosophie | Knobe-Effekt belegen | Große Replikationsstudie, deren Abstract den Einzelfall nicht nennt |
| Kunstwissenschaften | Echtheitsprüfung von Gemälden | Bleiweiß über natürliche Radioaktivität datieren | Verfahren belegt, Anwendung nur mit dem Titel erfasst |

Diese Angaben ließen sich per Websuche nicht bestätigen. Sie fehlen oder sind im Beleg als offen vermerkt:

- die Rückfallraten beider Gruppen bei Hentschel et al.,
- die Zahlen zu Fällen, Kontrollen und Sterblichkeit in den drei Arbeiten zu Rauchen und Lungenkrebs,
- Verfahren und Fallzahlen bei Hill et al.,
- die Effektstärken bei Sisk et al. und das Konfidenzintervall bei Yeager et al.,
- der Vergleichswert für die nützliche Nebenfolge bei Knobe und die Frage, ob seine Studie zu den 40 replizierten gehört,
- welche Gemälde Keisch 1968 gemessen hat und mit welchem Ergebnis,
- die Befunde von Holmes und Forsyth 1995 zu den Federalist Papers,
- die DOI von Mosteller und Wallace, die nur aus einer Literaturliste stammt.

Sechs Werte stammen aus Sekundärquellen und sind im Beleg so gekennzeichnet: die Schlussfolgerungen von Doll und Hill, die Zahl der Fälle bei Will et al., die Notenverbesserung bei Yeager et al., der Anteil bei Knobe sowie Dauer und Temperatur bei Yoshida et al.

Bei 14 der 36 neuen Studien verweist der Link auf die Fassung, die gelesen wurde, statt auf die Zeitschrift: auf ein Arbeitspapier (Bertrand und Mullainathan; Kline, Rose und Walters), einen Preprint (Novoselov et al. 2005, Zhang et al.), ein Repositorium oder Archiv (Broockman und Kalla, Knobe), einen Eintrag in PubMed oder einem Katalog (Hentschel et al., Maude et al. 2014 und 2018, Henry et al., Bruce et al., Wilmut et al., Keisch 1968) oder einen Eintrag im Astrophysics Data System (Novoselov et al. 2004). Die zurückgezogene Studie von LaCour und Green ist über die Rückzugsnotiz verlinkt.

Auch diese Stufe hat den Prozess nicht verändert. Neu genutzt wurde nur, was das Datenmodell schon konnte: die Beziehung „nicht entscheidend“ und Fassungen einer Studie, die nicht die Zeitschriftenfassung sind.

## Vertiefung der bestehenden Ziele

**Stand vom 22. November 2026.** Diese Stufe bringt kein neues Fachgebiet. Sie füllt offene Meilensteine, erweitert drei Ziele um weitere Meilensteine und gibt einem Teilgebiet ein zweites Ziel. Der Atlas hat damit 33 Ziele mit 97 Meilensteinen. Elf davon sind offen, vorher waren es dreizehn von 87.

| Ziel | Was dazukam | Was der Fall zeigt |
|---|---|---|
| Helicobacter pylori | Zweite kontrollierte Studie (Graham et al. 1992) mit 12 % gegenüber 95 % Rückfällen | Der offene dritte Meilenstein hat jetzt einen Vorschlag |
| Knobe-Effekt | Replikation in Many Labs 2 | Unabhängiges Team, die Aussage wäre mehrfach gestützt |
| Federalist Papers | Zweites Verfahren (Fung 2003) | Zwei Quellen auf denselben Texten bleiben eine Grundlage |
| Haustürgespräche | Drei weitere Feldexperimente (Kalla und Broockman 2020) | Zweite Quelle desselben Teams: Der Meilenstein „anderes Team“ bleibt offen |
| PET-Abbau | Zweites Enzym (Lu et al. 2022) | Abbaugrad erreicht, aber in einer Woche: Das Kriterium nennt keine Zeit |
| CAR-T-Zell-Therapie | Verlauf über drei Jahre (Laetsch et al. 2023) | Drei Jahre erfüllen ein Kriterium von fünf Jahren nicht |
| Higgs-Boson | Zielkatalog v2: Zerfall in Bottom-Quarks bei ATLAS und CMS | Ein Ziel wächst, frühere Vorschläge bleiben gültig |
| Proteinstrukturvorhersage | Zielkatalog v2: Datenbank, Komplexe, unabhängige Prüfung | Angabe der Entwickler, die unabhängige Prüfung bleibt offen |
| Quantenüberlegenheit | Zielkatalog v2: zweite Plattform, größerer Prozessor | Wieder Schätzungen des klassischen Aufwands, keine Beweise |
| Gravitationswellen | Zweites Ziel im Teilgebiet: Neutronensterne und Gammablitz | Ein Beleg mit zwei Ereignissen als Grundlage |

Zwei Entscheidungen zum Vorgehen:

- **Ein Ziel wächst über eine neue Katalogversion.** Die neuen Meilensteine stehen in Katalog v2, der alle Meilensteine aus v1 behält. Der Verlauf nennt den Wechsel mit Begründung. Vorschläge zu den neuen Meilensteinen tragen `catalog_version: 2`.
- **Ein eigener, ungeprüfter Vorschlag wird ersetzt.** Kommt ein Beleg dazu, ändert das Sprachmodell seinen offenen Vorschlag zur Aussage, statt einen zweiten daneben zu legen. Die frühere Fassung steht in der Versionsgeschichte. Für freigegebene Entscheidungen gilt weiter `supersedes`.

Diese Angaben ließen sich nicht bestätigen. Sie fehlen oder sind im Beleg als offen vermerkt:

- die Effektstärke des Knobe-Effekts in Many Labs 2,
- die drei Wörter bei Fung und der Wortlaut seines Artikels,
- die Dauer der Wirkung in den beiden Versuchen zu Transphobie von 2020,
- die Schätzung des klassischen Aufwands bei Zhong et al., die nur über Berichte erfasst ist,
- die Zuordnung der 95 % zur Vergleichsgruppe bei Graham et al.,
- ein zweites Signal zweier Neutronensterne und ein Verlauf über fünf Jahre bei CAR-T.

Die Werte aus Tabelle 4 des Pilots sind weiterhin nicht geprüft. Die Fassungen bei Zenodo, der Universität Tartu und Springer sind aus der Arbeitsumgebung nicht erreichbar.

## Der Weg zur Freigabe

1. Eine Person prüft einen Beleg gegen den Volltext, trägt die genaue Fundstelle nach und setzt sich in `extracted_by` ein.
2. Eine zweite Person prüft Fundstelle, Richtung und Grenzen, setzt sich in `reviewed_by` ein und stellt `review_status` auf `freigegeben`.
3. Dieselben zwei Schritte folgen für die Entscheidung. Sie erhält zusätzlich die Art der Absicherung und den Status `freigegeben`.

`tests/test_fachgebiete.py` spielt diesen Weg für alle Vorschläge durch. Das Ergebnis wäre 4 von 4 in der Physik, 4 von 5 in der Mathematik, 4 von 4 bei CRISPR-Cas9 und 0 von 2 bei NgAgo. `tests/test_ausbau.py`, `tests/test_ausbau2.py` und `tests/test_vertiefung.py` tun dasselbe für die Ausbaustufen und die Vertiefung.
