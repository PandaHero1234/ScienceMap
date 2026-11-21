"""Erzeugt aus dem berechneten Stand die statische Übersicht und die JSON-Dateien.

Gestaltung und Bedienhilfen liegen in site/atlas.css und site/atlas.js. Alle
Inhalte stehen im HTML und sind ohne JavaScript lesbar.
"""

from __future__ import annotations

import json
import re
import shutil
from datetime import date
from html import escape as e
from pathlib import Path
from urllib.parse import quote

ASSETS = Path(__file__).resolve().parent.parent / "site"

LABELS = {
    "erreicht": "erreicht", "nicht_erreicht": "nicht erreicht", "offen": "offen",
    "vorlaeufig_gestuetzt": "vorläufig gestützt", "mehrfach_gestuetzt": "mehrfach gestützt",
    "widerspruechlich": "widersprüchlich", "spricht_dagegen": "Evidenz spricht dagegen",
    "vorgeschlagen": "vorgeschlagen", "in_pruefung": "in Prüfung", "freigegeben": "freigegeben",
    "erneut_zu_pruefen": "erneut zu prüfen",
    "quellenabgleich": "Quellenabgleich", "nachrechnung": "Nachrechnung", "neue_daten": "neue Daten",
    "anderes_team": "anderes Team", "anderes_instrument": "anderes Instrument",
    "beweisreview": "fachliches Beweisreview",
}
# Schlüsselwert -> (Farbton, Symbol). Symbol und Text tragen die Bedeutung, die Farbe unterstützt.
MARKS = {
    "erreicht": ("good", "circle-check"), "nicht_erreicht": ("none", "circle-cross"), "offen": ("none", "circle"),
    "vorlaeufig_gestuetzt": ("good", "circle-check"), "mehrfach_gestuetzt": ("good", "circle-check"),
    "widerspruechlich": ("warn", "alert"), "spricht_dagegen": ("bad", "circle-cross"),
    "vorgeschlagen": ("none", "circle-dash"), "in_pruefung": ("warn", "circle-dash"),
    "freigegeben": ("good", "circle-check"), "erneut_zu_pruefen": ("warn", "alert"),
}
RELATIONS = {  # Reihenfolge der Gruppen auf der Aussage-Seite
    "stuetzt": ("Stützt die Aussage", "stützt", "good", "circle-check"),
    "spricht_dagegen": ("Spricht gegen die Aussage", "spricht dagegen", "bad", "circle-cross"),
    "nicht_entscheidend": ("Entscheidet die Aussage nicht", "nicht entscheidend", "none", "minus"),
    "zurueckgezogen": ("Zurückgezogen, zählt nicht mehr", "zurückgezogen", "bad", "circle-cross"),
}


def direction(ev: dict) -> str:
    """Richtung eines Belegs. Ein stützender Beleg aus einer zurückgezogenen Studie zählt gesondert."""
    return "zurueckgezogen" if ev["relation"] == "stuetzt" and not ev["counts_as_support"] else ev["relation"]
KINDS = {  # Art der Grundlage -> (Einzahl, Mehrzahl)
    "datensatz": ("Datensatz", "Datensätze"), "ereignis": ("Ereignis", "Ereignisse"),
    "experiment": ("Versuchsreihe", "Versuchsreihen"), "klinische_studie": ("klinische Studie", "klinische Studien"),
    "beweis": ("Beweis", "Beweise"),
}
STATIONS = {  # Zustand einer Station -> (Beschriftung, Symbol)
    "reached": ("erreicht", "check"), "proposed": ("Vorschlag: erreicht", "dot"), "open": ("offen", ""),
    "failed": ("nicht erreicht", "cross"), "proposed-failed": ("Vorschlag: nicht erreicht", "cross"),
}
STROKE = 'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
ICONS = {
    "check": f'<path d="M3.5 8.5l3 3 6-7" {STROKE}/>',
    "cross": f'<path d="M4.5 4.5l7 7M11.5 4.5l-7 7" {STROKE}/>',
    "dot": '<circle cx="8" cy="8" r="3" fill="currentColor"/>',
    "minus": f'<circle cx="8" cy="8" r="6" {STROKE}/><path d="M5.5 8h5" {STROKE}/>',
    "circle": f'<circle cx="8" cy="8" r="6" {STROKE}/>',
    "circle-dash": f'<circle cx="8" cy="8" r="6" {STROKE} stroke-dasharray="3.2 3"/>',
    "circle-check": '<circle cx="8" cy="8" r="7" fill="currentColor"/>'
                    '<path d="M4.6 8.3l2.3 2.3 4.5-5" fill="none" stroke="var(--surface)" stroke-width="1.8" '
                    'stroke-linecap="round" stroke-linejoin="round"/>',
    "circle-cross": '<circle cx="8" cy="8" r="7" fill="currentColor"/>'
                    '<path d="M5.4 5.4l5.2 5.2M10.6 5.4l-5.2 5.2" fill="none" stroke="var(--surface)" stroke-width="1.8" '
                    'stroke-linecap="round"/>',
    "alert": '<path d="M8 1.6l6.9 12.2H1.1z" fill="currentColor"/>'
             '<path d="M8 6.2v3.6M8 11.9v.2" fill="none" stroke="var(--surface)" stroke-width="1.7" stroke-linecap="round"/>',
    "ext": f'<path d="M6.5 3.5h-3v9h9v-3M9.5 3.5h3v3M12.5 3.5l-5.5 5.5" {STROKE}/>',
    "search": f'<circle cx="7" cy="7" r="4.5" {STROKE}/><path d="M10.5 10.5l3.5 3.5" {STROKE}/>',
    "theme": '<path d="M8 1.5a6.5 6.5 0 1 0 0 13z" fill="currentColor"/>' + f'<circle cx="8" cy="8" r="6.5" {STROKE}/>',
    "arrow": f'<path d="M3 8h10M9 4l4 4-4 4" {STROKE}/>',
    "bang": f'<path d="M8 3.5v5.5M8 12v.4" {STROKE}/>',
}
PARTS = [  # Teile des Gesamtbalkens in fester Reihenfolge: Schlüssel, Name, CSS-Klasse
    ("reached", "erreicht", "reached"),
    ("proposed", "als erreicht vorgeschlagen", "proposed"),
    ("proposed_failed", "als nicht erreicht vorgeschlagen", "proposed-failed"),
    ("failed", "nicht erreicht", "failed"),
    ("open", "offen", "open"),
]
TILE_ICONS = {"reached": "check", "done": "check", "proposed": "dot", "proposed-failed": "cross",
              "failed": "cross", "open": "", "attention": "bang"}
TILE_TEXT = {  # Prüfstand von Aussagen und Belegen
    "done": "geprüft", "proposed": "vorgeschlagen, Zweitprüfung offen", "open": "noch nicht eingestuft",
    "attention": "erneut zu prüfen",
}
COVER_HEAD = ('<th scope="col">Meilensteine</th><th scope="col" class="num">erreicht</th>'
              '<th scope="col" class="num">vorgeschlagen</th><th scope="col" class="num">Aussagen geprüft</th>'
              '<th scope="col" class="num">Belege geprüft</th>')
MAP_LEGEND = [("done", "geprüft oder erreicht"), ("proposed", "vorgeschlagen"), ("open", "offen"),
              ("proposed-failed", "als nicht erreicht vorgeschlagen"), ("failed", "nicht erreicht"),
              ("attention", "erneut zu prüfen")]
LOGO = ('<svg viewBox="0 0 32 32" aria-hidden="true" focusable="false">'
        '<rect width="32" height="32" rx="7" fill="#1c5cab"/>'
        '<path d="M8 22h4l4-12h8" fill="none" stroke="#fff" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>'
        '<circle cx="8" cy="22" r="3" fill="#fff"/><circle cx="16" cy="10" r="3" fill="#1c5cab" stroke="#fff" stroke-width="2"/>'
        '<circle cx="24" cy="10" r="3" fill="#1c5cab" stroke="#fff" stroke-width="2" stroke-dasharray="2.4 2"/></svg>')

