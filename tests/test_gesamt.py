"""Die Gesamtübersicht: Gesamtstand, Karte, Tabelle je Ziel, offene Arbeit, Verlauf und Abzeichen."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

import atlas

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def state() -> dict:
    loaded, errors = atlas.load_checked(ROOT / "data")
    assert errors == []
    return atlas.build_state(loaded)


@pytest.fixture(scope="module")
def site(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("gesamt")
    assert atlas.main(["build", "--out", str(out)]) == 0
    return out


def test_gesamtstand_zaehlt_alle_meilensteine_nach_zustand(state):
    assert state["totals"]["goals"] == 5
    assert state["totals"]["milestones"] == {
        "total": 19, "reached": 0, "proposed": 12, "proposed_failed": 2, "failed": 0, "open": 5}
    assert state["totals"]["claims"] == {"total": 12, "reviewed": 0}
    assert state["totals"]["evidence"] == {"total": 21, "reviewed": 0}


def test_faecher_ergeben_zusammen_den_gesamtstand(state):
    assert [f["field"] for f in state["fields"]] == ["Biologie", "Mathematik", "Physik", "Process Mining"]
    for group in ("milestones", "claims", "evidence"):
        for key, value in state["totals"][group].items():
            assert sum(f[group][key] for f in state["fields"]) == value, (group, key)
    assert sum(f["goals"] for f in state["fields"]) == 5


def test_startseite_beginnt_mit_dem_gesamtstand(site):
    index = (site / "index.html").read_text(encoding="utf-8")
    assert "<b>0 von 19</b><span>Meilensteinen erreicht · 0 %</span>" in index
    assert "<b>0 von 12</b><span>Aussagen geprüft</span>" in index
    assert "<b>0 von 21</b><span>Belege geprüft</span>" in index
    order = [index.index(text) for text in ('id="gesamt"', "Karte des Atlas", "Stand nach Fach und Ziel",
                                             "Was noch fehlt", "Ziele im Einzelnen")]
    assert order == sorted(order), "erst das Ganze, dann die einzelnen Ziele"


def test_gesamtbalken_teilt_das_ganze_nach_zustand(site):
    index = (site / "index.html").read_text(encoding="utf-8")
    bar = index[index.index('<div class="segbar tall">'):index.index('<ul class="legend" aria-label="Legende des Balkens">')]
    assert re.findall(r'class="seg s-([a-z-]+)" style="flex-grow:(\d+)"', bar) == [
        ("proposed", "12"), ("proposed-failed", "2"), ("open", "5")]
    assert 'aria-label="12 von 19 als erreicht vorgeschlagen (63 %)"' in bar, "jeder Teil nennt Name, Anzahl und Anteil"
    assert "s-reached" not in bar, "ein Teil mit null zeichnet nichts"


def test_vorschlaege_sind_als_rechnung_gekennzeichnet(site):
    index = (site / "index.html").read_text(encoding="utf-8")
    assert "Rechnung, kein Stand: Würden alle offenen Vorschläge freigegeben, wären 12 von 19" in index


def test_karte_hat_eine_kachel_je_meilenstein_aussage_und_beleg(site):
    index = (site / "index.html").read_text(encoding="utf-8")
    tiles = re.findall(r'<a class="tile is-([a-z-]+)" href="([^"]+)"', index)
    assert len(tiles) == 19 + 12 + 21
    assert sum(1 for _, href in tiles if href.startswith("ziele/")) == 19
    assert sum(1 for _, href in tiles if href.startswith("aussagen/") and "#" not in href) == 12
    assert sum(1 for _, href in tiles if href.startswith("aussagen/") and "#ev-" in href) == 21
    assert {state for state, _ in tiles} == {"proposed", "proposed-failed", "open"}, "ohne Freigabe ist keine Kachel geprüft"
    assert "Meilenstein: Erstnachweis belegen · Vorschlag: erreicht" in index


def test_tabelle_nennt_jedes_ziel_und_die_summe(site):
    index = (site / "index.html").read_text(encoding="utf-8")
    table = index[index.index('<table class="cover">'):index.index("</table>")]
    assert table.count('<tr><th scope="row"><span class="k">') == 5
    total = table[table.index("<tfoot>"):]
    assert [c for c in re.findall(r'<td class="num">([^<]+)</td>', total)] == ["0 von 19", "12", "0 von 12", "0 von 21"]


def test_was_noch_fehlt_nennt_die_fehlende_arbeit(site):
    index = (site / "index.html").read_text(encoding="utf-8")
    assert "<b>14</b> Meilensteine warten auf die Zweitprüfung." in index
    assert "<b>5</b> Meilensteine haben noch keinen Vorschlag:" in index
    assert 'href="ziele/goal-primzahlluecken.html#ms-zwillingsprimzahlen">Zwillingsprimzahlvermutung beweisen</a> (Mathematik)' in index


def test_abzeichen_tragen_den_zaehlerstand(site):
    assert "Meilensteine: 0/19" in (site / "badge.svg").read_text(encoding="utf-8")
    assert "Mathematik: 0/5" in (site / "badge-mathematik.svg").read_text(encoding="utf-8")
    assert "Process Mining: 0/4" in (site / "badge-process-mining.svg").read_text(encoding="utf-8")


def test_progress_json_enthaelt_den_gesamtstand(site, state):
    progress = json.loads((site / "progress.json").read_text(encoding="utf-8"))
    assert progress["totals"] == state["totals"]
    assert progress["series"] == [{"date": "2026-11-21", "reached": 0, "total": 19}]
    assert len(progress["fields"]) == 4


def test_mit_einem_tag_gibt_es_noch_keine_kurve(site):
    assert '<figure class="chart">' not in (site / "index.html").read_text(encoding="utf-8")
    verlauf = (site / "verlauf.html").read_text(encoding="utf-8")
    assert "Die Kurve erscheint, sobald der Verlauf zwei Tage umfasst." in verlauf
    assert '<th scope="row">2026-11-21</th><td class="num">0</td><td class="num">19</td><td class="num">–</td>' in verlauf


def test_kurve_zeigt_erreichte_meilensteine_ueber_die_zeit(world, tmp_path):
    """Mit erfundenen Daten: zwei Freigaben an zwei Tagen ergeben drei Punkte."""
    world.decide("dec-1", "ms-a", "erreicht", "2026-02-01")
    world.decide("dec-2", "ms-b", "erreicht", "2026-03-15")
    loaded, errors = atlas.load_checked(world.root)
    assert errors == []
    assert atlas.build_state(loaded)["series"] == [
        {"date": "2026-01-01", "reached": 0, "total": 4},
        {"date": "2026-02-01", "reached": 1, "total": 4},
        {"date": "2026-03-15", "reached": 2, "total": 4}]
    assert atlas.main(["build", "--data", str(world.root), "--out", str(tmp_path / "s")]) == 0
    index = (tmp_path / "s" / "index.html").read_text(encoding="utf-8")
    assert "<b>2 von 4</b><span>Meilensteinen erreicht · 50 %</span>" in index
    chart = index[index.index('<figure class="chart">'):index.index("</figure>")]
    assert chart.count('<circle class="dot"') == 3
    assert "<title>2026-03-15: 2 von 4 erreicht</title>" in chart
    assert ">erreicht 2</text>" in chart and ">gesamt 4</text>" in chart
    verlauf = (tmp_path / "s" / "verlauf.html").read_text(encoding="utf-8")
    assert '<th scope="row">2026-03-15</th><td class="num">2</td><td class="num">4</td><td class="num">+1</td>' in verlauf
    bar = index[index.index('<div class="segbar tall">'):index.index('<ul class="legend" aria-label="Legende des Balkens">')]
    assert re.findall(r'class="seg s-([a-z-]+)" style="flex-grow:(\d+)"', bar) == [("reached", "2"), ("open", "2")]
