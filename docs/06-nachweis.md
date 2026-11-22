# Nachweis: Was funktioniert und was offen bleibt

**Stand vom 21. November 2026.** Der in dieser Dokumentation beschriebene Weg von versionierten Daten zur Übersicht ist gebaut und läuft. Der inhaltliche Stand des Pilots bleibt bei 0 von 4 Meilensteinen, weil die Zweitprüfung durch eine zweite Person aussteht.

## So lässt sich der Nachweis wiederholen

```bash
pip install -r requirements.txt
python scripts/atlas.py validate     # prüft die Daten
python -m pytest -q                  # prüft jede Regel
python scripts/atlas.py build        # schreibt die Übersicht nach public/
```

Von den 197 Tests arbeiten 52 mit erfundenen Daten in einem temporären Ordner. Die übrigen lesen die echten Daten. Sie leiten ihre Erwartungen aus den Daten ab, damit ein weiterer Ausbau der Karte keine Tests bricht. Als Gegenprobe wurden dreizehn Regeln einzeln im Skript ausgeschaltet. Jedes Mal schlug mindestens ein Test fehl.

## Belegt

| Regel aus der Dokumentation | Kapitel | Test in `tests/` |
|---|---|---|
| Der Pilot steht bei 0 von 4, Zielkatalog v1 | 1 | `test_pilotstand_entspricht_der_dokumentation` |
| Der Zähler enthält nur Meilensteine mit freigegebener Entscheidung „erreicht“ | 1 | `test_freigegebene_entscheidung_erhoeht_den_zaehler`, `test_vorschlag_zaehlt_nicht` |
| Ein zweiter Wert zählt die geprüften Aussagen | 1 | `test_zweiter_wert_zaehlt_gepruefte_aussagen` |
| Ein neuer Meilenstein erhöht den Nenner und erhält einen Änderungseintrag. Ältere Stände bleiben mit ihrer Katalogversion abrufbar | 1 | `test_neuer_meilenstein_erhoeht_nenner_und_alter_stand_bleibt_abrufbar` |
| Ein Ziel ohne Meilensteine zeigt „Katalog offen“ | 1 | `test_ziel_ohne_meilensteine_zeigt_katalog_offen` |
| Jeder Meilenstein zählt höchstens einmal | 1 | `test_meilenstein_darf_nur_einmal_definiert_sein` |
| Ein unbekannter Verweis stoppt die Aktualisierung | 3 | `test_unbekannte_studie_stoppt` und drei weitere, `test_fehler_stoppen_die_aktualisierung` |
| Eine Freigabe braucht zwei Personen, Begründung und Beleg-IDs | 2, 3 | `test_freigabe_braucht_zwei_verschiedene_personen` und vier weitere |
| Wiederverwendete Daten zählen als eine Beobachtung, alle Quellen bleiben sichtbar | 2, 3 | `test_gemeinsame_auswertung_zaehlt_die_ereignisse_nur_einmal` |
| Ausschnitte desselben Rohlogs haben dieselbe Herkunft | 5 | `test_ausschnitt_desselben_rohlogs_ist_keine_neue_beobachtung` |
| Bei widersprechenden Nachfolgern gilt die letzte eindeutige Freigabe | 3 | `test_bei_konflikt_gilt_die_letzte_eindeutige_freigabe` |
| Neue Belege, Korrekturen und Rückzüge lösen eine erneute Prüfung aus. Die alte Entscheidung bleibt lesbar | 2 | `test_neuer_beleg_loest_eine_erneute_pruefung_aus`, `test_korrigierte_messung_ueberholt_den_urspruenglichen_befund` |
| Ein Nullergebnis kann einen Meilenstein erfüllen | 5 | `test_nullergebnis_kann_einen_meilenstein_erfuellen` |
| Bei Dissens bleibt der Vorschlag offen und die abweichende Begründung sichtbar | 2 | `test_dissens_bleibt_sichtbar_und_der_vorschlag_offen` |
| Von der Startseite führt ein Weg über Ziel und Aussage zur Fundstelle und zum Einwand | 5 | `test_weg_von_der_startseite_bis_zur_fundstelle` |
| Kein interner Link und kein Anker führt ins Leere | 1 | `test_kein_interner_link_und_kein_anker_fuehrt_ins_leere` |
| Jeder ungeprüfte Eintrag steht unter „Offene Prüfungen“ mit seiner Datei | 1 | `test_offene_pruefungen_nennen_jeden_ungeprueften_eintrag_mit_datei` |
| Der Zustand einer Station steht als Text und nicht nur als Farbe | 1 | `test_zustand_steht_als_text_und_nicht_nur_als_farbe` |
| Alle Inhalte sind ohne JavaScript lesbar | 1 | `test_ohne_javascript_ist_alles_lesbar` |
| Der Gesamtstand zählt alle Meilensteine nach Zustand, die Fächer ergeben zusammen das Ganze | 1 | `test_gesamtstand_zaehlt_alle_meilensteine_nach_zustand`, `test_faecher_ergeben_zusammen_den_gesamtstand` |
| Die Karte hat eine Kachel je Meilenstein, Aussage und Beleg | 1 | `test_karte_hat_eine_kachel_je_meilenstein_aussage_und_beleg` |
| Die Kurve zeigt erreichte Meilensteine über die Zeit | 1 | `test_kurve_zeigt_erreichte_meilensteine_ueber_die_zeit` |
| Der Über-Atlas zeigt alle 42 Fachgebiete, auch die leeren, und die Fachgebiete ergeben zusammen den Gesamtstand | 1 | `test_startseite_zeigt_alle_fachgebiete_auch_die_leeren`, `test_fachgebiete_ergeben_zusammen_den_gesamtstand` |
| Ein Ziel ohne oder mit unbekanntem Fachgebiet stoppt die Aktualisierung | 3 | `test_ziel_ohne_fachgebiet_stoppt`, `test_unbekanntes_fachgebiet_stoppt` |
| Jede der sechs Ebenen führt hinein zur nächsten und mit einem Knopf hinaus zur vorigen | 1 | `test_jede_ebene_fuehrt_hinein_zur_naechsten`, `test_jede_ebene_fuehrt_mit_einem_knopf_hinaus_zur_vorigen` |
| Jede Ebene nennt ihre Stufe und den ganzen Weg nach außen | 1 | `test_jede_ebene_nennt_ihre_stufe_und_den_ganzen_weg_nach_aussen` |
| Ein Vorschlag ist sichtbar und verändert den Zähler nicht | 2, 7 | `test_vorschlag_ist_sichtbar_und_zaehlt_nicht` |
| Ein Sprachmodell ersetzt keine der zwei Personen | 2 | `test_sprachmodell_ersetzt_keine_der_zwei_personen` |
| Eine zurückgezogene Studie stützt nichts mehr | 7 | `test_zurueckgezogene_studie_stuetzt_nichts_mehr` |
| Ein Beweis ist eine Grundlage wie ein Datensatz oder ein Ereignis | 7 | `test_zwei_verschiedene_beweise_sind_zwei_grundlagen` |
| Die Vorschläge der drei Fächer bleiben nach einer Freigabe durch zwei Personen widerspruchsfrei | 7 | `test_nach_freigabe_steht_der_zaehler_wie_vorgeschlagen` |
| Ein nicht entscheidender Beleg zählt weder dafür noch dagegen | 7 | `test_nicht_entscheidender_beleg_zaehlt_weder_dafuer_noch_dagegen` |
| Dieselbe Studie kann eine Aussage stützen und gegen eine andere sprechen | 7 | `test_eine_studie_stuetzt_eine_aussage_und_spricht_gegen_eine_andere` |
| Der Link eines Belegs führt zu der Fassung, die gelesen wurde | 7 | `test_beleg_verweist_auf_die_fassung_die_gelesen_wurde` |
| Jeder der sechs Bereiche hat mindestens drei Fachgebiete mit Zielen | 7 | `test_jeder_bereich_hat_mindestens_drei_fachgebiete_mit_zielen` |
| Weitere Meilensteine kommen als neue Katalogversion, frühere Vorschläge bleiben bei ihrem Meilenstein | 3, 7 | `test_weitere_meilensteine_kommen_als_neue_katalogversion`, `test_vorschlaege_aus_katalog_v1_bleiben_bei_ihrem_meilenstein` |
| Ein Vorschlag für die falsche Katalogversion stoppt die Aktualisierung | 3 | `test_vorschlag_fuer_falsche_katalogversion_stoppt` |
| Zwei Verfahren auf denselben Texten zählen als eine Grundlage | 7 | `test_zwei_verfahren_auf_denselben_texten_sind_eine_grundlage` |
| Eine zweite Studie desselben Teams erfüllt kein Kriterium, das ein anderes Team verlangt | 7 | `test_zweite_studie_desselben_teams_laesst_den_meilenstein_offen` |