# Fachprofile aus atlas.yaml: eigene Bezeichnungen je Fach, gesetzt in write_site().
PROFILES: dict = {}


# --------------------------------------------------------------------------
# Bausteine
# --------------------------------------------------------------------------


def icon(name: str) -> str:
    return f'<svg class="i" viewBox="0 0 16 16" aria-hidden="true" focusable="false">{ICONS[name]}</svg>'


def label(value: str | None, field: str | None = None) -> str:
    override = PROFILES.get(field, {}).get("labels", {})
    return override.get(value) or LABELS.get(value, value or "offen")


def chip(value: str, field: str | None = None, draft: bool = False) -> str:
    tone, symbol = MARKS.get(value, ("none", "circle"))
    text = label(value, field)
    if draft:
        return f'<span class="chip is-draft t-none">{icon("circle-dash")}Vorschlag: {e(text)}</span>'
    return f'<span class="chip t-{tone}">{icon(symbol)}{e(text)}</span>'


def number(value) -> str:
    return str(value).replace(".", ",") if isinstance(value, float) else str(value)


def plural(count: int, one: str, many: str) -> str:
    return f"{count} {one if count == 1 else many}"


def slug(text: str) -> str:
    table = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"})
    return re.sub(r"[^a-z0-9]+", "-", text.lower().translate(table)).strip("-")


def people(record: dict) -> str:
    return " und ".join(p for p in (record.get("extracted_by"), record.get("reviewed_by")) if p)


def station_state(milestone: dict) -> str:
    return milestone["state"]


def node(state: str) -> str:
    symbol = STATIONS[state][1]
    inner = f'<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false">{ICONS[symbol]}</svg>' if symbol else ""
    return f'<span class="node">{inner}</span>'


def route(goal: dict, prefix: str) -> str:
    """Die Stationen eines Ziels als waagerechte Route. Jede Station führt zum Meilenstein."""
    if not goal["milestones"]:
        return '<p class="muted small">Für dieses Ziel sind noch keine Meilensteine definiert.</p>'
    items = ""
    for ms in goal["milestones"]:
        state = station_state(ms)
        items += (f'<li class="station is-{state}"><a href="{prefix}ziele/{e(goal["id"])}.html#{e(ms["id"])}" '
                  f'title="{e(ms["title"])}: {e(STATIONS[state][0])}">{node(state)}'
                  f'<span class="station-label">{e(ms["title"])}</span>'
                  f'<span class="sr">: {e(STATIONS[state][0])}</span></a></li>')
    return f'<ol class="route" aria-label="Meilensteine: {e(count_text(goal, plain=True))}">{items}</ol>'


def count_text(goal: dict, plain: bool = False) -> str:
    if goal["milestones_total"] is None:
        return "Katalog offen"
    head = f"{goal['milestones_reached']} von {goal['milestones_total']}"
    text = f"{head} Meilensteinen erreicht" if plain else f"<strong>{head}</strong> Meilensteinen erreicht"
    if goal["milestones_proposed"]:
        text += f" · {goal['milestones_proposed']} vorgeschlagen"
    declined = sum(1 for ms in goal["milestones"] if station_state(ms) == "proposed-failed")
    if declined:
        text += f" · {declined} als nicht erreicht vorgeschlagen"
    return text


def basis_phrase(claim: dict) -> str:
    """'3 Quellen, 2 Ereignisse': wie viele Veröffentlichungen auf wie vielen Grundlagen."""
    sources, bases = claim["supporting_sources"], claim["supporting_observations"]
    if not sources:
        return "keine stützende Quelle"
    kinds = {b["kind"] for ev in claim["evidence"] if ev["counts_as_support"] for b in ev["basis"]}
    one, many = KINDS[kinds.pop()] if len(kinds) == 1 else ("Grundlage", "Grundlagen")
    return f"{plural(sources, 'Quelle', 'Quellen')}, {plural(bases, one, many)}"


def claim_chip(claim: dict) -> str:
    if claim["decision"]:
        return chip(claim["evidence_status"], claim["field"])
    if claim.get("proposed_status"):
        return chip(claim["proposed_status"], claim["field"], draft=True)
    return chip("offen")


def alerts(item: dict) -> str:
    out = ""
    if item.get("conflict"):
        out += (f'<div class="alert">{icon("alert")}<p><strong>Widersprechende Entscheidungen.</strong> '
                f'Bis zur fachlichen Klärung gilt der Stand davor. <span class="id">{e(", ".join(item["conflict"]))}</span></p></div>')
    for reason in item.get("reexamine", []):
        out += f'<div class="alert">{icon("alert")}<p><strong>Erneut zu prüfen.</strong> {e(reason)}</p></div>'
    return out


def decision_box(dec: dict, field: str | None, draft: bool, queue_href: str = "", show_chip: bool = True) -> str:
    """Eine Einstufung mit Begründung. Ein Vorschlag ist gestrichelt gerahmt."""
    if draft:
        who = f"von {e(dec['suggested_by'])}" if dec.get("suggested_by") else (f"von {e(people(dec))}" if people(dec) else "")
        state = "in Prüfung" if dec.get("status") == "in_pruefung" else "Zweitprüfung offen"
        meta = f"Vorgeschlagen am {e(dec['date'])} {who} · {state}"
        if queue_href:
            meta += f' · <a href="{e(queue_href)}">Zur Prüfung</a>'
    else:
        meta = f"Freigegeben am {e(dec['date'])} von {e(people(dec))}"
        if dec.get("assurance"):
            meta += " · Absicherung: " + e(", ".join(label(a) for a in dec["assurance"]))
    extra = f'<p><strong>Abweichende Einschätzung.</strong> {e(dec["dissent"])}</p>' if dec.get("dissent") else ""
    mark = f'<p>{chip(dec["outcome"], field, draft)}</p>' if show_chip else ""
    return (f'<div class="note-box{"" if draft else " is-final"}" id="{e(dec["id"])}">'
            f'{mark}<p>{e(dec["rationale"])}</p>{extra}'
            f'<p class="small muted">{meta}</p></div>')


