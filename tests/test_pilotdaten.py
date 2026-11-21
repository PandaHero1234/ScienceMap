"""Die echten Daten unter data/ und die daraus erzeugte Übersicht."""

from __future__ import annotations

import json
import re
from pathlib import Path

import atlas

ROOT = Path(__file__).resolve().parent.parent
PILOT = "goal-discovery-fscore"
CLAIM = "cl-splitminer-bpic12-fscore"


def by_id(items: list[dict], wanted: str) -> dict:
    return next(i for i in items if i["id"] == wanted)


def test_pilotdaten_sind_gueltig():
    assert atlas.load_checked(ROOT / "data")[1] == []


def test_pilotstand_entspricht_der_dokumentation():
    """docs/01: 0 von 4, solange keine Freigabe durch zwei Personen vorliegt."""
    loaded, _ = atlas.load_checked(ROOT / "data")
    goal = by_id(atlas.build_state(loaded)["goals"], PILOT)
    assert goal["display"] == "0 von 4"
    assert goal["catalog_version"] == 1
    assert [m["status"] for m in goal["milestones"]] == ["offen"] * 4


def test_kein_beleg_ist_ohne_zweitpruefung_freigegeben():
    loaded, _ = atlas.load_checked(ROOT / "data")
    for record in list(loaded.evidence.values()) + list(loaded.decisions.values()):
        status = record.get("review_status", record.get("status"))
        if status == "freigegeben":
            assert record["extracted_by"].casefold() != record["reviewed_by"].casefold()


def test_weg_von_der_startseite_bis_zur_fundstelle(tmp_path):
    """docs/05, Erfolgskriterium: Startseite -> Ziel -> Aussage -> Fundstelle -> Einwand."""
    assert atlas.main(["build", "--out", str(tmp_path)]) == 0

    def links(path: Path) -> list[str]:
        return re.findall(r'href="([^"]+)"', path.read_text(encoding="utf-8"))

    index = tmp_path / "index.html"
    goal_link = next(h for h in links(index) if h == f"ziele/{PILOT}.html")
    goal_page = tmp_path / goal_link
    assert goal_page.is_file()

    claim_link = next(h for h in links(goal_page) if h.startswith("../aussagen/"))
    claim_page = (goal_page.parent / claim_link).resolve()
    assert claim_page.is_file()

    html = claim_page.read_text(encoding="utf-8")
    assert "Tabelle 4, BPIC12, Zeilen SM und IM" in html
    assert "https://kodu.ut.ee/~dumas/pubs/SplitMinerKAIS.pdf" in links(claim_page)
    assert "split miner: 0,88" in html and "inductive miner: 0,66" in html
    assert any("/issues/new?template=einwand.md" in h for h in links(claim_page))

    for page in tmp_path.rglob("*.html"):
        for href in links(page):
            if not href.startswith("http"):
                assert (page.parent / href).resolve().is_file(), f"{page.name}: toter Link {href}"


def test_progress_json_enthaelt_den_stand(tmp_path):
    assert atlas.main(["build", "--out", str(tmp_path)]) == 0
    progress = json.loads((tmp_path / "progress.json").read_text(encoding="utf-8"))
    goal = by_id(progress["goals"], PILOT)
    assert (goal["milestones_reached"], goal["milestones_total"]) == (0, 4)
    claim = by_id(progress["claims"], CLAIM)
    assert claim["editorial_status"] == "vorgeschlagen"
    assert claim["evidence_status"] == "offen"
    assert claim["evidence"][0]["study"]["url"].endswith("SplitMinerKAIS.pdf")
    history = json.loads((tmp_path / "history.json").read_text(encoding="utf-8"))
    assert history[0]["type"] == "katalog"
