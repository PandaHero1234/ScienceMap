"""Die erzeugten Seiten: Wege, Anker, Zustände der Stationen und die Liste offener Prüfungen."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import atlas

ROOT = Path(__file__).resolve().parent.parent
REPO = "https://github.com/PandaHero1234/ScienceMap"


@pytest.fixture(scope="module")
def site(real_site) -> Path:
    return real_site


def pages(site: Path) -> list[Path]:
    return sorted(site.rglob("*.html"))


def hrefs(page: Path) -> list[str]:
    return re.findall(r'(?:href|src)="([^"]+)"', page.read_text(encoding="utf-8"))


def ids(page: Path) -> set[str]:
    return set(re.findall(r'\bid="([^"]+)"', page.read_text(encoding="utf-8")))


def test_alle_seiten_sind_vorhanden(site, real_state):
    names = {p.relative_to(site).as_posix() for p in pages(site)}
    assert {"index.html", "ziele.html", "pruefen.html", "verlauf.html"} <= names
    areas = [a for r in real_state["realms"] for a in r["areas"]]
    assert {"fach/mathematik.html", "fach/informatik.html", "fach/physik-astronomie.html", "fach/biologie.html"} <= names
    assert sum(n.startswith("fach/") for n in names) == sum(1 for a in areas if a["goal_ids"])
    assert sum(n.startswith("bereich/") for n in names) == 6, "eine Zwischenkarte je Bereich"
    assert sum(n.startswith("thema/") for n in names) == sum(len(a["topics"]) for a in areas)
    assert sum(n.startswith("ziele/") for n in names) == len(real_state["goals"])
    assert sum(n.startswith("aussagen/") for n in names) == len(real_state["claims"])
    assert (site / "atlas.css").is_file() and (site / "atlas.js").is_file()
    assert (site / "badge.svg").is_file() and (site / "badge-physik.svg").is_file()


def test_jede_seite_hat_grundgeruest_fuer_bedienbarkeit(site):
    for page in pages(site):
        html = page.read_text(encoding="utf-8")
        assert '<html lang="de">' in html, page.name
        assert len(re.findall(r"<h1[ >]", html)) == 1, f"{page.name}: genau eine Hauptüberschrift"
        assert re.search(r"<title>[^<]+</title>", html), page.name
        assert 'class="skip" href="#inhalt"' in html and 'id="inhalt"' in html, f"{page.name}: Sprunglink"
        assert 'name="viewport"' in html, page.name


def test_kein_interner_link_und_kein_anker_fuehrt_ins_leere(site):
    for page in pages(site):
        for href in hrefs(page):
            if href.startswith(("http", "data:")):
                continue
            path, _, anchor = href.partition("#")
            target = (page.parent / path).resolve() if path else page
            assert target.is_file(), f"{page.name}: toter Link {href}"
            if anchor and target.suffix == ".html":
                assert anchor in ids(target), f"{page.name}: Anker {href} fehlt"


def test_route_zeigt_jeden_meilenstein_mit_seinem_zustand(site, real_state):
    index = (site / "ziele.html").read_text(encoding="utf-8")
    m = real_state["totals"]["milestones"]
    states = re.findall(r'<li class="station is-([a-z-]+)">', index)
    assert len(states) == m["total"]
    assert {s: states.count(s) for s in set(states)} == {
        "proposed": m["proposed"], "proposed-failed": m["proposed_failed"], "open": m["open"]}
    assert "is-reached" not in " ".join(states), "ohne Freigabe ist keine Station erreicht"


def test_zustand_steht_als_text_und_nicht_nur_als_farbe(site, real_state):
    index = (site / "ziele.html").read_text(encoding="utf-8")
    assert index.count('<span class="sr">: Vorschlag: erreicht</span>') == real_state["totals"]["milestones"]["proposed"]
    assert 'aria-label="Legende der Stationen"' in index
    claim = (site / "aussagen" / "cl-gw-zwei-ereignisse.html").read_text(encoding="utf-8")
    assert "Vorschlag: mehrfach gestützt" in claim


def test_ohne_javascript_ist_alles_lesbar(site, real_state):
    index = (site / "ziele.html").read_text(encoding="utf-8")
    assert index.count('<li class="goal"') == len(real_state["goals"]), "alle Ziele stehen im HTML"
    assert 'id="filter" role="search" hidden' in index, "die Filterleiste erscheint erst mit JavaScript"
    assert 'id="theme" type="button" hidden' in index


def test_suche_findet_ziele_ueber_aussagen_und_quellen(site):
    index = (site / "ziele.html").read_text(encoding="utf-8")
    search = {m.group(1): m.group(2) for m in re.finditer(
        r'data-search="([^"]*)">\s*<div>\s*<h4><a href="ziele/([^"]+)\.html"', index)}
    by_goal = {goal: text for text, goal in search.items()}
    assert "ngago" in by_goal["goal-ngago-genom-editierung"]
    assert "frangoul et al. 2024" in by_goal["goal-cas9-genom-editierung"]
    assert "zwillingsprimzahlvermutung" in by_goal["goal-primzahlluecken"]


def test_quellenmatrix_zeigt_geteilte_grundlagen(site):
    claim = (site / "aussagen" / "cl-gw-zwei-ereignisse.html").read_text(encoding="utf-8")
    table = claim[claim.index('<table class="matrix">'):claim.index("</table>")]
    assert table.count("<tr>") == 4, "Kopfzeile und drei Quellen"
    assert table.count('<span class="dot"></span>') == 4, "zwei Einzelveröffentlichungen und die gemeinsame Auswertung"
    assert "3 Quellen, 2 Ereignisse." in claim
    assert "vom selben Team und nutzen dasselbe Instrument" in claim


def test_aussage_fuehrt_zurueck_zu_ziel_und_meilenstein(site):
    claim = site / "aussagen" / "cl-primluecken-endliche-schranke.html"
    links = hrefs(claim)
    assert "../ziele/goal-primzahlluecken.html" in links
    assert "../ziele/goal-primzahlluecken.html#ms-primluecken-zweiter-beweis" in links
    assert "../fach/mathematik.html" in links, "der Rückweg führt über das Fachgebiet"


def test_offene_pruefungen_nennen_jeden_ungeprueften_eintrag_mit_datei(site, real_atlas):
    expected = {e["id"] for e in real_atlas.evidence.values() if e["review_status"] != "freigegeben"}
    expected |= {d["id"] for d in real_atlas.decisions.values() if d["status"] != "freigegeben"}
    queue = site / "pruefen.html"
    listed = {i[2:] for i in ids(queue) if i.startswith("q-")}
    assert listed == expected and len(listed) > 100
    edits = [h for h in hrefs(queue) if h.startswith(f"{REPO}/edit/main/")]
    assert len(edits) == len(expected)
    for href in edits:
        assert (ROOT / href.removeprefix(f"{REPO}/edit/main/")).is_file(), f"Datei fehlt: {href}"


def test_vorschlag_verweist_auf_seine_pruefung(site):
    goal = site / "ziele" / "goal-gravitationswellen-schwarze-loecher.html"
    assert "../pruefen.html#q-dec-2026-11-21-ms-gw-erstnachweis" in hrefs(goal)


def test_gestaltung_deckt_helles_und_dunkles_design_ab(site):
    css = (site / "atlas.css").read_text(encoding="utf-8")
    assert ':root:not([data-theme="light"])' in css and ':root[data-theme="dark"]' in css
    assert "prefers-reduced-motion" in css and ":focus-visible" in css
    literal = [line for line in css.splitlines()
               if re.search(r"#[0-9a-fA-F]{3,6}\b", line) and "--" not in line and "#fff" not in line]
    assert literal == [], f"Farben nur über Variablen: {literal}"


def test_erreichte_station_nach_freigabe(world, tmp_path):
    """Mit erfundenen Daten: Eine freigegebene Entscheidung macht die Station zu 'erreicht'."""
    world.decide("dec-1", "ms-a", "erreicht", "2026-02-01")
    assert atlas.main(["build", "--data", str(world.root), "--out", str(tmp_path / "s")]) == 0
    index = (tmp_path / "s" / "ziele.html").read_text(encoding="utf-8")
    assert index.count('<li class="station is-reached">') == 1
    assert "<strong>1 von 4</strong> Meilensteinen erreicht" in index
    goal = (tmp_path / "s" / "ziele" / "goal-test.html").read_text(encoding="utf-8")
    assert "Freigegeben am 2026-02-01 von Ada und Ben" in goal
    verlauf = (tmp_path / "s" / "verlauf.html").read_text(encoding="utf-8")
    assert "keine Einstufung → erreicht" in verlauf and "1 von 4 erreicht (Katalog v1)" in verlauf
    assert "Zurzeit wartet nichts auf eine Prüfung." in (tmp_path / "s" / "pruefen.html").read_text(encoding="utf-8")