def page(title: str, body: str, ctx: dict, depth: int = 0, current: str = "", description: str = "") -> str:
    up = "../" * depth
    config = ctx["config"]
    favicon = "data:image/svg+xml," + quote(LOGO.replace('viewBox', 'xmlns="http://www.w3.org/2000/svg" viewBox'))

    def nav(href: str, text: str, key: str, extra: str = "") -> str:
        mark = ' aria-current="page"' if key == current else ""
        return f'<a href="{up}{href}"{mark}>{text}{extra}</a>'

    queue = f'<span class="count">{len(ctx["queue"])}<span class="sr"> Einträge</span></span>' if ctx["queue"] else ""
    full_title = config["title"] if current == "index" else f"{title} · {config['title']}"
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(full_title)}</title>
<meta name="description" content="{e(description or config['title'])}">
<link rel="icon" href="{favicon}">
<script>try{{var t=localStorage.getItem("atlas-theme");if(t==="dark"||t==="light")document.documentElement.setAttribute("data-theme",t)}}catch(e){{}}</script>
<link rel="stylesheet" href="{up}atlas.css">
</head>
<body>
<a class="skip" href="#inhalt">Zum Inhalt springen</a>
<header class="top"><div class="wrap">
<a class="brand" href="{up}index.html">{LOGO}{e(config['title'])}</a>
<nav class="nav" aria-label="Hauptnavigation">
{nav("index.html", "Übersicht", "index")}
{nav("ziele.html", "Ziele", "ziele")}
{nav("pruefen.html", "Offene Prüfungen", "pruefen", queue)}
{nav("verlauf.html", "Verlauf", "verlauf")}
<a href="{e(config['repo_url'])}#readme">Methodik</a>
<button class="theme" id="theme" type="button" hidden>{icon("theme")}<span>Dunkles Design</span></button>
</nav>
</div></header>
<main id="inhalt"><div class="wrap">
{body}
</div></main>
<footer class="foot"><div class="wrap">
<p>Erzeugt aus den versionierten Daten im Repository. Jede Zahl lässt sich über die verlinkten
Einstufungen und Belege bis zur Fundstelle zurückverfolgen.</p>
<nav aria-label="Daten und Quelltext">
<a href="{up}progress.json">Stand als JSON</a>
<a href="{up}history.json">Verlauf als JSON</a>
<a href="{e(config['repo_url'])}">Quelltext</a>
</nav>
</div></footer>
<script src="{up}atlas.js"></script>
</body>
</html>
"""


def percent(part: int, total: int) -> str:
    return f"{round(100 * part / total)} %" if total else "0 %"


def segbar(counts: dict, tall: bool = False) -> str:
    """Ein Ganzes, geteilt nach Zustand. Hoch mit Zahlen im Block, schmal neben Zahlen in der Tabelle."""
    total = counts["total"]
    if not total:
        return ""
    blocks = ""
    for key, name, css in PARTS:
        n = counts[key]
        if not n:
            continue
        if tall:
            text = f"{n} von {total} {name} ({percent(n, total)})"
            printed = f'<span class="n">{n}</span>' if n / total >= 0.06 else ""
            blocks += (f'<span class="seg s-{css}" style="flex-grow:{n}" tabindex="0" role="img" '
                       f'aria-label="{e(text)}" title="{e(text)}">{printed}</span>')
        else:
            blocks += f'<span class="seg s-{css}" style="flex-grow:{n}"></span>'
    return f'<div class="segbar {"tall" if tall else "thin"}"{"" if tall else ' aria-hidden="true"'}>{blocks}</div>'


def bar_legend(counts: dict) -> str:
    """Namen in der Reihenfolge der Blöcke. Eine Zahl steht hier nur, wenn sie im Block keinen Platz hat."""
    items = ""
    for key, name, css in PARTS:
        n = counts[key]
        if n:
            extra = "" if n / counts["total"] >= 0.06 else f" ({n})"
            items += f'<li><span class="swatch s-{css}"></span>{e(name)}{extra}</li>'
    return f'<ul class="legend" aria-label="Legende des Balkens">{items}</ul>'


def tile(state: str, href: str, tip: str) -> str:
    symbol = TILE_ICONS[state]
    inner = f'<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false">{ICONS[symbol]}</svg>' if symbol else ""
    return f'<a class="tile is-{state}" href="{e(href)}" title="{e(tip)}">{inner}<span class="sr">{e(tip)}</span></a>'


def atlas_map(state: dict, prefix: str = "") -> str:
    """Die Karte: je Ziel eine Reihe Kacheln für Meilensteine, Aussagen und Belege."""
    blocks = ""
    for goal in state["goals"]:
        claims = [c for c in state["claims"] if c["goal_ids"][0] == goal["id"]]
        rows = [
            ("Meilensteine", "".join(
                tile(ms["state"], f"{prefix}ziele/{goal['id']}.html#{ms['id']}",
                     f"Meilenstein: {ms['title']} · {STATIONS[ms['state']][0]}") for ms in goal["milestones"])),
            ("Aussagen", "".join(
                tile(c["review_state"], f"{prefix}aussagen/{c['id']}.html",
                     f"Aussage: {c['statement']} · {TILE_TEXT[c['review_state']]}") for c in claims)),
            ("Belege", "".join(
                tile(ev["review_state"], f"{prefix}aussagen/{c['id']}.html#{ev['id']}",
                     f"Beleg: {ev['study']['short_label']}, {ev['locator']} · {TILE_TEXT[ev['review_state']]}")
                for c in claims for ev in c["evidence"])),
        ]
        body = "".join(f'<div><dt>{name}</dt><dd>{tiles or "<span class=muted>noch keine</span>"}</dd></div>'
                       for name, tiles in rows)
        blocks += (f'<div class="map-goal"><span class="k">{e(goal["field"])}</span>'
                   f'<a class="map-title" href="{prefix}ziele/{e(goal["id"])}.html">{e(goal["title"])}</a>'
                   f'<dl class="map-rows">{body}</dl></div>')
    items = "".join(f'<li><span class="tile is-{state}" aria-hidden="true">'
                    + (f'<svg viewBox="0 0 16 16">{ICONS[TILE_ICONS[state]]}</svg>' if TILE_ICONS[state] else "")
                    + f'</span>{e(text)}</li>' for state, text in MAP_LEGEND)
    return f'<ul class="legend" aria-label="Legende der Karte">{items}</ul><div class="map">{blocks}</div>'


def cover_table(state: dict, prefix: str = "") -> str:
    """Zahlen je Ziel und gesamt. Zugleich die Tabellenansicht zu Balken und Karte."""
    cells = cover_cells
    rows = "".join(
        f'<tr><th scope="row"><span class="k">{e(g["field"])}</span>'
        f'<a href="{prefix}ziele/{e(g["id"])}.html">{e(g["title"])}</a></th>{cells(g["tally"])}</tr>' for g in state["goals"])
    return f"""<div class="tablewrap"><table class="cover">