## Widerlegt oder nur mit Änderung umsetzbar

| Annahme im Entwurf | Befund | Lösung im Repository |
|---|---|---|
| Das Datenbeispiel nutzt `relation: supports` und `review_status: proposed` | Die Werte widersprechen dem deutschen Vokabular aus Kapitel 2 | Feste Schlüsselwerte, siehe Kapitel 3. Die englischen Werte werden abgelehnt |
| „Die letzte eindeutige Freigabe bleibt gültig“ | Ohne Verweis auf die Vorgängerin ist das nicht entscheidbar | Feld `supersedes`. Eine klärende Entscheidung ersetzt beide Konfliktparteien |
| Zwei Erstentscheidungen zum selben Gegenstand | Es gibt keinen früheren eindeutigen Stand | Der Gegenstand gilt als offen, der Konflikt wird angezeigt |
| Die Beispielkarten nennen „An zwei Ereignissen beobachtet“ und „durch Korrektur überholt“ | Beide Bezeichnungen fehlen im Vokabular der Evidenzlage | Kein neuer Wert nötig. Die Seite zeigt Quellen und Beobachtungen als Zahl und die frühere Entscheidung im Verlauf |
| „Zwei Personen“ prüfen | Das Skript erkennt zwei verschiedene Namen, keine zwei verschiedenen Menschen | Absicherung über den Review im Pull Request. Eine Schutzregel für `main` ist einzurichten |
| „Hinreichende Unabhängigkeit“ | Ohne Fachprofil nicht berechenbar | Geprüft wird das Minimum von zwei verschiedenen Beobachtungen. Gemeinsames Team und Instrument werden angezeigt und fachlich bewertet |
| Ordner `methodik/` | Die Methodik liegt bereits in `docs/` | Kapitel 3 nennt die tatsächlichen Pfade |

