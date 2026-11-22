"""Die Gesamtübersicht: Gesamtstand, Karte, Tabelle je Ziel, offene Arbeit, Verlauf und Abzeichen."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

import atlas

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def state(real_state) -> dict:
    return real_state


@pytest.fixture(scope="module")
def site(real_site) -> Path:
    return real_site


def test_gesamtstand_zaehlt_alle_meilensteine_nach_zustand(state, real_atlas):
    m = state["totals"]["milestones"]
    assert state["totals"]["goals"] == len(real_atlas.goals)
    assert m["total"] == sum(len(g["catalog"][-1]["milestones"]) for g in real_atlas.goals.values() if g.get("catalog"))
    assert m["total"] == m["reached"] + m["proposed"] + m["proposed_failed"] + m["failed"] + m["open"], "jeder Meilenstein zählt genau einmal"
    assert (m["reached"], m["failed"]) == (0, 0), "ohne Freigabe ist nichts entschieden"
    assert state["totals"]["claims"] == {"total": len(real_atlas.claims), "reviewed": 0}
    assert state["totals"]["evidence"] == {"total": len(real_atlas.evidence), "reviewed": 0}


def test_faecher_ergeben_zusammen_den_gesamtstand(state):
    assert [f["field"] for f in state["fields"]] == sorted({g["field"] for g in state["goals"]})
    for group in ("milestones", "claims", "evidence"):
        for key, value in state["totals"][group].items():
            assert sum(f[group][key] for f in state["fields"]) == value, (group, key)
    assert sum(f["goals"] for f in state["fields"]) == state["totals"]["goals"]


def test_startseite_beginnt_mit_dem_gesamtstand(site, state):
    index = (site / "index.html").read_text(encoding="utf-8")
    totals = state["totals"]
    m = totals["milestones"]
    assert f"<b>{m['reached']} von {m['total']}</b><span>Meilensteinen erreicht · 0 %</span>" in index
    assert f"<b>0 von {totals['claims']['total']}</b><span>Aussagen geprüft</span>" in index
    assert f"<b>0 von {totals['evidence']['total']}</b><span>Belege geprüft</span>" in index
    order = [index.index(text) for text in ('id="gesamt"', "Karte der Wissenschaften", "Stand nach Fachgebiet",
                                             "Was noch fehlt", f'href="ziele.html">Alle {totals["goals"]} Ziele ansehen')]
    assert order == sorted(order), "erst das Ganze, dann der Weg zu den einzelnen Zielen"
    assert '<li class="goal"' not in index, "die einzelnen Ziele stehen auf eigenen Seiten"


def test_gesamtbalken_teilt_das_ganze_nach_zustand(site, state):
    index = (site / "index.html").read_text(encoding="utf-8")
    m = state["totals"]["milestones"]
    bar = index[index.index('<div class="segbar tall">'):index.index('<ul class="legend" aria-label="Legende des Balkens">')]
    assert re.findall(r'class="seg s-([a-z-]+)" style="flex-grow:(\d+)"', bar) == [
        ("proposed", str(m["proposed"])), ("proposed-failed", str(m["proposed_failed"])), ("open", str(m["open"]))]
    share = round(100 * m["proposed"] / m["total"])
    assert f'aria-label="{m["proposed"]} von {m["total"]} als erreicht vorgeschlagen ({share} %)"' in bar, \
        "jeder Teil nennt Name, Anzahl und Anteil"
    assert "s-reached" not in bar, "ein Teil mit null zeichnet nichts"


def test_vorschlaege_sind_als_rechnung_gekennzeichnet(site, state):
    index = (site / "index.html").read_text(encoding="utf-8")
    m = state["totals"]["milestones"]
    assert (f"Rechnung, kein Stand: Würden alle offenen Vorschläge freigegeben, wären {m['proposed']} von {m['total']}"
            in index)


def test_karte_hat_eine_kachel_je_meilenstein_aussage_und_beleg(site, state):
    index = (site / "ziele.html").read_text(encoding="utf-8")
    totals = state["totals"]
    tiles = re.findall(r'<a class="tile is-([a-z-]+)" href="([^"]+)"', index)
    assert len(tiles) == totals["milestones"]["total"] + totals["claims"]["total"] + totals["evidence"]["total"]
    assert sum(1 for _, href in tiles if href.startswith("ziele/")) == totals["milestones"]["total"]
    assert sum(1 for _, href in tiles if href.startswith("aussagen/") and "#" not in href) == totals["claims"]["total"]
    assert sum(1 for _, href in tiles if href.startswith("aussagen/") and "#ev-" in href) == totals["evidence"]["total"]
    assert {state for state, _ in tiles} == {"proposed", "proposed-failed", "open"}, "ohne Freigabe ist keine Kachel geprüft"
    assert "Meilenstein: Erstnachweis belegen · Vorschlag: erreicht" in index


def test_tabelle_nennt_jedes_fachgebiet_und_die_summe(site, state):
    index = (site / "index.html").read_text(encoding="utf-8")
    totals = state["totals"]
    table = index[index.index('<table class="cover">'):index.index("</table>")]
    assert table.count('<tr><th scope="row"><span class="k">') == state["coverage"]["covered"], \
        "eine Zeile je Fachgebiet mit Einträgen"
    total = table[table.index("<tfoot>"):]
    assert re.findall(r'<td class="num">([^<]+)</td>', total) == [
        str(totals["goals"]), f"0 von {totals['milestones']['total']}", str(totals["milestones"]["proposed"]),
        f"0 von {totals['claims']['total']}", f"0 von {totals['evidence']['total']}"]


def test_was_noch_fehlt_nennt_die_fehlende_arbeit(site, state):
    index = (site / "index.html").read_text(encoding="utf-8")
    m = state["totals"]["milestones"]
    assert f"<b>{m['proposed'] + m['proposed_failed']}</b> Meilensteine warten auf die Zweitprüfung." in index
    assert f"<b>{m['open']}</b> Meilensteine haben noch keinen Vorschlag:" in index
    assert 'href="ziele/goal-primzahlluecken.html#ms-zwillingsprimzahlen">Zwillingsprimzahlvermutung beweisen</a> (Mathematik)' in index


def test_abzeichen_tragen_den_zaehlerstand(site, state):
    total = state["totals"]["milestones"]["total"]
    assert f"Meilensteine: 0/{total}" in (site / "badge.svg").read_text(encoding="utf-8")
    mathe = next(f for f in state["fields"] if f["field"] == "Mathematik")
    assert f"Mathematik: 0/{mathe['milestones']['total']}" in (site / "badge-mathematik.svg").read_text(encoding="utf-8")
    assert "Process Mining: 0/4" in (site / "badge-process-mining.svg").read_text(encoding="utf-8")


def test_progress_json_enthaelt_den_gesamtstand(site, state):
    progress = json.loads((site / "progress.json").read_text(encoding="utf-8"))
    assert progress["totals"] == state["totals"]
    assert progress["series"] == state["series"]
    assert progress["series"][0] == {"date": "2026-11-21", "reached": 0, "total": 19}, "der erste Stand bleibt abrufbar"
    assert len(progress["fields"]) == len(state["fields"])


def test_mit_einem_tag_gibt_es_noch_keine_kurve(world, tmp_path):
    """Mit erfundenen Daten: Solange es nur einen Stand gibt, zeigt der Verlauf die Tabelle und einen Hinweis."""
    assert atlas.main(["build", "--data", str(world.root), "--out", str(tmp_path / "s")]) == 0
    assert '<figure class="chart">' not in (tmp_path / "s" / "index.html").read_text(encoding="utf-8")
    verlauf = (tmp_path / "s" / "verlauf.html").read_text(encoding="utf-8")
    assert "Die Kurve erscheint, sobald der Verlauf zwei Tage umfasst." in verlauf
    assert '<th scope="row">2026-01-01</th><td class="num">0</td><td class="num">4</td><td class="num">–</td>' in verlauf


def test_wachsender_katalog_erscheint_im_verlauf(site, state):
    """Echte Daten: Der Ausbau am zweiten Tag erhöht die Zahl der Meilensteine im Katalog, nicht die erreichten."""
    assert [p["date"] for p in state["series"]][:2] == ["2026-11-21", "2026-11-22"]
    assert state["series"][1]["total"] > state["series"][0]["total"] and state["series"][1]["reached"] == 0
    assert '<figure class="chart">' in (site / "index.html").read_text(encoding="utf-8")
    verlauf = (site / "verlauf.html").read_text(encoding="utf-8")
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