<thead><tr><th scope="col">Fach und Ziel</th>{COVER_HEAD}</tr></thead>
<tbody>{rows}</tbody>
<tfoot><tr><th scope="row">Gesamt</th>{cells(state["totals"])}</tr></tfoot>
</table></div>"""


def needs(state: dict, prefix: str = "", extra: str = "") -> str:
    """Was bis zum vollen Zählerstand fehlt, nach Art der fehlenden Arbeit."""
    m = state["totals"]["milestones"]
    items = ""
    waiting = m["proposed"] + m["proposed_failed"]
    if waiting:
        items += (f'<li><b>{waiting}</b> {"Meilenstein wartet" if waiting == 1 else "Meilensteine warten"} auf die '
                  f'Zweitprüfung. <a href="{prefix}pruefen.html">Zu den offenen Prüfungen</a></li>')
    missing = [(g, ms) for g in state["goals"] for ms in g["milestones"] if ms["state"] == "open"]
    if missing:
        links = ", ".join(f'<a href="{prefix}ziele/{e(g["id"])}.html#{e(ms["id"])}">{e(ms["title"])}</a> ({e(g["field"])})'
                          for g, ms in missing)
        items += (f'<li><b>{len(missing)}</b> {"Meilenstein hat" if len(missing) == 1 else "Meilensteine haben"} '
                  f'noch keinen Vorschlag: {links}</li>')
    again = [c for c in state["claims"] if c["review_state"] == "attention"]
    if again:
        links = ", ".join(f'<a href="{prefix}aussagen/{e(c["id"])}.html">{e(c["statement"])}</a>' for c in again)
        items += f'<li><b>{len(again)}</b> {"Aussage ist" if len(again) == 1 else "Aussagen sind"} erneut zu prüfen: {links}</li>'
    if m["failed"]:
        items += f'<li><b>{m["failed"]}</b> {"Meilenstein gilt" if m["failed"] == 1 else "Meilensteine gelten"} als nicht erreicht.</li>'
    items += extra
    if not items:
        items = "<li>Alle Meilensteine sind erreicht und geprüft.</li>"
    return f'<ul class="needs">{items}</ul>'


def chart(series: list[dict]) -> str:
    """Verlauf in Zahlen: erreichte Meilensteine als Linie, Gesamtzahl gestrichelt. Erst ab zwei Tagen sinnvoll."""
    if len(series) < 2:
        return ""
    width, height, left, right, top, bottom = 640, 230, 34, 104, 14, 30
    first = date.fromisoformat(series[0]["date"])
    span = max((date.fromisoformat(series[-1]["date"]) - first).days, 1)
    peak = max(max(p["total"] for p in series), 1)
    x = lambda p: left + (date.fromisoformat(p["date"]) - first).days / span * (width - left - right)
    y = lambda value: top + (1 - value / peak) * (height - top - bottom)

    def steps(key: str) -> str:
        path = f"M{x(series[0]):.1f} {y(series[0][key]):.1f}"
        for point in series[1:]:
            path += f"H{x(point):.1f}V{y(point[key]):.1f}"
        return path

    ticks = sorted({0, peak // 2, peak})
    grid = "".join(f'<line class="grid" x1="{left}" x2="{width - right}" y1="{y(v):.1f}" y2="{y(v):.1f}"/>'
                   f'<text class="tick" x="{left - 8}" y="{y(v) + 4:.1f}" text-anchor="end">{v}</text>' for v in ticks)
    dots = "".join(f'<circle class="dot" cx="{x(p):.1f}" cy="{y(p["reached"]):.1f}" r="4.5">'
                   f'<title>{e(p["date"])}: {p["reached"]} von {p["total"]} erreicht</title></circle>' for p in series)
    last = series[-1]
    y_reached, y_total = y(last["reached"]), y(last["total"])
    if abs(y_reached - y_total) < 16:
        y_total = y_reached - 16
    end = width - right + 10
    labels = (f'<text class="end" x="{end}" y="{y_reached + 4:.1f}">erreicht {last["reached"]}</text>'
              f'<text class="end muted" x="{end}" y="{y_total + 4:.1f}">gesamt {last["total"]}</text>')
    days = (f'<text class="tick" x="{left}" y="{height - 8}">{e(series[0]["date"])}</text>'
            f'<text class="tick" x="{width - right}" y="{height - 8}" text-anchor="end">{e(last["date"])}</text>')
    summary = (f"Verlauf vom {series[0]['date']} bis {last['date']}: zuletzt {last['reached']} von "
               f"{last['total']} Meilensteinen erreicht.")
    return (f'<figure class="chart"><svg viewBox="0 0 {width} {height}" role="img" aria-label="{e(summary)}">'
            f'{grid}<path class="total" d="{steps("total")}"/><path class="reached" d="{steps("reached")}"/>'
            f'{dots}{labels}{days}</svg>'
            f'<figcaption class="small muted">Durchgezogen: erreichte Meilensteine. Gestrichelt: Meilensteine im Katalog.'
            f'</figcaption></figure>')


def series_table(series: list[dict]) -> str:
    rows, before = "", None
    for point in series:
        change = "–" if before is None else f"{point['reached'] - before:+d}"
        rows += (f'<tr><th scope="row">{e(point["date"])}</th><td class="num">{point["reached"]}</td>'
                 f'<td class="num">{point["total"]}</td><td class="num">{change}</td></tr>')
        before = point["reached"]
    return f"""<div class="tablewrap"><table class="cover">
<thead><tr><th scope="col">Tag</th><th scope="col" class="num">erreicht</th><th scope="col" class="num">im Katalog</th>
<th scope="col" class="num">Änderung</th></tr></thead><tbody>{rows}</tbody></table></div>"""


def badge_svg(name: str, value: str) -> str:
    """Abzeichen für die README, etwa 'Meilensteine 0/19'."""
    left, right = 12 + round(6.7 * len(name)), 12 + round(7.2 * len(value))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{left + right}" height="20" role="img" '
            f'aria-label="{e(name)}: {e(value)}"><title>{e(name)}: {e(value)}</title>'
            f'<rect width="{left + right}" height="20" rx="3" fill="#43505d"/>'
            f'<path d="M{left} 0h{right - 3}a3 3 0 0 1 3 3v14a3 3 0 0 1-3 3H{left}z" fill="#1c5cab"/>'
            f'<g fill="#fff" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11" text-anchor="middle">'
            f'<text x="{left / 2}" y="14">{e(name)}</text><text x="{left + right / 2}" y="14">{e(value)}</text></g></svg>\n')


def cover_cells(counts: dict) -> str:
    m = counts["milestones"]
    return (f'<td class="bar">{segbar(m)}</td><td class="num">{m["reached"]} von {m["total"]}</td>'
            f'<td class="num">{m["proposed"]}</td>'
            f'<td class="num">{counts["claims"]["reviewed"]} von {counts["claims"]["total"]}</td>'
            f'<td class="num">{counts["evidence"]["reviewed"]} von {counts["evidence"]["total"]}</td>')


def overall(counts: dict, stats: list[tuple[str, str]], title: str = "Gesamtstand") -> str:
    """Der Stand als große Zahl mit Balken. stats sind weitere Kennzahlen als (Wert, Beschriftung)."""
    m = counts["milestones"]
    scenario = ""
    if m["proposed"]:
        scenario = (f'<p class="small muted">Rechnung, kein Stand: Würden alle offenen Vorschläge freigegeben, wären '
                    f'{m["reached"] + m["proposed"]} von {m["total"]} Meilensteinen erreicht '
                    f'({percent(m["reached"] + m["proposed"], m["total"])}).</p>')
    items = "".join(f"<li><b>{value}</b><span>{text}</span></li>" for value, text in stats)
    return f"""<section class="panel overall" aria-labelledby="gesamt">
<h2 class="k" id="gesamt">{e(title)}</h2>
<div class="overall-head">
<p class="hero"><b>{m['reached']} von {m['total']}</b><span>Meilensteinen erreicht · {percent(m['reached'], m['total'])}</span></p>
<ul class="stats">{items}</ul>
</div>
{segbar(m, tall=True)}
{bar_legend(m)}
{scenario}
</section>"""


def science_map(state: dict) -> str:
    """Der Über-Atlas: jedes Fachgebiet der Systematik als Feld, mit oder ohne Einträge."""
    out = ""
    for realm in state["realms"]:
        cells = ""
        covered = sum(1 for a in realm["areas"] if a["goal_ids"])
        for area in realm["areas"]:
            head = f'<span class="area-code">{e(area["code"])}</span><span class="area-name">{e(area["name"])}</span>'
            if area["goal_ids"]:
                m = area["tally"]["milestones"]
                meta = f'{m["reached"]} von {m["total"]} erreicht'
                if m["proposed"]:
                    meta += f' · {m["proposed"]} vorgeschlagen'
                cells += (f'<a class="area has" href="fach/{slug(area["name"])}.html">{head}{segbar(m)}'
                          f'<span class="area-meta">{meta}</span>'
                          f'<span class="area-meta">{plural(len(area["goal_ids"]), "Ziel", "Ziele")}</span></a>')
            else:
                cells += f'<div class="area">{head}<span class="area-meta">noch kein Eintrag</span></div>'
        out += (f'<section class="realm"><h3>{e(realm["name"])} '
                f'<small>{covered} von {len(realm["areas"])} mit Einträgen</small></h3>'
                f'<div class="areas">{cells}</div></section>')
    return out


def goal_list(goals: list[dict], ctx: dict, prefix: str = "", with_filter: bool = True) -> str:
    """Die Ziele als Routen, nach Fach gruppiert. Mit Suche und Fachfilter, wenn gewünscht."""
    fields = sorted({g["field"] for g in goals})
    sections = ""
    for field in fields:
        rows = ""
        mine = [g for g in goals if g["field"] == field]
        for goal in mine:
            claims = [ctx["claims"][c] for ms in goal["milestones"] for c in ms["claims"]]
            words = [field, goal["title"]] + [ms["title"] for ms in goal["milestones"]]
            words += [c["statement"] for c in claims] + [ev["study"]["short_label"] for c in claims for ev in c["evidence"]]
            nxt = (f'<p class="goal-next"><span class="k">Nächste offene Prüfung</span>{e(goal["open_question"])}</p>'
                   if goal.get("open_question") else "")
            rows += f"""<li class="goal" data-field="{e(field)}" data-search="{e(' '.join(words).lower())}">
