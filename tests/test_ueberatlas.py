"""Der Über-Atlas: alle Fachgebiete der Systematik, mit oder ohne Einträge, und der Atlas je Fachgebiet."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import pytest
import yaml

import atlas

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def state(real_state) -> dict:
    return real_state


@pytest.fixture(scope="module")
def site(real_site) -> Path:
    return real_site


def test_systematik_hat_sechs_bereiche_und_42_fachgebiete(state):
    assert len(state["realms"]) == 6
    assert sum(len(r["areas"]) for r in state["realms"]) == 42
    codes = [a["code"] for r in state["realms"] for a in r["areas"]]
    assert len(set(codes)) == 42
    assert all(a["code"].startswith(r["code"]) for r in state["realms"] for a in r["areas"])


def test_abdeckung_zaehlt_die_fachgebiete_mit_eintraegen(state):
    covered = {a["name"]: len(a["goal_ids"]) for r in state["realms"] for a in r["areas"] if a["goal_ids"]}
    assert state["coverage"] == {"areas": 42, "covered": len(covered)}
    assert {"Mathematik", "Informatik", "Physik, Astronomie", "Biologie"} <= set(covered)
    assert sum(covered.values()) == len(state["goals"]), "jedes Ziel liegt in genau einem Fachgebiet"


def test_alle_sechs_bereiche_haben_eintraege(state):
    assert all(r["tally"] for r in state["realms"]), "der Ausbau reicht in jeden Bereich"


def test_fachgebiete_ergeben_zusammen_den_gesamtstand(state):
    tallies = [a["tally"] for r in state["realms"] for a in r["areas"] if a["tally"]]
    for group in ("milestones", "claims", "evidence"):
        for key, value in state["totals"][group].items():
            assert sum(t[group][key] for t in tallies) == value, (group, key)
    assert sum(t["goals"] for t in tallies) == state["totals"]["goals"]


def test_jedes_ziel_ist_einem_fachgebiet_zugeordnet(state):
    assert all(goal["area"] for goal in state["goals"])


def world_copy(tmp_path: Path) -> Path:
    data = tmp_path / "data"
    shutil.copytree(ROOT / "data", data)
    return data


def test_unbekanntes_fachgebiet_stoppt(tmp_path):
    data = world_copy(tmp_path)
    path = data / "goals" / "goal-primzahlluecken.yaml"
    record = yaml.safe_load(path.read_text(encoding="utf-8")) | {"area": "999"}
    path.write_text(yaml.safe_dump(record, allow_unicode=True, sort_keys=False), encoding="utf-8")
    errors = atlas.load_checked(data)[1]
    assert any("goal-primzahlluecken" in e and "unbekanntes Fachgebiet 999" in e for e in errors)


def test_ziel_ohne_fachgebiet_stoppt(tmp_path):
    data = world_copy(tmp_path)
    path = data / "goals" / "goal-primzahlluecken.yaml"
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    del record["area"]
    path.write_text(yaml.safe_dump(record, allow_unicode=True, sort_keys=False), encoding="utf-8")
    errors = atlas.load_checked(data)[1]
    assert any("goal-primzahlluecken" in e and "area" in e for e in errors)


def test_startseite_zeigt_alle_fachgebiete_auch_die_leeren(site, state):
    index = (site / "index.html").read_text(encoding="utf-8")
    covered = state["coverage"]["covered"]
    assert len(re.findall(r'class="area(?: has)?"', index)) == 42
    assert index.count('<a class="area has" href="fach/') == covered
    assert index.count("noch kein Eintrag") == 42 - covered
    assert f"<b>{covered} von 42</b><span>Fachgebieten mit Einträgen</span>" in index
    assert f"<b>{42 - covered}</b> Fachgebiete haben noch keinen Eintrag." in index
    for realm in state["realms"]:
        inside = sum(1 for a in realm["areas"] if a["goal_ids"])
        assert f'{realm["name"]}</a> <small>{inside} von {len(realm["areas"])} mit Einträgen</small>' in index


def test_feld_auf_der_karte_nennt_stand_und_fuehrt_zum_fachatlas(site, state):
    index = (site / "index.html").read_text(encoding="utf-8")
    area = next(a for r in state["realms"] for a in r["areas"] if a["name"] == "Biologie")
    m = area["tally"]["milestones"]
    cell = index[index.index('<a class="area has" href="fach/biologie.html">'):]
    cell = cell[:cell.index("</a>")]
    assert f"0 von {m['total']} erreicht · {m['proposed']} vorgeschlagen" in cell
    assert f"{len(area['goal_ids'])} Ziele" in cell
    assert (site / "fach" / "biologie.html").is_file()


def test_fachatlas_zeigt_stand_teilgebiete_und_tabelle_des_fachs(site, state):
    page = (site / "fach" / "biologie.html").read_text(encoding="utf-8")
    area = next(a for r in state["realms"] for a in r["areas"] if a["name"] == "Biologie")
    assert "<h1>Biologie</h1>" in page and "Fachgebiet 106" in page
    assert f"<b>0 von {area['tally']['milestones']['total']}</b><span>Meilensteinen erreicht · 0 %</span>" in page
    assert page.count('<div class="topic">') == len(area["topics"])
    assert '<a class="topic-title" href="../thema/106-genom-editierung.html">Genom-Editierung</a>' in page
    assert "Gravitationswellen" not in page, "Ziele anderer Fachgebiete gehören nicht hierher"
    order = [page.index(text) for text in ("Stand des Fachgebiets", "<h2>Teilgebiete</h2>", "Stand nach Ziel", "Was noch fehlt")]
    assert order == sorted(order)


def test_ziel_und_aussage_fuehren_zurueck_zum_fachatlas(site):
    goal = (site / "ziele" / "goal-discovery-fscore.html").read_text(encoding="utf-8")
    assert '<a href="../fach/informatik.html">Informatik</a>' in goal
    claim = (site / "aussagen" / "cl-gw150914-nachweis.html").read_text(encoding="utf-8")
    assert '<a href="../fach/physik-astronomie.html">Physik, Astronomie</a>' in claim


def test_progress_json_enthaelt_die_abdeckung(site, state):
    progress = json.loads((site / "progress.json").read_text(encoding="utf-8"))
    assert progress["coverage"] == state["coverage"]
    assert [r["name"] for r in progress["realms"]][:2] == ["Naturwissenschaften", "Technische Wissenschaften"]


def test_ohne_systematik_bleibt_die_uebersicht_bei_den_zielen(world, tmp_path):
    """Mit erfundenen Daten ohne taxonomy.yaml: keine Karte der Wissenschaften, dafür die Karte der Einträge."""
    assert atlas.main(["build", "--data", str(world.root), "--out", str(tmp_path / "s")]) == 0
    index = (tmp_path / "s" / "index.html").read_text(encoding="utf-8")
    assert "Karte der Wissenschaften" not in index and "Karte des Atlas" in index
    assert not (tmp_path / "s" / "fach").exists()
    goal = (tmp_path / "s" / "ziele" / "goal-test.html").read_text(encoding="utf-8")
    assert "<li>Testfach</li>" in goal, "ohne Fachgebiet steht das Fach als Text im Rückweg"
