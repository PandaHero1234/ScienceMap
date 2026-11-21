"""Jede Regel aus der Dokumentation als Test. Die Zuordnung steht in docs/06-nachweis.md."""

from __future__ import annotations

import json

import atlas
from conftest import MILESTONES


def has(errors: list[str], *parts: str) -> bool:
    return any(all(p in line for p in parts) for line in errors)


# --- Zählregel (docs/01) ----------------------------------------------------


def test_ohne_entscheidung_null_von_vier(world):
    goal = world.goal()
    assert goal["display"] == "0 von 4"
    assert (goal["claims_reviewed"], goal["claims_total"]) == (0, 1)


def test_freigegebene_entscheidung_erhoeht_den_zaehler(world):
    world.decide("dec-1", "ms-a", "erreicht", "2026-02-01")
    goal = world.goal()
    assert goal["display"] == "1 von 4"
    assert goal["milestones"][0]["status"] == "erreicht"


def test_vorschlag_zaehlt_nicht(world):
    world.decide("dec-1", "ms-a", "erreicht", "2026-02-01", status="vorgeschlagen")
    assert world.goal()["display"] == "0 von 4"


def test_nicht_erreicht_zaehlt_nicht(world):
    world.decide("dec-1", "ms-a", "nicht_erreicht", "2026-02-01")
    assert world.goal()["display"] == "0 von 4"


def test_zweiter_wert_zaehlt_gepruefte_aussagen(world):
    world.decide("dec-1", "cl-a", "vorlaeufig_gestuetzt", "2026-02-01")
    goal = world.goal()
    assert (goal["claims_reviewed"], goal["claims_total"]) == (1, 1)
    assert goal["display"] == "0 von 4", "eine geprüfte Aussage ist noch kein erreichter Meilenstein"


def test_ziel_ohne_meilensteine_zeigt_katalog_offen(world):
    world.put("goals", {"id": "goal-leer", "field": "Anderes Fach", "title": "Ziel ohne Katalog"})
    leer = next(g for g in world.state()["goals"] if g["id"] == "goal-leer")
    assert leer["display"] == "Katalog offen"
    assert leer["milestones_total"] is None


def test_neuer_meilenstein_erhoeht_nenner_und_alter_stand_bleibt_abrufbar(world):
    world.decide("dec-1", "ms-a", "erreicht", "2026-02-01")
    goal = atlas.load(world.root)[0].goals["goal-test"]
    goal["milestones"].append({"id": "ms-e", "title": "ms-e", "criterion": "Neu"})
    goal["catalog"].append({"version": 2, "date": "2026-03-01", "reason": "Fünfter Meilenstein ergänzt",
                            "milestones": MILESTONES + ["ms-e"]})
    world.put("goals", goal)
    state = world.state()
    assert state["goals"][0]["display"] == "1 von 5"
    assert state["goals"][0]["catalog_version"] == 2
    stand = {e["date"]: e["stand"]["goal-test"] for e in state["history"]}
    assert stand["2026-02-01"] == {"display": "1 von 4", "catalog_version": 1}
    assert stand["2026-03-01"] == {"display": "1 von 5", "catalog_version": 2}
    katalog = [e for e in state["history"] if e["type"] == "katalog"]
    assert katalog[-1]["added"] == ["ms-e"], "der neue Meilenstein hat einen eigenen Änderungseintrag"


def test_meilenstein_darf_nur_einmal_definiert_sein(world):
    world.put("goals", {
        "id": "goal-zwei", "field": "Testfach", "title": "Zweites Ziel",
        "milestones": [{"id": "ms-a", "title": "doppelt", "criterion": "x"}],
        "catalog": [{"version": 1, "date": "2026-01-01", "reason": "x", "milestones": ["ms-a"]}]})
    assert has(world.errors(), "ms-a", "bereits")


# --- Verweise und Pflichtangaben (docs/03) ---------------------------------


def test_unbekannte_studie_stoppt(world):
    world.evidence("ev-b", study="st-fehlt")
    assert has(world.errors(), "ev-b", "unbekannte Studie")


def test_unbekannte_aussage_stoppt(world):
    world.evidence("ev-b", claim="cl-fehlt")
    assert has(world.errors(), "ev-b", "unbekannte Aussage")


def test_unbekannter_meilenstein_stoppt(world):
    world.put("claims", {"id": "cl-b", "statement": "x", "scope": "y", "milestone_ids": ["ms-fehlt"]})
    assert has(world.errors(), "cl-b", "unbekannter Meilenstein")