<div>
<h4><a href="{prefix}ziele/{e(goal['id'])}.html">{e(goal['title'])}</a></h4>
<p class="goal-count">{count_text(goal)}</p>
{nxt}
</div>
{route(goal, prefix)}
</li>"""
        sections += (f'<section class="field" id="fach-{slug(field)}" data-field="{e(field)}">'
                     f'<h3>{e(field)} <small>{plural(len(mine), "Ziel", "Ziele")}</small></h3>'
                     f'<ul class="goals">{rows}</ul></section>')
    if not with_filter:
        return sections
    pills = '<button class="pill" type="button" data-field="" aria-pressed="true">Alle Fächer</button>' + "".join(
        f'<button class="pill" type="button" data-field="{e(f)}" aria-pressed="false">{e(f)}</button>' for f in fields)
    return f"""<div class="filters" id="filter" role="search" hidden>
<div class="search">{icon("search")}<label class="sr" for="suche">Ziele, Aussagen und Quellen durchsuchen</label>
<input type="search" id="suche" placeholder="Ziele, Aussagen und Quellen durchsuchen" autocomplete="off"></div>
<div class="pills" role="group" aria-label="Nach Fach filtern">{pills}</div>
</div>
<p class="result" id="treffer" role="status" aria-live="polite"></p>
{sections}
<div class="empty" id="leer" hidden><p>Kein Ziel passt zu dieser Suche.</p>
<button class="btn ghost s" type="button" id="zuruecksetzen">Suche zurücksetzen</button></div>"""


ROUTE_INTRO = ('<p class="scope">Jedes Ziel ist eine Route aus Meilensteinen. Als erreicht gilt eine Station erst, wenn '
               'zwei Personen die Einstufung freigegeben haben. Bis dahin bleibt sie ein Vorschlag.</p>')
CATALOG_NOTE = ('<p class="small muted" style="margin-top:2rem">Die Zählung bezieht sich auf den jeweiligen Zielkatalog. '
                'Aus einem Zählerstand lässt sich keine Aussage zum gesamten Forschungsstand eines Fachs ableiten.</p>')


def area_of(goal: dict, ctx: dict) -> dict | None:
    return ctx["areas"].get(goal.get("area"))


def crumbs(goal: dict, ctx: dict, with_goal: bool = False) -> str:
    """Rückweg: Übersicht, Fachgebiet und bei Aussagen das Ziel."""
    area = area_of(goal, ctx)
    middle = (f'<li><a href="../fach/{area["slug"]}.html">{e(area["name"])}</a></li>' if area
              else f'<li>{e(goal["field"])}</li>')
    last = f'<li><a href="../ziele/{e(goal["id"])}.html">{e(goal["title"])}</a></li>' if with_goal else ""
    return f'<ol class="crumbs"><li><a href="../index.html">Übersicht</a></li>{middle}{last}</ol>'


def legend() -> str:
    items = "".join(f'<li class="is-{state}">{node(state)}{e(text)}</li>' for state, (text, _) in STATIONS.items())
    return f'<ul class="legend" aria-label="Legende der Stationen">{items}</ul>'


# --------------------------------------------------------------------------
# Seiten
# --------------------------------------------------------------------------


def render_index(state: dict, ctx: dict) -> str:
    """Der Über-Atlas: das Ganze zuerst, dann der Weg in die Fachgebiete."""
    goals, totals, coverage = state["goals"], state["totals"], state["coverage"]
    fields = sorted({g["field"] for g in goals})
    stats = [(f"{totals['claims']['reviewed']} von {totals['claims']['total']}", "Aussagen geprüft"),
             (f"{totals['evidence']['reviewed']} von {totals['evidence']['total']}", "Belege geprüft"),
             (str(len(ctx["queue"])), '<a href="pruefen.html">offene Prüfungen</a>')]
    if coverage["areas"]:
        stats.append((f"{coverage['covered']} von {coverage['areas']}", "Fachgebieten mit Einträgen"))
    else:
        stats.append((str(len(goals)), f"{'Ziel' if len(goals) == 1 else 'Ziele'} in {plural(len(fields), 'Fach', 'Fächern')}"))
    history = ""
    if len(state["series"]) > 1:
        history = f'<h2>Verlauf</h2>{chart(state["series"])}<p><a href="verlauf.html">Alle Änderungen ansehen</a></p>'
    if coverage["areas"]:
        rows = "".join(
            f'<tr><th scope="row"><span class="k">{e(realm["name"])}</span>'
            f'<a href="fach/{slug(area["name"])}.html">{e(area["name"])}</a></th>'
            f'<td class="num">{len(area["goal_ids"])}</td>{cover_cells(area["tally"])}</tr>'
            for realm in state["realms"] for area in realm["areas"] if area["goal_ids"])
        table = f"""<div class="tablewrap"><table class="cover">
<thead><tr><th scope="col">Fachgebiet</th><th scope="col" class="num">Ziele</th>{COVER_HEAD}</tr></thead>
<tbody>{rows}</tbody>
<tfoot><tr><th scope="row">Gesamt</th><td class="num">{len(goals)}</td>{cover_cells(totals)}</tr></tfoot>
</table></div>"""
        empty = coverage["areas"] - coverage["covered"]
        more = (f'<li><b>{empty}</b> {"Fachgebiet hat" if empty == 1 else "Fachgebiete haben"} noch keinen Eintrag. '
                f'<a href="{e(ctx["repo"])}/blob/{e(ctx["branch"])}/CONTRIBUTING.md">So trägst du ein Ziel bei</a></li>'
                if empty else "")
        middle = f"""<h2>Karte der Wissenschaften</h2>
<p class="scope">Die Karte zeigt alle {coverage['areas']} Fachgebiete der Systematik in {len(state['realms'])} Bereichen,
auch die ohne Einträge. Ein Fachgebiet mit Einträgen führt zu seinem eigenen Atlas.</p>
{science_map(state)}
<p class="small muted">Gliederung: {e(ctx['taxonomy'].get('source', ''))}.</p>
<h2>Stand nach Fachgebiet</h2>
{table}
<h2>Was noch fehlt</h2>
{needs(state, extra=more)}"""
    else:
        middle = f"""<h2>Karte des Atlas</h2>
<p class="scope">Jede Kachel ist ein Meilenstein, eine Aussage oder ein Beleg und führt zu ihrem Eintrag.</p>
{atlas_map(state)}
<h2>Stand nach Fach und Ziel</h2>
{cover_table(state)}
<h2>Was noch fehlt</h2>
{needs(state)}"""
    body = f"""<h1>{e(ctx['config']['title'])}</h1>
<p class="lead">Der Atlas zeigt, wie weit die Forschung bei ausgewählten Zielen ist, welche Veröffentlichungen
das tragen und welche Prüfung als Nächstes ansteht.</p>
{overall(totals, stats)}
{middle}
{history}
<div class="actions">
<a class="btn" href="ziele.html">Alle {len(goals)} Ziele ansehen</a>
<a class="btn ghost" href="pruefen.html">Offene Prüfungen</a>
</div>
{CATALOG_NOTE}"""
    return page("Übersicht", body, ctx, current="index",
                description="Über-Atlas: Gesamtstand und Karte aller Wissenschaften mit dem Weg in die Fachgebiete.")


def render_goals(state: dict, ctx: dict) -> str:
    """Alle Ziele auf einer Seite: Karte der Einträge und die Routen mit Suche."""
    body = f"""<ol class="crumbs"><li><a href="index.html">Übersicht</a></li></ol>
