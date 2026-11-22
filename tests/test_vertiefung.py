"""Vertiefung: bestehende Ziele wachsen, statt dass neue Fachgebiete dazukommen."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

import atlas

ROOT = Path(__file__).resolve().parent.parent
EXTENDED = {  # Ziel: (neue Meilensteine in Katalog v2, Stand nach Freigabe aller Vorschläge)
    "goal-higgs-boson": (["ms-higgs-bottom", "ms-higgs-bottom-zweites-experiment"], "5 von 5"),
    "goal-proteinstruktur-vorhersage": (
        ["ms-protein-datenbank", "ms-protein-komplexe", "ms-protein-komplexe-unabhaengig"], "4 von 5"),
    "goal-quantenueberlegenheit": (["ms-qc-zweite-plattform", "ms-qc-groesserer-prozessor"], "3 von 4")}


def by_id(items: list[dict], wanted: str) -> dict:
    return next(i for i in items if i["id"] == wanted)


# Ein Ziel bekommt weitere Meilensteine ------------------------------------------

@pytest.mark.parametrize("goal_id", sorted(EXTENDED))
def test_weitere_meilensteine_kommen_als_neue_katalogversion(real_atlas, real_state, goal_id):
    added = EXTENDED[goal_id][0]
    first, second = real_atlas.goals[goal_id]["catalog"]
    assert (first["version"], second["version"]) == (1, 2)
    assert second["milestones"] == first["milestones"] + added, "v2 behält alle Meilensteine aus v1"
    goal = by_id(real_state["goals"], goal_id)
    assert goal["catalog_version"] == 2 and len(goal["milestones"]) == len(second["milestones"])


@pytest.mark.parametrize("goal_id", sorted(EXTENDED))
def test_vorschlaege_aus_katalog_v1_bleiben_bei_ihrem_meilenstein(real_atlas, real_state, goal_id):
    old = real_atlas.goals[goal_id]["catalog"][0]["milestones"]
    goal = by_id(real_state["goals"], goal_id)
    for milestone in goal["milestones"]:
        versions = {real_atlas.decisions[p["id"]]["catalog_version"] for p in milestone["open_proposals"]}
        assert versions <= ({1} if milestone["id"] in old else {2}), milestone["id"]
    assert all(by_id(goal["milestones"], mid)["open_proposals"] for mid in old)


@pytest.mark.parametrize("goal_id", sorted(EXTENDED))
def test_verlauf_nennt_die_neue_katalogversion_mit_begruendung(real_state, real_site, goal_id):
    event = next(h for h in real_state["history"]
                 if h["type"] == "katalog" and h["goal_ids"] == [goal_id] and h["subject"] == "Zielkatalog v2")
    assert event["added"] == EXTENDED[goal_id][0] and event["removed"] == [] and event["reason"]
    assert event["reason"] in (real_site / "verlauf.html").read_text(encoding="utf-8")


def test_vorschlag_fuer_falsche_katalogversion_stoppt(tmp_path):
    """Ein Meilenstein aus v2 lässt sich nicht mit Katalog v1 entscheiden."""
    data = tmp_path / "data"
    shutil.copytree(ROOT / "data", data)
    path = next((data / "decisions").glob("*ms-higgs-bottom.yaml"))
    record = yaml.safe_load(path.read_text(encoding="utf-8")) | {"catalog_version": 1}
    path.write_text(yaml.safe_dump(record, allow_unicode=True, sort_keys=False), encoding="utf-8")
    errors = atlas.load_checked(data)[1]
    assert any("ms-higgs-bottom gehört nicht zu Katalog v1" in e for e in errors), errors


# Offene Meilensteine werden gefüllt ----------------------------------------------

def test_zweite_studie_einer_anderen_gruppe_schliesst_den_meilenstein(real_state):
    for claim_id, goal_id, milestone_id in [
            ("cl-hpylori-rueckfall", "goal-helicobacter-geschwuer", "ms-hpylori-zweite-studie"),
            ("cl-knobe-nebenfolgen", "goal-knobe-effekt", "ms-knobe-replikation")]:
        claim = by_id(real_state["claims"], claim_id)
        assert (claim["supporting_sources"], claim["supporting_observations"]) == (2, 2), claim_id
        assert claim["proposed_status"] == "mehrfach_gestuetzt" and claim["shared_dependencies"] == []
        assert by_id(by_id(real_state["goals"], goal_id)["milestones"], milestone_id)["state"] == "proposed"


def test_zwei_verfahren_auf_denselben_texten_sind_eine_grundlage(real_state, real_site):
    claim = by_id(real_state["claims"], "cl-federalist-madison")
    assert (claim["supporting_sources"], claim["supporting_observations"]) == (2, 1)
    assert claim["proposed_status"] == "vorlaeufig_gestuetzt"
    goal = by_id(real_state["goals"], "goal-federalist-autorschaft")
    assert [m["state"] for m in goal["milestones"]] == ["proposed", "proposed"]
    assert "2 Quellen, 1 Datensatz." in (real_site / "aussagen" / "cl-federalist-madison.html").read_text(encoding="utf-8")


def test_zweite_studie_desselben_teams_laesst_den_meilenstein_offen(real_state):
    claim = by_id(real_state["claims"], "cl-haustuer-transphobie")
    assert claim["proposed_status"] == "mehrfach_gestuetzt"
    assert claim["shared_dependencies"] == ["Team: broockman-kalla"]
    goal = by_id(real_state["goals"], "goal-haustuergespraeche")
    assert by_id(goal["milestones"], "ms-haustuer-anderes-team")["state"] == "open"


def test_verlauf_ueber_drei_jahre_erfuellt_das_kriterium_von_fuenf_nicht(real_state):
    goal = by_id(real_state["goals"], "goal-car-t-leukaemie")
    milestone = by_id(goal["milestones"], "ms-cart-fuenf-jahre")
    assert milestone["state"] == "open" and milestone["claims"] == ["cl-cart-drei-jahre"]
    assert "drei Jahre" in milestone["note"] and "fünf" in milestone["note"]
    assert by_id(real_state["claims"], "cl-cart-drei-jahre")["proposed_status"] == "vorlaeufig_gestuetzt"


def test_je_ziel_und_aussage_steht_nur_ein_offener_vorschlag(real_state):
    """Ein eigener, noch ungeprüfter Vorschlag wird ersetzt und nicht gestapelt."""
    for claim in real_state["claims"]:
        assert len(claim["open_proposals"]) <= 1, claim["id"]
    for goal in real_state["goals"]:
        for milestone in goal["milestones"]:
            assert len(milestone["open_proposals"]) <= 1, milestone["id"]


# Ein Teilgebiet bekommt ein zweites Ziel ------------------------------------------

def test_teilgebiet_gravitationswellen_hat_zwei_ziele(real_state, real_site):
    physics = next(a for r in real_state["realms"] for a in r["areas"] if a["code"] == "103")
    topic = by_id([t | {"id": t["name"]} for t in physics["topics"]], "Gravitationswellen")
    assert topic["goal_ids"] == ["goal-gravitationswellen-neutronensterne", "goal-gravitationswellen-schwarze-loecher"]
    assert topic["tally"]["milestones"]["total"] == 7
    page = (real_site / "thema" / "103-gravitationswellen.html").read_text(encoding="utf-8")
    assert all(f"../ziele/{goal_id}.html" in page for goal_id in topic["goal_ids"])


def test_ein_beleg_kann_zwei_ereignisse_als_grundlage_haben(real_state):
    claim = by_id(real_state["claims"], "cl-gwns-gammablitz")
    assert [sorted(b["id"] for b in ev["basis"]) for ev in claim["evidence"]] == [["grb170817a", "gw170817"]]
    assert {b["kind"] for ev in claim["evidence"] for b in ev["basis"]} == {"ereignis"}


# Durchgespielt ---------------------------------------------------------------------

@pytest.fixture(scope="module")
def approved(tmp_path_factory) -> dict:
    """Zwei Personen geben jeden Vorschlag frei."""
    data = tmp_path_factory.mktemp("vertiefung-freigabe") / "data"
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


@pytest.mark.parametrize("goal_id, display", [(g, d) for g, (_, d) in sorted(EXTENDED.items())] + [
    ("goal-gravitationswellen-neutronensterne", "2 von 3")])
def test_nach_freigabe_zaehlen_alte_und_neue_meilensteine_zusammen(approved, goal_id, display):
    assert by_id(approved["goals"], goal_id)["display"] == display


def test_nach_freigabe_zeigt_die_kurve_den_sprung_beim_katalogwechsel(approved):
    last = approved["series"][-1]
    assert last["total"] == approved["totals"]["milestones"]["total"]
    assert last["reached"] == approved["totals"]["milestones"]["reached"] > 0