## Nicht belegt

- **Zahlenwerte aus Tabelle 4.** Die Werte 0,88 und 0,66 stammen aus dem Dokumentationsentwurf. Sie sind noch nicht mit der Veröffentlichung abgeglichen. Der Beleg steht deshalb auf „vorgeschlagen“. Dieser Abgleich ist Meilenstein 1.
- **Variante des Inductive Miner, Fassung und Vorverarbeitung von BPIC12.** Diese Angaben sind in Aussage und Datensatz als offen markiert.
- **Veröffentlichung von `main` aus.** Die Übersicht ist auf GitHub Pages veröffentlicht. Den Lauf von `main` aus lehnt GitHub bisher ab, vermutlich weil die Umgebung `github-pages` nur den früheren Standard-Branch zulässt. Bis `main` dort eingetragen ist, wird der Lauf von Hand vom Arbeits-Branch aus gestartet.
- **Überwachung von Korrekturen und Rückzügen.** Jemand muss den Status der Studie von Hand eintragen. Danach markiert das Skript alle betroffenen Entscheidungen.
- **Unsicherheit in Meilenstein 3.** Das Kriterium nennt noch kein Verfahren und keine Schwelle für „Vorteil nicht nachweisbar“.
- **Einträge außerhalb des Pilots.** Die Einträge der 32 weiteren Ziele sind mit Abstracts abgeglichen, nicht mit den Volltexten. Was sich nicht bestätigen ließ, steht in [Drei Fachgebiete als Prozesstest](07-fachgebiete.md).
- **Bezeichnungen der Systematik.** Der Aufbau von ÖFOS 2012 mit 6 Hauptgruppen und 42 Gruppen ist geprüft. Die Namen der Gruppen sind noch nicht vollständig mit der Veröffentlichung von Statistik Austria abgeglichen.
- **Zuordnung von Meilenstein 1.** Der Quellenabgleich ist Arbeit am Atlas und zählt derzeit im Fortschrittsbalken mit. Kapitel 1 trennt beides. Die Entscheidung steht aus.