<h1>Alle Ziele</h1>
<p class="lead">{plural(len(state['goals']), 'Forschungsziel', 'Forschungsziele')} mit ihren Meilensteinen, Aussagen und Belegen.</p>
<h2>Karte der Einträge</h2>
<p class="scope">Jede Kachel ist ein Meilenstein, eine Aussage oder ein Beleg und führt zu ihrem Eintrag.
Eine Kachel gilt erst als geprüft, wenn zwei Personen sie freigegeben haben.</p>
{atlas_map(state)}
<h2 id="ziele">Ziele im Einzelnen</h2>
{ROUTE_INTRO}
{legend()}
{goal_list(state['goals'], ctx)}
{CATALOG_NOTE}"""
    return page("Alle Ziele", body, ctx, current="ziele",
                description="Alle Forschungsziele des Atlas als Routen aus Meilensteinen.")


def render_area(realm: dict, area: dict, state: dict, ctx: dict) -> str:
    """Der Atlas eines Fachgebiets: derselbe Aufbau wie das Ganze, begrenzt auf ein Fach."""
    goals = [ctx["goals"][g] for g in area["goal_ids"]]
    ids = set(area["goal_ids"])
    claims = [c for c in state["claims"] if c["goal_ids"][0] in ids]
    sub = {"goals": goals, "claims": claims, "totals": area["tally"]}
    waiting = sum(1 for q in ctx["queue"] if q["goal_id"] in ids)
    stats = [(f"{area['tally']['claims']['reviewed']} von {area['tally']['claims']['total']}", "Aussagen geprüft"),
             (f"{area['tally']['evidence']['reviewed']} von {area['tally']['evidence']['total']}", "Belege geprüft"),
             (str(waiting), '<a href="../pruefen.html">offene Prüfungen</a>'),
             (str(len(goals)), "Ziel" if len(goals) == 1 else "Ziele")]
    body = f"""<ol class="crumbs"><li><a href="../index.html">Übersicht</a></li><li>{e(realm['name'])}</li></ol>
<p class="k">Fachgebiet {e(area['code'])}</p>
<h1>{e(area['name'])}</h1>
{overall(area['tally'], stats, title="Stand des Fachgebiets")}
<h2>Karte der Einträge</h2>
<p class="scope">Jede Kachel ist ein Meilenstein, eine Aussage oder ein Beleg und führt zu ihrem Eintrag.</p>
{atlas_map(sub, "../")}
<h2>Stand nach Ziel</h2>
{cover_table(sub, "../")}
<h2>Was noch fehlt</h2>
{needs(sub, "../")}
<h2>Ziele im Einzelnen</h2>
{ROUTE_INTRO}
{legend()}
{goal_list(goals, ctx, "../", with_filter=False)}
{CATALOG_NOTE}"""
    return page(area["name"], body, ctx, depth=1,
                description=f"Atlas des Fachgebiets {area['name']}: Stand, Karte und Ziele.")


def render_goal(goal: dict, ctx: dict) -> str:
    steps = ""
    for ms in goal["milestones"]:
        state = station_state(ms)
        if ms["decision"]:
            status, boxes = chip(ms["status"]), decision_box(ms["decision"], None, draft=False, show_chip=False)
        elif ms["open_proposals"]:
            status = chip(ms["open_proposals"][-1]["outcome"], draft=True)
            boxes = "".join(decision_box(p, None, True, f"../pruefen.html#q-{p['id']}", show_chip=len(ms["open_proposals"]) > 1)
                            for p in ms["open_proposals"])
        else:
            status = chip("offen")
            boxes = f'<p class="muted">{e(ms["note"])}</p>' if ms.get("note") else ""
        rows = ""
        for cid in ms["claims"]:
            claim = ctx["claims"][cid]
            rows += (f'<li><a class="claim-row" href="../aussagen/{e(cid)}.html"><span class="st">{e(claim["statement"])}</span>'
                     f'<span class="meta">{claim_chip(claim)}<span>{e(basis_phrase(claim))}</span></span></a></li>')
        claims = (f'<ul class="claims">{rows}</ul>' if rows
                  else '<p class="muted small">Zu diesem Meilenstein ist noch keine Aussage erfasst.</p>')
        earlier = "".join(decision_box(d, None, draft=False) for d in reversed(ms["earlier_decisions"]))
        if earlier:
            earlier = f'<details><summary>Frühere Einstufungen</summary>{earlier}</details>'
        steps += f"""<li class="step is-{state}" id="{e(ms['id'])}">
{node(state)}
<div class="step-body">
<div class="step-head"><h3>{e(ms['title'])}</h3>{status}</div>
{alerts(ms)}
<div class="fact"><span class="k">Erfüllungskriterium</span><p>{e(ms['criterion'])}</p></div>
{boxes}{earlier}
<div><span class="k">Aussagen zu diesem Meilenstein</span>{claims}</div>
</div>
</li>"""
    if not steps:
        steps = '<li class="muted">Für dieses Ziel sind noch keine Meilensteine definiert.</li>'
    catalog = f" · Zielkatalog v{goal['catalog_version']}" if goal["catalog_version"] else ""
    nxt = (f'<p class="scope"><span class="k">Nächste offene Prüfung</span>{e(goal["open_question"])}</p>'
           if goal.get("open_question") else "")
    body = f"""{crumbs(goal, ctx)}
<h1>{e(goal['title'])}</h1>
<p class="goal-count">{count_text(goal)}{catalog} ·
{goal['claims_reviewed']} von {goal['claims_total']} Aussagen geprüft</p>
{nxt}
<h2>Meilensteine</h2>
{legend()}
<ol class="steps">{steps}</ol>"""
    return page(goal["title"], body, ctx, depth=1, description=f"Meilensteine und Belege zum Ziel: {goal['title']}")


def matrix(claim: dict) -> str:
    """Welche Quelle auf welcher Grundlage beruht. Zeigt, wo mehrere Quellen dieselbe Grundlage teilen."""
    bases: dict[str, dict] = {}
    for ev in claim["evidence"]:
        for b in ev["basis"]:
            bases.setdefault(b["id"], b)
    if len(claim["evidence"]) < 2 and len(bases) < 2:
        return ""
    head = "".join(f'<th scope="col" title="{e(b["title"])}">{e(b["short_title"])}'
                   f'<br><span class="muted" style="font-weight:400">{e(KINDS[b["kind"]][0])}</span></th>'
                   for b in bases.values())
    rows = ""
    for ev in claim["evidence"]:
        mine = {b["id"] for b in ev["basis"]}
        cells = "".join(
            ('<td><span class="dot"></span><span class="sr">beruht darauf</span></td>' if bid in mine
             else '<td><span class="sr">nein</span></td>') for bid in bases)
        _, short, tone, symbol = RELATIONS[direction(ev)]
        rows += (f'<tr><th scope="row"><a href="#{e(ev["id"])}">{e(ev["study"]["short_label"])}</a></th>'
                 f'<td><span class="chip t-{tone}">{icon(symbol)}{e(short)}</span></td>{cells}</tr>')
    return (f'<div class="matrix-wrap"><table class="matrix"><caption class="sr">Quellen und ihre Grundlagen</caption>'
            f'<thead><tr><th scope="col">Quelle</th><th scope="col">Richtung</th>{head}</tr></thead>'
            f'<tbody>{rows}</tbody></table></div>')


def evidence_card(ev: dict, ctx: dict) -> str:
    study = ev["study"]
    _, short, tone, symbol = RELATIONS[direction(ev)]
    marks = f'<span class="chip t-{tone}">{icon(symbol)}{e(short)}</span>'
    marks += f'<span class="chip t-{MARKS[ev["review_status"]][0]}">{icon(MARKS[ev["review_status"]][1])}Prüfung: {e(label(ev["review_status"]))}</span>'
    values = "".join(f"<li><b>{e(k.replace('_', ' '))}:</b> {e(number(v))}</li>" for k, v in ev["values"].items())
    rows = [("Fundstelle", f'<div class="locator"><span>{e(ev["locator"])}</span>'
                           f'<a class="btn ghost s" href="{e(study["url"])}" rel="noopener">Original öffnen {icon("ext")}</a></div>'),
            ("Messgröße", e(ev["metric"])),
            ("Ergebnis", f'<ul class="values">{values}</ul>'),
            ("Unsicherheit", e(ev["uncertainty"]))]
    if ev.get("conditions"):
        rows.append(("Bedingungen", e(ev["conditions"])))
    rows.append(("Grundlage", "<br>".join(f"{e(KINDS[b['kind']][0])}: {e(b['title'])}" for b in ev["basis"])))
    if study["status"] != "aktiv":
        word = "Korrigiert" if study["status"] == "korrigiert" else "Zurückgezogen"
        rows.append(("Status der Studie", e(f"{word} am {study.get('status_date')}. {study.get('status_note')}")))
    if people(ev):
        check = f"Geprüft von {people(ev)}."
    else:
        check = "Noch nicht geprüft." + (f" Vorgeschlagen von {ev['suggested_by']}." if ev.get("suggested_by") else "")
    rows.append(("Prüfung", e(check)))
    if ev.get("note"):
        rows.append(("Anmerkung", e(ev["note"])))
    body = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows)
    file = f"{ctx['repo']}/blob/{ctx['branch']}/data/evidence/{ev['id']}.yaml"
    return f"""<article class="evidence" id="{e(ev['id'])}">
