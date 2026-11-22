"""Der Ausbau in alle sechs Bereiche: zwölf weitere Ziele, alle als Vorschläge."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

import atlas

ROOT = Path(__file__).resolve().parent.parent


def by_id(items: list[dict], wanted: str) -> dict:
    return next(i for i in items if i["id"] == wanted)


def relations(claim: dict) -> list[str]:
    return sorted(ev["relation"] for ev in claim["evidence"])


def test_zwei_experimente_stuetzen_das_neue_boson(real_state):
    claim = by_id(real_state["claims"], "cl-higgs-neues-boson")
    assert (claim["supporting_sources"], claim["supporting_observations"]) == (2, 2)
    assert claim["proposed_status"] == "mehrfach_gestuetzt"
    assert claim["shared_dependencies"] == [], "zwei Kollaborationen mit eigenen Detektoren"


def test_formale_pruefung_ist_kein_zweiter_beweis(real_state, real_site):
    claim = by_id(real_state["claims"], "cl-kepler-dichte")
    assert (claim["supporting_sources"], claim["supporting_observations"]) == (2, 1)
    assert claim["proposed_status"] == "vorlaeufig_gestuetzt"
    page = (real_site / "aussagen" / "cl-kepler-dichte.html").read_text(encoding="utf-8")
    assert "Vorschlag: bewiesen (ein Beweis)" in page and "2 Quellen, 1 Beweis." in page


def test_zwei_phase_3_studien_verschiedener_sponsoren(real_state):
    claim = by_id(real_state["claims"], "cl-mrna-phase3-wirksam")
    assert (claim["supporting_sources"], claim["supporting_observations"]) == (2, 2)
    assert {b["kind"] for ev in claim["evidence"] for b in ev["basis"]} == {"klinische_studie"}
    assert claim["proposed_status"] == "mehrfach_gestuetzt" and claim["shared_dependencies"] == []


def test_zurueckgezogene_kinderstudie_laesst_die_aussage_offen(real_state):
    claim = by_id(real_state["claims"], "cl-reis-kinder")
    assert claim["supporting_sources"] == 0 and claim["proposed_status"] == "offen"
    goal = by_id(real_state["goals"], "goal-goldener-reis")
    assert by_id(goal["milestones"], "ms-reis-kinder")["state"] == "proposed-failed"
    assert goal["milestones_proposed"] == 3


def test_erstbefund_und_replikationen_widersprechen_sich(real_state):
    claim = by_id(real_state["claims"], "cl-ego-depletion")
    assert relations(claim) == ["spricht_dagegen", "spricht_dagegen", "stuetzt"]
    assert claim["proposed_status"] == "widerspruechlich"


def test_nachrechnung_auf_demselben_datensatz_spricht_dagegen(real_state):
    claim = by_id(real_state["claims"], "cl-rr-wachstum-ueber-90")
    assert relations(claim) == ["spricht_dagegen", "stuetzt"]
    assert {b["id"] for ev in claim["evidence"] for b in ev["basis"]} == {"rr-datensatz"}
    assert claim["proposed_status"] == "spricht_dagegen"


def test_ueberholte_schaetzung_des_klassischen_aufwands(real_state):
    goal = by_id(real_state["goals"], "goal-quantenueberlegenheit")
    assert [m["state"] for m in goal["milestones"]] == ["proposed", "proposed-failed"]
    assert by_id(real_state["claims"], "cl-sycamore-klassischer-aufwand")["proposed_status"] == "spricht_dagegen"


def test_offener_meilenstein_ohne_beleg_bleibt_offen(real_state):
    goal = by_id(real_state["goals"], "goal-richard-iii")
    second = by_id(goal["milestones"], "ms-r3-zweite-gruppe")
    assert second["state"] == "open" and second["claims"] == []


def test_neue_teilgebiete_in_bestehenden_faechern(real_state):
    topics = {a["name"]: [t["name"] for t in a["topics"]] for r in real_state["realms"] for a in r["areas"] if a["topics"]}
    assert topics["Mathematik"] == ["Kugelpackungen", "Primzahlverteilung"]
    assert topics["Informatik"] == ["Process Mining", "Quantenüberlegenheit"]
    assert topics["Physik, Astronomie"] == ["Gravitationswellen", "Higgs-Boson"]
    assert topics["Biologie"] == ["Genom-Editierung", "Proteinstrukturvorhersage"]


@pytest.fixture(scope="module")
def approved(tmp_path_factory) -> dict:
    """Durchgespielt: Zwei Personen geben jeden Vorschlag frei."""
    data = tmp_path_factory.mktemp("ausbau-freigabe") / "data"
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
    ("goal-higgs-boson", "3 von 3"), ("goal-kepler-vermutung", "2 von 2"), ("goal-proteinstruktur-vorhersage", "2 von 2"),
    ("goal-element-117", "2 von 2"), ("goal-kreide-einschlag", "3 von 3"), ("goal-mrna-impfstoff", "3 von 3"),
    ("goal-goldener-reis", "3 von 4"), ("goal-ego-depletion", "1 von 2"), ("goal-schulden-wachstum", "1 von 2"),
    ("goal-richard-iii", "1 von 2"), ("goal-lk99-supraleitung", "1 von 2"), ("goal-quantenueberlegenheit", "1 von 2")])
def test_nach_freigabe_steht_jedes_neue_ziel_wie_vorgeschlagen(approved, goal_id, display):
    assert by_id(approved["goals"], goal_id)["display"] == display


def test_nach_freigabe_bleibt_keine_aussage_im_widerspruch_zu_ihren_belegen(approved):
    for claim in approved["claims"]:
        assert claim["conflict"] == [] and claim["reexamine"] == [], claim["id"]