def test_unbekannter_beleg_in_entscheidung_stoppt(world):
    world.decide("dec-1", "ms-a", "erreicht", "2026-02-01", evidence_ids=["ev-fehlt"])
    assert has(world.errors(), "dec-1", "unbekannter Beleg")


def test_fehler_stoppen_die_aktualisierung(world, tmp_path, capsys):
    world.evidence("ev-b", study="st-fehlt")
    out = tmp_path / "ausgabe"
    assert atlas.main(["build", "--data", str(world.root), "--out", str(out)]) == 1
    assert not out.exists(), "bei Fehlern darf keine Übersicht geschrieben werden"
    assert "wird nicht aktualisiert" in capsys.readouterr().err


def test_id_muss_dem_dateinamen_entsprechen(world):
    (world.root / "datasets" / "ds-anders.yaml").write_text(
        "id: ds-eins\ntitle: x\nsource: y\n", encoding="utf-8")
    assert has(world.errors(), "ds-anders.yaml", "Dateinamen")


def test_englische_werte_aus_dem_entwurf_werden_abgelehnt(world):
    world.evidence("ev-b", relation="supports")
    assert has(world.errors(), "ev-b", "relation")


def test_freigabe_braucht_zwei_verschiedene_personen(world):
    world.decide("dec-1", "ms-a", "erreicht", "2026-02-01", reviewed_by="ada")
    assert has(world.errors(), "dec-1", "zwei verschiedenen Personen")


def test_freigabe_ohne_zweitpruefung_wird_abgelehnt(world):
    world.decide("dec-1", "ms-a", "erreicht", "2026-02-01", reviewed_by=None)
    assert has(world.errors(), "dec-1", "zwei verschiedenen Personen")


def test_freigabe_braucht_belege(world):
    world.decide("dec-1", "ms-a", "erreicht", "2026-02-01", evidence_ids=[])
    assert has(world.errors(), "dec-1", "Beleg-IDs")


def test_freigabe_braucht_begruendung(world):
    world.decide("dec-1", "ms-a", "erreicht", "2026-02-01", rationale=None)
    assert has(world.errors(), "dec-1", "rationale")


def test_freigabe_auf_ungeprueftem_beleg_wird_abgelehnt(world):
    world.evidence("ev-a", released=False)
    world.decide("dec-1", "ms-a", "erreicht", "2026-02-01")
    assert has(world.errors(), "dec-1", "noch nicht freigegeben")


def test_beleg_muss_zum_gegenstand_gehoeren(world):
    world.decide("dec-1", "ms-c", "erreicht", "2026-02-01")
    assert has(world.errors(), "dec-1", "gehört nicht zu ms-c")


# --- Nachfolge und Konflikte (docs/03) --------------------------------------


def test_nachfolger_ersetzt_fruehere_entscheidung_und_bleibt_lesbar(world):
    world.decide("dec-1", "ms-a", "erreicht", "2026-02-01")
    world.decide("dec-2", "ms-a", "nicht_erreicht", "2026-03-01", supersedes="dec-1")
    state = world.state()
    milestone = state["goals"][0]["milestones"][0]
    assert state["goals"][0]["display"] == "0 von 4"
    assert milestone["decision"]["id"] == "dec-2"
    assert [d["id"] for d in milestone["earlier_decisions"]] == ["dec-1"]
    events = {e["decision_id"]: e for e in state["history"] if e["type"] == "entscheidung"}
    assert events["dec-1"]["stand"]["goal-test"]["display"] == "1 von 4"
    assert (events["dec-2"]["old"], events["dec-2"]["new"]) == (["erreicht"], "nicht_erreicht")


def test_bei_konflikt_gilt_die_letzte_eindeutige_freigabe(world):
    world.decide("dec-1", "ms-a", "erreicht", "2026-02-01")
    world.decide("dec-2", "ms-a", "nicht_erreicht", "2026-03-01", supersedes="dec-1")
    world.decide("dec-3", "ms-a", "erreicht", "2026-03-01", supersedes="dec-1")
    state = world.state()
    milestone = state["goals"][0]["milestones"][0]
    assert milestone["decision"]["id"] == "dec-1"
    assert milestone["conflict"] == ["dec-2", "dec-3"]
    assert state["goals"][0]["display"] == "1 von 4"
    assert atlas.conflicts(state)