<header><h3>{e(study['short_label'])}</h3><div class="chips">{marks}</div></header>
<p class="cite">{e(study['label'])} · {e(study['version'])}</p>
<dl class="finding">{body}</dl>
<details><summary>Für Prüfende</summary>
<p>Beleg <span class="id">{e(ev['id'])}</span> · <a href="{e(file)}">Datei im Repository ansehen</a></p></details>
</article>"""


def render_claim(claim: dict, ctx: dict) -> str:
    field = claim["field"]
    goal = ctx["goals"][claim["goal_ids"][0]]
    stations = ", ".join(
        f'<a href="../ziele/{e(ctx["milestones"][m][0]["id"])}.html#{e(m)}">{e(ctx["milestones"][m][1]["title"])}</a>'
        for m in claim["milestone_ids"])
    proposals = claim["open_proposals"]
    if claim["decision"]:
        verdict = chip(claim["evidence_status"], field)
    elif proposals:
        verdict = chip(proposals[-1]["outcome"], field, draft=True)
    else:
        verdict = chip("offen")
    assurance = ", ".join(label(a) for a in claim["assurance"]) or "Noch nichts geprüft"
    status = f"""<div class="status">
<div><span class="k">Evidenzlage</span><p class="v">{verdict}</p>
<p class="why">Welche Schlussfolgerung die Belege in diesem Geltungsbereich tragen.</p></div>
<div><span class="k">Redaktioneller Stand</span><p class="v">{chip(claim['editorial_status'])}</p>
<p class="why">Wie weit die Prüfung der Quellenarbeit durch zwei Personen ist.</p></div>
<div><span class="k">Art der Absicherung</span><p class="v">{e(assurance)}</p>
<p class="why">Was tatsächlich geprüft wurde, etwa Quellenabgleich oder Nachrechnung.</p></div>
</div>"""
    basis = e(basis_phrase(claim))
    basis = basis[0].upper() + basis[1:] + "."
    shared = {d.split(":")[0] for d in claim["shared_dependencies"]}
    if shared == {"Team", "Instrument"}:
        basis += " Alle stützenden Quellen stammen vom selben Team und nutzen dasselbe Instrument."
    elif shared == {"Team"}:
        basis += " Alle stützenden Quellen stammen vom selben Team."
    elif shared == {"Instrument"}:
        basis += " Alle stützenden Quellen nutzen dasselbe Instrument."
    if claim["decision"]:
        verdicts = decision_box(claim["decision"], field, draft=False)
    else:
        verdicts = '<p class="muted">Zu dieser Aussage gibt es noch keine freigegebene Einstufung.</p>'
    verdicts += "".join(decision_box(p, field, True, f"../pruefen.html#q-{p['id']}") for p in proposals)
    earlier = "".join(decision_box(d, field, draft=False) for d in reversed(claim["earlier_decisions"]))
    if earlier:
        verdicts += f"<h3 class=\"group-title\">Frühere Einstufungen</h3>{earlier}"
    groups = ""
    for relation, (heading, _, tone, symbol) in RELATIONS.items():
        cards = "".join(evidence_card(ev, ctx) for ev in claim["evidence"] if direction(ev) == relation)
        if cards:
            count = sum(1 for ev in claim["evidence"] if direction(ev) == relation)
            groups += (f'<h3 class="group-title t-{tone}">{icon(symbol)}{e(heading)} '
                       f'<span class="muted" style="font-weight:400">({count})</span></h3>{cards}')
    if not groups:
        groups = '<p class="muted">Zu dieser Aussage ist noch kein Beleg erfasst.</p>'
    issue = f"{ctx['repo']}/issues/new?template=einwand.md&title=" + quote(f"Einwand zu {claim['id']}")
    file = f"{ctx['repo']}/blob/{ctx['branch']}/data/claims/{claim['id']}.yaml"
    body = f"""{crumbs(goal, ctx, with_goal=True)}
<p class="k">Aussage</p>
<h1 class="statement">{e(claim['statement'])}</h1>
<p class="scope"><span class="k">Geltungsbereich</span>{e(claim['scope'])}</p>
<p class="scope"><span class="k">Gehört zu den Meilensteinen</span>{stations}</p>
{alerts(claim)}
{status}
<h2>Quellen und ihre Grundlagen</h2>
<p class="scope">{basis} Mehrere Veröffentlichungen zur selben Grundlage zählen als eine Beobachtung.</p>
{matrix(claim)}
<h2>Einstufung</h2>
{verdicts}
<h2>Belege</h2>
{groups}
<div class="actions">
<a class="btn" href="{e(issue)}">Einwand oder Korrektur einreichen</a>
<a class="btn ghost" href="{e(file)}">Daten dieser Aussage ansehen</a>
</div>
<p class="id" style="margin-top:1rem">{e(claim['id'])}</p>"""
    return page(claim["statement"], body, ctx, depth=1, description=claim["statement"])


def render_queue(ctx: dict) -> str:
    """Alles, was auf die Zweitprüfung wartet, mit direktem Weg zur Datei."""
    groups, jump = "", ""
    for goal in ctx["goals"].values():
        items = [q for q in ctx["queue"] if q["goal_id"] == goal["id"]]
        if not items:
            continue
        parts = ""
        for heading, wanted in (("Belege", True), ("Einstufungen", False)):
            rows = ""
            for q in items:
                if (q["kind"] == "Beleg") != wanted:
                    continue
                rows += (f'<li id="q-{e(q["id"])}"><div class="what"><span class="k">{e(q["kind"])}</span>'
                         f'<a href="{e(q["href"])}">{e(q["title"])}</a><p>{e(q["text"])}</p></div>'
                         f'<div class="do"><a class="btn ghost s" href="{e(q["edit"])}">Datei bearbeiten {icon("ext")}</a></div></li>')
            if rows:
                count = sum(1 for q in items if (q["kind"] == "Beleg") == wanted)
                parts += (f'<h3 class="group-title">{heading} <span class="muted" style="font-weight:400">({count})</span></h3>'
                          f'<ul class="queue">{rows}</ul>')
        groups += (f'<section id="p-{e(goal["id"])}"><h2><a href="ziele/{e(goal["id"])}.html">{e(goal["title"])}</a></h2>'
                   f'<p class="muted small">{e(goal["field"])}</p>{parts}</section>')
        jump += (f'<li><a href="#p-{e(goal["id"])}">{e(goal["title"])}</a> '
                 f'<span class="count">{len(items)}</span></li>')
    if not groups:
        groups = '<p class="empty">Zurzeit wartet nichts auf eine Prüfung.</p>'
    else:
        groups = f'<h2>Nach Ziel</h2><ul class="jump">{jump}</ul>' + groups
    body = f"""<h1>Offene Prüfungen</h1>
