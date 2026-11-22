"""Zweite Ausbaustufe: fünfzehn weitere Ziele in vierzehn neuen Fachgebieten, alle als Vorschläge."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import pytest
import yaml

import atlas

ROOT = Path(__file__).resolve().parent.parent

NEW_GOALS = {
    "goal-graphen": ("210", "3 von 3"), "goal-memristor": ("202", "1 von 2"),
    "goal-helicobacter-geschwuer": ("302", "3 von 3"), "goal-rauchen-lungenkrebs": ("303", "3 von 3"),
    "goal-car-t-leukaemie": ("304", "2 von 3"), "goal-neonicotinoide-bienen": ("401", "2 von 3"),
    "goal-bse-creutzfeldt-jakob": ("403", "3 von 3"), "goal-klonen-saeugetier": ("402", "3 von 3"),
    "goal-growth-mindset": ("503", "1 von 2"), "goal-bewerbung-benachteiligung": ("504", "3 von 3"),
    "goal-haustuergespraeche": ("506", "1 von 2"), "goal-federalist-autorschaft": ("602", "2 von 2"),
    "goal-knobe-effekt": ("603", "2 von 2"), "goal-bleiweiss-datierung": ("604", "1 von 2"),
    "goal-pet-enzymabbau": ("209", "3 von 3")}


def by_id(items: list[dict], wanted: str) -> dict:
    return next(i for i in items if i["id"] == wanted)


def relations(claim: dict) -> list[str]:
    return sorted(ev["relation"] for ev in claim["evidence"])


def states(real_state: dict, goal_id: str) -> list[str]:
    return [m["state"] for m in by_id(real_state["goals"], goal_id)["milestones"]]


# Abdeckung -------------------------------------------------------------------

def test_jedes_neue_ziel_liegt_im_genannten_fachgebiet(real_atlas):
    for goal_id, (area, _) in NEW_GOALS.items():
        assert real_atlas.goals[goal_id]["area"] == area, goal_id


def test_jeder_bereich_hat_mindestens_drei_fachgebiete_mit_zielen(real_state):
    for realm in real_state["realms"]:
        covered = [a for a in realm["areas"] if a["goal_ids"]]
        assert len(covered) >= 3, realm["name"]


def test_alles_neue_ist_vorschlag_eines_sprachmodells(real_atlas):
    wanted = set(NEW_GOALS)
    milestones = {m["id"] for g in wanted for m in real_atlas.goals[g]["milestones"]}
    claims = {c["id"] for c in real_atlas.claims.values() if set(c["milestone_ids"]) & milestones}
    evidence = [e for e in real_atlas.evidence.values() if e["claim_id"] in claims]
    decisions = [d for d in real_atlas.decisions.values() if d["target_id"] in milestones | claims]
    assert len(claims) >= 23 and len(evidence) >= 38 and len(decisions) >= 55
    assert {e["review_status"] for e in evidence} == {"vorgeschlagen"}
    assert {d["status"] for d in decisions} == {"vorgeschlagen"}
    assert {r["suggested_by"] for r in evidence + decisions} == {"Sprachmodell"}
    assert not any("extracted_by" in r or "reviewed_by" in r for r in evidence + decisions)


# Einzelne Fälle ----------------------------------------------------------------

def test_zwei_gruppen_mit_eigenen_proben(real_state):
    claim = by_id(real_state["claims"], "cl-graphen-dirac")
    assert (claim["supporting_sources"], claim["supporting_observations"]) == (2, 2)
    assert claim["proposed_status"] == "mehrfach_gestuetzt" and claim["shared_dependencies"] == []


def test_streit_um_die_einordnung_derselben_bauelemente(real_state):
    claim = by_id(real_state["claims"], "cl-memristor-chua")
    assert relations(claim) == ["spricht_dagegen", "stuetzt"]
    assert {b["id"] for ev in claim["evidence"] for b in ev["basis"]} == {"exp-strukov-2008"}
    assert claim["proposed_status"] == "widerspruechlich"
    assert states(real_state, "goal-memristor") == ["proposed", "proposed-failed"]


def test_drei_grundlagen_stuetzen_dieselbe_aussage(real_state):
    for claim_id in ("cl-rauchen-lungenkrebs", "cl-dolly-herkunft", "cl-bewerbung-rueckmeldungen"):
        claim = by_id(real_state["claims"], claim_id)
        assert (claim["supporting_sources"], claim["supporting_observations"]) == (3, 3), claim_id
        assert claim["proposed_status"] == "mehrfach_gestuetzt"


def test_zwei_studien_derselben_arbeitsgruppe_werden_benannt(real_state, real_site):
    claim = by_id(real_state["claims"], "cl-cart-remission")
    assert claim["proposed_status"] == "mehrfach_gestuetzt"
    assert claim["shared_dependencies"] == ["Team: maude-et-al"]
    assert {b["kind"] for ev in claim["evidence"] for b in ev["basis"]} == {"klinische_studie"}
    page = (real_site / "aussagen" / "cl-cart-remission.html").read_text(encoding="utf-8")
    assert "Alle stützenden Quellen stammen vom selben Team." in page


def test_eine_studie_stuetzt_eine_aussage_und_spricht_gegen_eine_andere(real_state):
    hummeln = by_id(real_state["claims"], "cl-neonic-hummeln")
    honigbienen = by_id(real_state["claims"], "cl-neonic-honigbienen")
    field_study = "rundlof-wildbienen-nature-2015"
    assert by_id([e | {"id": e["study"]["id"]} for e in hummeln["evidence"]], field_study)["relation"] == "stuetzt"
    assert by_id([e | {"id": e["study"]["id"]} for e in honigbienen["evidence"]], field_study)["relation"] == "spricht_dagegen"
    assert (hummeln["proposed_status"], honigbienen["proposed_status"]) == ("mehrfach_gestuetzt", "widerspruechlich")
    assert states(real_state, "goal-neonicotinoide-bienen") == ["proposed", "proposed", "proposed-failed"]


@pytest.mark.parametrize("claim_id", ["cl-mindset-noten", "cl-bleiweiss-alter"])
def test_nicht_entscheidender_beleg_zaehlt_weder_dafuer_noch_dagegen(real_state, claim_id):
    claim = by_id(real_state["claims"], claim_id)
    assert relations(claim) == ["nicht_entscheidend", "stuetzt"]
    assert (claim["supporting_sources"], claim["supporting_observations"]) == (1, 1)
    assert claim["proposed_status"] == "vorlaeufig_gestuetzt"


def test_schwache_gesamtwirkung_laesst_den_zweiten_meilenstein_scheitern(real_state):
    assert states(real_state, "goal-growth-mindset") == ["proposed", "proposed-failed"]


def test_zurueckgezogene_studie_zaehlt_nicht_die_nachfolgestudie_schon(real_state, real_site):
    retracted = by_id(real_state["claims"], "cl-haustuer-gleichstellung")
    assert retracted["supporting_sources"] == 0 and retracted["proposed_status"] == "offen"
    assert [ev["counts_as_support"] for ev in retracted["evidence"]] == [False]
    follow_up = by_id(real_state["claims"], "cl-haustuer-transphobie")
    assert follow_up["supporting_sources"] == 2 and follow_up["proposed_status"] == "mehrfach_gestuetzt"
    assert states(real_state, "goal-haustuergespraeche") == ["proposed", "open"]
    page = (real_site / "aussagen" / "cl-haustuer-gleichstellung.html").read_text(encoding="utf-8")
    assert "zurückgezogen" in page and "2015.05.28-Science-LaCourGreen.pdf" in page


@pytest.mark.parametrize("goal_id, open_milestone", [
    ("goal-car-t-leukaemie", "ms-cart-fuenf-jahre"), ("goal-bleiweiss-datierung", "ms-bleiweiss-anwendung"),
    ("goal-haustuergespraeche", "ms-haustuer-anderes-team")])
def test_meilenstein_ohne_vorschlag_bleibt_offen(real_state, goal_id, open_milestone):
    goal = by_id(real_state["goals"], goal_id)
    assert by_id(goal["milestones"], open_milestone)["state"] == "open"
    assert goal["milestones_proposed"] == len(goal["milestones"]) - 1


def test_beleg_verweist_auf_die_fassung_die_gelesen_wurde(real_site):
    """Wo nur ein Arbeitspapier, ein Preprint oder ein Archiv geprüft wurde, führt der Link genau dorthin."""
    def links(name: str) -> list[str]:
        return re.findall(r'href="([^"]+)"', (real_site / "aussagen" / f"{name}.html").read_text(encoding="utf-8"))

    assert "https://www.nber.org/papers/w9873" in links("cl-bewerbung-rueckmeldungen")
    assert "https://arxiv.org/abs/cond-mat/0509355" in links("cl-graphen-dirac")
    assert "https://escholarship.org/uc/item/2np7q721" in links("cl-haustuer-transphobie")
    assert "https://pubmed.ncbi.nlm.nih.gov/8419816/" in links("cl-hpylori-rueckfall")


def test_jedes_neue_ziel_hat_seite_und_weg_nach_aussen(real_site):
    for goal_id in NEW_GOALS:
        html = (real_site / "ziele" / f"{goal_id}.html").read_text(encoding="utf-8")
        assert "Ebene 5 von 6" in html and "Raus: " in html, goal_id
        for claim_link in set(re.findall(r'href="(\.\./aussagen/[^"]+)"', html)):
            assert (real_site / "ziele" / claim_link).resolve().is_file(), claim_link


# Durchgespielt -------------------------------------------------------------------

@pytest.fixture(scope="module")
def approved(tmp_path_factory) -> dict:
    """Zwei Personen geben jeden Vorschlag frei."""
    data = tmp_path_factory.mktemp("ausbau2-freigabe") / "data"
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


@pytest.mark.parametrize("goal_id", sorted(NEW_GOALS))
def test_nach_freigabe_steht_jedes_neue_ziel_wie_vorgeschlagen(approved, goal_id):
    assert by_id(approved["goals"], goal_id)["display"] == NEW_GOALS[goal_id][1]


def test_nach_freigabe_bleibt_die_zurueckgezogene_aussage_offen(approved):
    claim = by_id(approved["claims"], "cl-haustuer-gleichstellung")
    assert claim["evidence_status"] == "offen" and claim["supporting_sources"] == 0