def test_klaerende_entscheidung_loest_den_konflikt(world):
    world.decide("dec-1", "ms-a", "erreicht", "2026-02-01")
    world.decide("dec-2", "ms-a", "nicht_erreicht", "2026-03-01", supersedes="dec-1")
    world.decide("dec-3", "ms-a", "erreicht", "2026-03-01", supersedes="dec-1")
    world.decide("dec-4", "ms-a", "nicht_erreicht", "2026-04-01", supersedes=["dec-2", "dec-3"])
    milestone = world.goal()["milestones"][0]
    assert milestone["decision"]["id"] == "dec-4"
    assert milestone["conflict"] == []


def test_zwei_erstentscheidungen_sind_ein_konflikt_ohne_gueltigen_stand(world):
    world.decide("dec-1", "ms-a", "erreicht", "2026-02-01")
    world.decide("dec-2", "ms-a", "nicht_erreicht", "2026-02-01")
    milestone = world.goal()["milestones"][0]
    assert milestone["decision"] is None
    assert milestone["status"] == "offen"
    assert milestone["conflict"] == ["dec-1", "dec-2"]


def test_nachfolger_darf_nicht_aelter_sein(world):
    world.decide("dec-1", "ms-a", "erreicht", "2026-02-01")
    world.decide("dec-2", "ms-a", "nicht_erreicht", "2026-01-15", supersedes="dec-1")
    assert has(world.errors(), "dec-2", "älter als ihr Vorgänger")


def test_nachfolger_muss_denselben_gegenstand_betreffen(world):
    world.decide("dec-1", "ms-a", "erreicht", "2026-02-01")
    world.decide("dec-2", "ms-b", "erreicht", "2026-03-01", supersedes="dec-1")
    assert has(world.errors(), "dec-2", "anderen Gegenstand")


def test_kreis_in_der_nachfolge_wird_erkannt(world):
    world.decide("dec-1", "ms-a", "erreicht", "2026-02-01", supersedes="dec-2")
    world.decide("dec-2", "ms-a", "erreicht", "2026-02-01", supersedes="dec-1")
    assert has(world.errors(), "Kreis")


# --- Unabhängigkeit und Doppelzählung (docs/02, docs/03) --------------------


def ligo(world):
    """Zwei Ereignisse, drei Veröffentlichungen, ein Team, ein Instrument."""
    for sid in ("st-ereignis-a", "st-ereignis-b", "st-gesamt"):
        world.study(sid, team="kollaboration", instrument="detektor")
    world.dataset("gw-a")
    world.dataset("gw-b")
    world.evidence("ev-a", study="st-ereignis-a", event_ids=["gw-a"])
    world.evidence("ev-b", study="st-ereignis-b", event_ids=["gw-b"])
    world.evidence("ev-c", study="st-gesamt", event_ids=["gw-a", "gw-b"])


def test_gemeinsame_auswertung_zaehlt_die_ereignisse_nur_einmal(world):
    ligo(world)
    world.decide("dec-1", "cl-a", "mehrfach_gestuetzt", "2026-02-01",
                 evidence_ids=["ev-a", "ev-b", "ev-c"], assurance=["neue_daten"])
    claim = world.claim()
    assert claim["supporting_sources"] == 3, "alle drei Veröffentlichungen bleiben als Quellen sichtbar"
    assert claim["supporting_observations"] == 2, "gezählt werden die zwei Ereignisse"
    assert claim["shared_dependencies"] == ["Team: kollaboration", "Instrument: detektor"]


def test_zwei_veroeffentlichungen_zu_einer_beobachtung_sind_nicht_mehrfach_gestuetzt(world):
    world.study("st-zwei", team="team-zwei")
    world.evidence("ev-b", study="st-zwei")
    world.decide("dec-1", "cl-a", "mehrfach_gestuetzt", "2026-02-01", evidence_ids=["ev-a", "ev-b"])
    assert has(world.errors(), "dec-1", "zwei verschiedenen Grundlagen")


def test_ausschnitt_desselben_rohlogs_ist_keine_neue_beobachtung(world):
    world.dataset("ds-ausschnitt", derived_from="ds-eins")
    world.study("st-zwei", team="team-zwei")
    world.evidence("ev-b", study="st-zwei", dataset_id="ds-ausschnitt")
    world.decide("dec-1", "cl-a", "mehrfach_gestuetzt", "2026-02-01", evidence_ids=["ev-a", "ev-b"])
    assert has(world.errors(), "dec-1", "zwei verschiedenen Grundlagen")