<p class="lead">{plural(len(ctx['queue']), 'Eintrag wartet', 'Einträge warten')} auf die Freigabe durch zwei Personen.
Erst danach verändert ein Eintrag den Zählerstand und erscheint im Verlauf.</p>
<h2>So gibst du einen Eintrag frei</h2>
<ol class="steps-how">
<li>Die erste Person prüft den Beleg gegen die Originalarbeit, trägt die genaue Fundstelle nach und setzt sich in <code>extracted_by</code> ein.</li>
<li>Die zweite Person prüft Fundstelle, Richtung und Grenzen, setzt sich in <code>reviewed_by</code> ein und stellt den Status auf <code>freigegeben</code>.</li>
<li>Beide Schritte folgen danach für die Einstufung. Sie nennt zusätzlich die Art der Absicherung.</li>
<li>Die Änderung geht als Pull Request ins Repository. Die automatische Prüfung meldet fehlende Angaben.</li>
</ol>
{groups}"""
    return page("Offene Prüfungen", body, ctx, current="pruefen",
                description="Belege und Einstufungen, die auf die Zweitprüfung warten.")


def render_history(state: dict, ctx: dict) -> str:
    rows = ""
    for event in reversed(state["history"]):
        goal = ctx["goals"][event["goal_ids"][0]]
        stand = " · ".join((f"{v['display']} erreicht (Katalog v{v['catalog_version']})" if v["catalog_version"] else v["display"])
                           for v in event["stand"].values())
        if event["type"] == "katalog":
            title = f'<a href="ziele/{e(goal["id"])}.html">{e(goal["title"])}</a>'
            added = ", ".join(ctx["milestones"][m][1]["title"] for m in event["added"])
            change = f"{event['subject']}" + (f": {added} aufgenommen" if added else "")
            if event["removed"]:
                change += "; entfernt: " + ", ".join(event["removed"])
            sources = ""
        else:
            subject = event["subject"]
            if subject in ctx["milestones"]:
                owner, ms = ctx["milestones"][subject]
                title = f'<a href="ziele/{e(owner["id"])}.html#{e(subject)}">{e(ms["title"])}</a>'
            else:
                title = f'<a href="aussagen/{e(subject)}.html">{e(ctx["claims"][subject]["statement"])}</a>'
            before = " / ".join(label(o) for o in event["old"]) or "keine Einstufung"
            change = f"{before} → {label(event['new'])}"
            sources = "".join(
                f'<p class="small"><a href="{e(s["url"])}" rel="noopener">{e(s["study"])}</a>, {e(s["locator"])}'
                + (f' <span class="muted">(veröffentlicht {e(s["published"])})</span>' if s.get("published") else "") + "</p>"
                for s in event["sources"])
        rows += f"""<li><time datetime="{e(event['date'])}">{e(event['date'])}</time>
<div><h3>{title}</h3>
<p class="change">{e(change)}</p>
<p>{e(event['reason'])}</p>{sources}
<p class="small muted">Stand danach: {e(stand)}</p></div></li>"""
    if not rows:
        rows = "<li>Noch keine Einträge.</li>"
    series = state["series"]
    curve = chart(series) or ('<p class="scope">Die Kurve erscheint, sobald der Verlauf zwei Tage umfasst. '
                              'Bisher gibt es einen Stand.</p>' if series else "")
    body = f"""<h1>Verlauf</h1>
<p class="lead">Jede Änderung mit dem Datum der Atlasentscheidung, altem und neuem Stand, Grund und Quelle.
Vorschläge erscheinen hier erst nach ihrer Freigabe.</p>
<h2>Erreichte Meilensteine über die Zeit</h2>
{curve}
{series_table(series) if series else ""}
<h2>Änderungen</h2>
<ol class="timeline">{rows}</ol>"""
    return page("Verlauf", body, ctx, current="verlauf", description="Datierte Änderungen am Stand des Atlas.")


# --------------------------------------------------------------------------
# Ausgabe
# --------------------------------------------------------------------------


def build_queue(state: dict, ctx: dict) -> list[dict]:
    queue = []
    edit = f"{ctx['repo']}/edit/{ctx['branch']}/data"
    for claim in state["claims"]:
        for ev in claim["evidence"]:
            if ev["review_status"] != "freigegeben":
                queue.append({"goal_id": claim["goal_ids"][0], "kind": "Beleg", "id": ev["id"],
                              "title": f"{ev['study']['short_label']}, {ev['locator']}",
                              "text": claim["statement"],
                              "href": f"aussagen/{claim['id']}.html#{ev['id']}",
                              "edit": f"{edit}/evidence/{ev['id']}.yaml"})
    for goal in state["goals"]:
        for ms in goal["milestones"]:
            for prop in ms["open_proposals"]:
                queue.append({"goal_id": goal["id"], "kind": "Einstufung eines Meilensteins", "id": prop["id"],
                              "title": f"{ms['title']}: {label(prop['outcome'])}", "text": prop["rationale"],
                              "href": f"ziele/{goal['id']}.html#{ms['id']}",
                              "edit": f"{edit}/decisions/{prop['id']}.yaml"})
    for claim in state["claims"]:
        for prop in claim["open_proposals"]:
            queue.append({"goal_id": claim["goal_ids"][0], "kind": "Einstufung einer Aussage", "id": prop["id"],
                          "title": f"{label(prop['outcome'], claim['field'])}: {claim['statement']}",
                          "text": prop["rationale"], "href": f"aussagen/{claim['id']}.html",
                          "edit": f"{edit}/decisions/{prop['id']}.yaml"})
    return queue


def write_site(state: dict, config: dict, out: Path) -> list[Path]:
    PROFILES.clear()
    PROFILES.update(config.get("fields") or {})
    ctx = {
        "config": config, "repo": config["repo_url"], "branch": config.get("branch", "main"),
        "goals": {g["id"]: g for g in state["goals"]},
        "claims": {c["id"]: c for c in state["claims"]},
        "milestones": {ms["id"]: (g, ms) for g in state["goals"] for ms in g["milestones"]},
        "areas": {a["code"]: a | {"slug": slug(a["name"]), "realm": r["name"]}
                  for r in state["realms"] for a in r["areas"]},
        "taxonomy": state.get("taxonomy", {}),
        "queue": [],
    }
    ctx["queue"] = build_queue(state, ctx)
    files = {
        "index.html": render_index(state, ctx),
        "ziele.html": render_goals(state, ctx),
        "pruefen.html": render_queue(ctx),
        "verlauf.html": render_history(state, ctx),
        "progress.json": json.dumps({k: state[k] for k in ("as_of", "totals", "coverage", "realms", "fields",
                                                           "series", "goals", "claims")},
                                    ensure_ascii=False, indent=2) + "\n",
        "history.json": json.dumps(state["history"], ensure_ascii=False, indent=2) + "\n",
    }
    reached = state["totals"]["milestones"]
    files["badge.svg"] = badge_svg("Meilensteine", f"{reached['reached']}/{reached['total']}")
    for entry in state["fields"]:
        files[f"badge-{slug(entry['field'])}.svg"] = badge_svg(
            entry["field"], f"{entry['milestones']['reached']}/{entry['milestones']['total']}")
    for realm in state["realms"]:
        for area in realm["areas"]:
            if area["goal_ids"]:
                files[f"fach/{slug(area['name'])}.html"] = render_area(realm, area, state, ctx)
    for goal in state["goals"]:
        files[f"ziele/{goal['id']}.html"] = render_goal(goal, ctx)
    for claim in state["claims"]:
        files[f"aussagen/{claim['id']}.html"] = render_claim(claim, ctx)
    written = []
    for name, content in files.items():
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        written.append(target)
    for asset in ("atlas.css", "atlas.js"):
        shutil.copyfile(ASSETS / asset, out / asset)
        written.append(out / asset)
    return written
