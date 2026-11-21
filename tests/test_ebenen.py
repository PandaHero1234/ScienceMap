"""Die Ebenen der Karte: von 'Alle Wissenschaften' Schritt für Schritt hinein und wieder hinaus."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import atlas

ROOT = Path(__file__).resolve().parent.parent
# Ein Weg durch alle sechs Ebenen: (Seite, Name der Ebene, Überschrift beginnt mit)
WEG = [
    ("index.html", "Über-Atlas", "Forschungsatlas"),
    ("bereich/naturwissenschaften.html", "Bereich", "Naturwissenschaften"),
    ("fach/biologie.html", "Fachgebiet", "Biologie"),
    ("thema/106-genom-editierung.html", "Teilgebiet", "Genom-Editierung"),
    ("ziele/goal-ngago-genom-editierung.html", "Ziel", "DNA-geführte Genom-Editierung mit NgAgo"),
    ("aussagen/cl-ngago-editierung-humanzellen.html", "Aussage", "Das Argonaute-Protein"),
]


@pytest.fixture(scope="module")
def site(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("ebenen")
    assert atlas.main(["build", "--out", str(out)]) == 0
    return out


def links(page: Path) -> list[Path]:
    """Alle internen Linkziele einer Seite als absolute Pfade, ohne Anker."""
    found = []
    for href in re.findall(r'href="([^"#]+)(?:#[^"]*)?"', page.read_text(encoding="utf-8")):
        if not href.startswith(("http", "data:")):
            found.append((page.parent / href).resolve())
    return found


def out_link(page: Path) -> Path:
    """Das Ziel des Knopfs 'Raus' oben auf der Seite."""
    html = page.read_text(encoding="utf-8")
    href = re.search(r'<nav class="zoom"[^>]*><a class="btn ghost s" href="([^"]+)"', html).group(1)
    return (page.parent / href).resolve()


def test_jede_ebene_fuehrt_hinein_zur_naechsten(site):
    for (outer, _, _), (inner, _, _) in zip(WEG, WEG[1:]):
        assert (site / inner).resolve() in links(site / outer), f"{outer} führt nicht hinein zu {inner}"


def test_jede_ebene_fuehrt_mit_einem_knopf_hinaus_zur_vorigen(site):
    for (outer, _, _), (inner, _, _) in zip(WEG, WEG[1:]):
        assert out_link(site / inner) == (site / outer).resolve(), f"{inner} führt nicht hinaus zu {outer}"


def test_jede_ebene_nennt_ihre_stufe_und_den_ganzen_weg_nach_aussen(site):
    for depth, (name, level, heading) in enumerate(WEG):
        html = (site / name).read_text(encoding="utf-8")
        assert re.search(rf"<h1[^>]*>{re.escape(heading)}", html), name
        if depth == 0:
            assert '<nav class="zoom"' not in html, "die äußerste Ebene hat keinen Weg hinaus"
            continue
        assert f"Ebene {depth + 1} von 6" in html, name
        path = html[html.index('<ol class="zoom-path">'):html.index("</ol>", html.index('<ol class="zoom-path">'))]
        assert re.findall(r'<span class="k">([^<]+)</span>', path) == [w[1] for w in WEG[:depth + 1]], name
        assert path.count("<a href=") == depth, "jede äußere Ebene ist ein Link"
        assert f'<li aria-current="page"><span class="k">{level}</span>' in path
        for outer, _, _ in WEG[:depth]:
            assert (site / outer).resolve() in links(site / name), f"{name} verlinkt {outer} nicht"


def test_von_ganz_innen_fuehrt_der_weg_zur_fundstelle(site):
    claim = (site / WEG[-1][0]).read_text(encoding="utf-8")
    assert "https://doi.org/10.1038/nbt.3753" in claim and "Original öffnen" in claim


def test_nachbarn_auf_derselben_ebene(site):
    def beside(name: str) -> list[str]:
        html = (site / name).read_text(encoding="utf-8")
        if '<p class="beside">' not in html:
            return []
        block = html[html.index('<p class="beside">'):]
        return re.findall(r'<a class="pill" href="[^"]+">([^<]+)</a>', block[:block.index("</p>")])

    assert len(beside("bereich/naturwissenschaften.html")) == 5, "die fünf anderen Bereiche"
    assert beside("fach/biologie.html") == ["Mathematik", "Informatik", "Physik, Astronomie"]
    assert beside("thema/106-genom-editierung.html") == [], "das einzige Teilgebiet der Biologie"
    assert beside("ziele/goal-ngago-genom-editierung.html") == [
        "Programmierbare Genom-Editierung mit CRISPR-Cas9 nachweisen, bestätigen und klinisch anwenden"]
    assert len(beside("aussagen/cl-gw150914-nachweis.html")) == 3, "die drei anderen Aussagen desselben Ziels"


def test_bereich_ohne_eintraege_ist_begehbar_und_sagt_das(site):
    html = (site / "bereich" / "geisteswissenschaften.html").read_text(encoding="utf-8")
    assert "In diesem Bereich hat der Atlas noch keinen Eintrag." in html
    assert html.count("noch kein Eintrag") == 5 and 'class="area has"' not in html
    assert out_link(site / "bereich" / "geisteswissenschaften.html") == (site / "index.html").resolve()


def test_bereich_zeigt_seine_fachgebiete_und_ihren_stand(site):
    html = (site / "bereich" / "naturwissenschaften.html").read_text(encoding="utf-8")
    assert len(re.findall(r'class="area(?: has)?"', html)) == 7
    assert html.count('<a class="area has" href="../fach/') == 4
    assert "<b>0 von 19</b><span>Meilensteinen erreicht · 0 %</span>" in html, "alle Einträge liegen in diesem Bereich"


def test_teilgebiet_zeigt_seine_ziele_als_karte_und_routen(site):
    html = (site / "thema" / "106-genom-editierung.html").read_text(encoding="utf-8")
    assert "<b>0 von 6</b><span>Meilensteinen erreicht · 0 %</span>" in html
    assert len(re.findall(r'<a class="tile is-', html)) == 6 + 4 + 8
    assert html.count('<li class="goal"') == 2
    assert "Gravitationswellen" not in html


def test_teilgebiete_ergeben_zusammen_ihr_fachgebiet():
    loaded, errors = atlas.load_checked(ROOT / "data")
    assert errors == []
    state = atlas.build_state(loaded)
    for realm in state["realms"]:
        inside = [a for a in realm["areas"] if a["tally"]]
        if realm["tally"]:
            assert sum(a["tally"]["milestones"]["total"] for a in inside) == realm["tally"]["milestones"]["total"]
        for area in inside:
            assert sum(t["tally"]["milestones"]["total"] for t in area["topics"]) == area["tally"]["milestones"]["total"]
            assert sorted(g for t in area["topics"] for g in t["goal_ids"]) == area["goal_ids"]