def test_zwei_unabhaengige_datensaetze_sind_mehrfach_gestuetzt(world):
    world.dataset("ds-zwei")
    world.study("st-zwei", team="team-zwei")
    world.evidence("ev-b", study="st-zwei", dataset_id="ds-zwei")
    world.decide("dec-1", "cl-a", "mehrfach_gestuetzt", "2026-02-01", evidence_ids=["ev-a", "ev-b"])
    claim = world.claim()
    assert claim["evidence_status"] == "mehrfach_gestuetzt"
    assert claim["shared_dependencies"] == []


def test_evidenzlage_muss_zu_den_belegen_passen(world):
    world.decide("dec-1", "cl-a", "spricht_dagegen", "2026-02-01")
    assert has(world.errors(), "dec-1", "Gegenbeleg")


def test_ein_beleg_mit_zwei_ereignissen_ist_nicht_mehrfach_gestuetzt(world):
    world.dataset("gw-a")
    world.dataset("gw-b")
    world.evidence("ev-a", event_ids=["gw-a", "gw-b"])
    world.decide("dec-1", "cl-a", "mehrfach_gestuetzt", "2026-02-01")
    assert has(world.errors(), "dec-1", "zwei stützende Belege")


def test_zwei_verschiedene_beweise_sind_zwei_grundlagen(world):
    """Mathematik: Ein Beweis ist die Grundlage, auf der ein Beleg beruht."""
    world.dataset("beweis-eins", kind="beweis")
    world.dataset("beweis-zwei", kind="beweis")
    world.study("st-zwei", team="team-zwei")
    world.evidence("ev-a", basis_ids=["beweis-eins"])
    world.evidence("ev-b", study="st-zwei", basis_ids=["beweis-zwei"])
    world.decide("dec-1", "cl-a", "mehrfach_gestuetzt", "2026-02-01",
                 evidence_ids=["ev-a", "ev-b"], assurance=["beweisreview"])
    claim = world.claim()
    assert (claim["supporting_sources"], claim["supporting_observations"]) == (2, 2)
    assert claim["evidence"][0]["basis"][0]["kind"] == "beweis"


def test_derselbe_beweis_in_zwei_veroeffentlichungen_zaehlt_einmal(world):
    world.dataset("beweis-eins", kind="beweis")
    world.study("st-zwei", team="team-zwei")
    world.evidence("ev-a", basis_ids=["beweis-eins"])
    world.evidence("ev-b", study="st-zwei", basis_ids=["beweis-eins"])
    world.decide("dec-1", "cl-a", "mehrfach_gestuetzt", "2026-02-01", evidence_ids=["ev-a", "ev-b"])
    assert has(world.errors(), "dec-1", "zwei verschiedenen Grundlagen")


def test_unbekannte_grundlage_stoppt(world):
    world.evidence("ev-b", basis_ids=["beweis-fehlt"])
    assert has(world.errors(), "ev-b", "unbekannte Grundlage")


def test_zurueckgezogene_studie_stuetzt_nichts_mehr(world):
    world.study("st-eins", status="zurueckgezogen", status_date="2026-01-15", status_note="Nicht reproduzierbar")
    claim = world.claim()
    assert claim["supporting_sources"] == 0
    assert claim["evidence"][0]["counts_as_support"] is False
    world.decide("dec-1", "cl-a", "vorlaeufig_gestuetzt", "2026-02-01")
    assert has(world.errors(), "dec-1", "nicht zurückgezogenen Studie")


# --- Vorschläge --------------------------------------------------------------


def test_vorschlag_ist_sichtbar_und_zaehlt_nicht(world):
    world.decide("dec-1", "ms-a", "erreicht", "2026-02-01", status="vorgeschlagen",
                 suggested_by="Sprachmodell", extracted_by=None, reviewed_by=None)
    goal = world.goal()
    assert goal["display"] == "0 von 4"
    assert goal["milestones_proposed"] == 1
    assert goal["milestones"][0]["open_proposals"][0]["suggested_by"] == "Sprachmodell"
    assert world.state()["history"][-1]["type"] == "katalog", "Vorschläge stehen nicht im Verlauf"


def test_auch_ein_vorschlag_muss_zu_den_belegen_passen(world):
    world.decide("dec-1", "cl-a", "mehrfach_gestuetzt", "2026-02-01", status="vorgeschlagen")
    assert has(world.errors(), "dec-1", "zwei stützende Belege")


def test_sprachmodell_ersetzt_keine_der_zwei_personen(world):
    world.decide("dec-1", "ms-a", "erreicht", "2026-02-01", suggested_by="Sprachmodell", extracted_by=None)
    assert has(world.errors(), "dec-1", "zwei verschiedenen Personen")


