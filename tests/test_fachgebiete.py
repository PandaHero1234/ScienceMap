"""Die drei Fachgebiete Physik, Mathematik und Biologie mit den echten Daten unter data/.

Alle Einträge sind Vorschläge eines Sprachmodells. Der zweite Teil spielt durch, was
passiert, wenn zwei Personen jeden Vorschlag freigeben.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

import atlas

ROOT = Path(__file__).resolve().parent.parent
GW = "goal-gravitationswellen-schwarze-loecher"
PRIM = "goal-primzahlluecken"
CAS9 = "goal-cas9-genom-editierung"
NGAGO = "goal-ngago-genom-editierung"


def by_id(items: list[dict], wanted: str) -> dict:
    return next(i for i in items if i["id"] == wanted)


@pytest.fixture(scope="module")
def state() -> dict:
    loaded, errors = atlas.load_checked(ROOT / "data")
    assert errors == []
    return atlas.build_state(loaded)


# --- Stand heute: nur Vorschläge ---------------------------------------------


@pytest.mark.parametrize("goal_id, field, total, proposed", [
    (GW, "Physik", 4, 4), (PRIM, "Mathematik", 5, 4), (CAS9, "Biologie", 4, 4), (NGAGO, "Biologie", 2, 0)])
def test_ohne_zweitpruefung_ist_kein_meilenstein_erreicht(state, goal_id, field, total, proposed):
    goal = by_id(state["goals"], goal_id)
    assert goal["field"] == field
    assert (goal["milestones_reached"], goal["milestones_total"]) == (0, total)
    assert goal["milestones_proposed"] == proposed
    assert goal["claims_reviewed"] == 0


def test_das_sprachmodell_hat_nichts_freigegeben():
    loaded, _ = atlas.load_checked(ROOT / "data")
    for record in list(loaded.evidence.values()) + list(loaded.decisions.values()):
        if record.get("suggested_by"):
            assert record.get("review_status", record.get("status")) == "vorgeschlagen", record["id"]
            assert "reviewed_by" not in record, record["id"]


def test_physik_drei_quellen_zwei_ereignisse(state):
    claim = by_id(state["claims"], "cl-gw-zwei-ereignisse")
    assert (claim["supporting_sources"], claim["supporting_observations"]) == (3, 2)
    assert claim["shared_dependencies"] == ["Team: ligo-virgo-kollaboration", "Instrument: ligo"]
    assert claim["proposed_status"] == "mehrfach_gestuetzt"


def test_physik_zweite_auswertung_ist_keine_neue_beobachtung(state):
    claim = by_id(state["claims"], "cl-gw150914-nachweis")
    assert (claim["supporting_sources"], claim["supporting_observations"]) == (2, 1)
    assert claim["proposed_status"] == "vorlaeufig_gestuetzt"


def test_mathematik_zwei_beweise_und_ein_offener_meilenstein(state):
    claim = by_id(state["claims"], "cl-primluecken-endliche-schranke")
    assert (claim["supporting_sources"], claim["supporting_observations"]) == (2, 2)
    assert {b["kind"] for ev in claim["evidence"] for b in ev["basis"]} == {"beweis"}
    twin = by_id(by_id(state["goals"], PRIM)["milestones"], "ms-zwillingsprimzahlen")
    assert twin["status"] == "offen" and twin["open_proposals"] == [] and twin["claims"] == []


def test_mathematik_schwaechere_schranke_entscheidet_die_aussage_nicht(state):
    claim = by_id(state["claims"], "cl-primluecken-6-bedingt")
    relations = {ev["id"]: ev["relation"] for ev in claim["evidence"]}
    assert relations["ev-primluecken-maynard-eh-12"] == "nicht_entscheidend"
    assert claim["supporting_sources"] == 1


def test_biologie_drei_veroeffentlichungen_aus_zwei_studien(state):
    claim = by_id(state["claims"], "cl-cas9-klinische-wirksamkeit")
    assert (claim["supporting_sources"], claim["supporting_observations"]) == (3, 2)
    assert claim["shared_dependencies"] == ["Team: vertex-und-crispr-therapeutics"]


def test_biologie_zurueckgezogene_studie_zaehlt_nicht(state):
    claim = by_id(state["claims"], "cl-ngago-editierung-humanzellen")
    assert claim["supporting_sources"] == 0
    gao = by_id(claim["evidence"], "ev-ngago-gao-2016")
    assert gao["study"]["status"] == "zurueckgezogen" and gao["counts_as_support"] is False
    assert claim["proposed_status"] == "spricht_dagegen"


def test_seiten_zeigen_vorschlaege_und_fachbezeichnungen(tmp_path):
    assert atlas.main(["build", "--out", str(tmp_path)]) == 0
    index = (tmp_path / "ziele.html").read_text(encoding="utf-8")
    assert index.count("</strong> Meilensteinen erreicht · 4 vorgeschlagen") == 3
    assert "0 von 2</strong> Meilensteinen erreicht · 2 als nicht erreicht vorgeschlagen" in index
    mathe = (tmp_path / "aussagen" / "cl-primluecken-endliche-schranke.html").read_text(encoding="utf-8")
    assert "Vorschlag: bewiesen (mehrere Beweise)" in mathe
    assert "2 Quellen, 2 Beweise." in mathe
    ngago = (tmp_path / "aussagen" / "cl-ngago-editierung-humanzellen.html").read_text(encoding="utf-8")
    assert "Zurückgezogen, zählt nicht mehr" in ngago
    assert "Keine stützende Quelle." in ngago


# --- Durchgespielt: zwei Personen geben jeden Vorschlag frei ------------------


@pytest.fixture(scope="module")
def approved(tmp_path_factory) -> dict:
    data = tmp_path_factory.mktemp("freigabe") / "data"
    shutil.copytree(ROOT / "data", data)
    people = {"extracted_by": "Erste Person", "reviewed_by": "Zweite Person"}
    for path in (data / "evidence").glob("*.yaml"):
        record = yaml.safe_load(path.read_text(encoding="utf-8")) | people | {"review_status": "freigegeben"}
        path.write_text(yaml.safe_dump(record, allow_unicode=True, sort_keys=False), encoding="utf-8")
    for path in (data / "decisions").glob("*.yaml"):
        record = yaml.safe_load(path.read_text(encoding="utf-8")) | people | {
            "status": "freigegeben", "assurance": ["quellenabgleich"]}
        path.write_text(yaml.safe_dump(record, allow_unicode=True, sort_keys=False), encoding="utf-8")
    loaded, errors = atlas.load_checked(data)
    assert errors == [], errors
    return atlas.build_state(loaded)


@pytest.mark.parametrize("goal_id, display", [
    (GW, "4 von 4"), (PRIM, "4 von 5"), (CAS9, "4 von 4"), (NGAGO, "0 von 2"), ("goal-discovery-fscore", "0 von 4")])
def test_nach_freigabe_steht_der_zaehler_wie_vorgeschlagen(approved, goal_id, display):
    goal = by_id(approved["goals"], goal_id)
    assert goal["display"] == display
    assert goal["milestones_proposed"] == 0


def test_nach_freigabe_sind_alle_aussagen_der_drei_faecher_eingestuft(approved):
    expected = {
        "cl-gw150914-nachweis": "vorlaeufig_gestuetzt",
        "cl-gw-zwei-ereignisse": "mehrfach_gestuetzt",
        "cl-primluecken-endliche-schranke": "mehrfach_gestuetzt",
        "cl-primluecken-6-bedingt": "vorlaeufig_gestuetzt",
        "cl-cas9-editierung-humanzellen": "mehrfach_gestuetzt",
        "cl-cas9-klinische-wirksamkeit": "vorlaeufig_gestuetzt",
        "cl-ngago-editierung-humanzellen": "spricht_dagegen",
    }
    for claim_id, outcome in expected.items():
        claim = by_id(approved["claims"], claim_id)
        assert claim["evidence_status"] == outcome, claim_id
        assert claim["editorial_status"] == "freigegeben", (claim_id, claim["reexamine"])
        assert claim["conflict"] == []


def test_nach_freigabe_stimmt_der_gesamtstand(approved):
    assert approved["totals"]["milestones"] == {
        "total": 19, "reached": 12, "proposed": 0, "proposed_failed": 0, "failed": 2, "open": 5}
    assert approved["totals"]["claims"] == {"total": 12, "reviewed": 11}
    assert approved["totals"]["evidence"] == {"total": 21, "reviewed": 21}


def test_nach_freigabe_steht_jede_entscheidung_im_verlauf(approved):
    decisions = [e for e in approved["history"] if e["type"] == "entscheidung"]
    assert len(decisions) == 25
    ngago = by_id([{"id": e["decision_id"], **e} for e in decisions], "dec-2026-11-21-ms-ngago-erstbefund")
    assert ngago["new"] == "nicht_erreicht"
    assert ngago["sources"][0]["study"].startswith("Gao et al.")