def test_vorgeschlagene_entscheidung_macht_die_aussage_nicht_zu_in_pruefung(world):
    world.decide("dec-1", "cl-a", "vorlaeufig_gestuetzt", "2026-02-01", status="vorgeschlagen")
    claim = world.claim()
    assert claim["editorial_status"] == "vorgeschlagen"
    assert (claim["evidence_status"], claim["proposed_status"]) == ("offen", "vorlaeufig_gestuetzt")


# --- Neubewertung (docs/02, Schritt 6) --------------------------------------


def test_neuer_beleg_loest_eine_erneute_pruefung_aus(world):
    world.decide("dec-1", "cl-a", "vorlaeufig_gestuetzt", "2026-02-01")
    assert world.claim()["editorial_status"] == "freigegeben"
    world.study("st-zwei", team="team-zwei")
    world.evidence("ev-b", study="st-zwei", relation="spricht_dagegen", released=False)
    claim = world.claim()
    assert claim["editorial_status"] == "erneut_zu_pruefen"
    assert claim["evidence_status"] == "vorlaeufig_gestuetzt", "die alte Einstufung gilt bis zur neuen Entscheidung"
    assert "ev-b" in claim["reexamine"][0]


def test_korrigierte_messung_ueberholt_den_urspruenglichen_befund(world):
    """Das Muster des OPERA-Beispiels aus docs/04, mit erfundenen Daten."""
    world.decide("dec-1", "cl-a", "vorlaeufig_gestuetzt", "2026-02-01")
    world.study("st-eins", status="korrigiert", status_date="2026-03-01",
                status_note="Fehler in der Zeitmessung gefunden")
    claim = world.claim()
    assert claim["editorial_status"] == "erneut_zu_pruefen"
    assert "korrigiert" in claim["reexamine"][0]

    world.study("st-korrektur")
    world.evidence("ev-b", study="st-korrektur", relation="spricht_dagegen")
    world.decide("dec-2", "cl-a", "spricht_dagegen", "2026-04-01", supersedes="dec-1",
                 evidence_ids=["ev-a", "ev-b"], assurance=["nachrechnung"])
    state = world.state()
    claim = state["claims"][0]
    assert claim["evidence_status"] == "spricht_dagegen"
    assert claim["editorial_status"] == "freigegeben"
    assert [d["outcome"] for d in claim["earlier_decisions"]] == ["vorlaeufig_gestuetzt"]
    last = state["history"][-1]
    assert (last["old"], last["new"]) == (["vorlaeufig_gestuetzt"], "spricht_dagegen")


def test_nullergebnis_kann_einen_meilenstein_erfuellen(world):
    """docs/05: Ein präzises Nullergebnis erfüllt 'Übertragbarkeit testen'."""
    world.evidence("ev-a", relation="spricht_dagegen")
    world.decide("dec-1", "cl-a", "spricht_dagegen", "2026-02-01", assurance=["neue_daten"])
    world.decide("dec-2", "ms-a", "erreicht", "2026-02-01", assurance=["neue_daten"])
    state = world.state()
    assert state["goals"][0]["display"] == "1 von 4"
    assert state["claims"][0]["evidence_status"] == "spricht_dagegen"


def test_dissens_bleibt_sichtbar_und_der_vorschlag_offen(world):
    world.decide("dec-1", "cl-a", "vorlaeufig_gestuetzt", "2026-02-01", status="in_pruefung",
                 dissent="Die zweite Person hält den Vergleich für nicht entscheidend.")
    claim = world.claim()
    assert claim["editorial_status"] == "in_pruefung"
    assert claim["evidence_status"] == "offen"
    assert claim["open_proposals"][0]["dissent"].startswith("Die zweite Person")


# --- Ausgabe -----------------------------------------------------------------


def test_ausgabe_ist_wiederholbar(world, tmp_path):
    world.decide("dec-1", "ms-a", "erreicht", "2026-02-01")
    first, second = tmp_path / "eins", tmp_path / "zwei"
    for out in (first, second):
        assert atlas.main(["build", "--data", str(world.root), "--out", str(out)]) == 0
    for name in ("progress.json", "history.json", "index.html"):
        assert (first / name).read_bytes() == (second / name).read_bytes()
    progress = json.loads((first / "progress.json").read_text(encoding="utf-8"))
    assert progress["goals"][0]["display"] == "1 von 4"
