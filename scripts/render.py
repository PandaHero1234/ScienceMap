"""Erzeugt aus dem berechneten Stand die statische Übersicht und die JSON-Dateien.

Gestaltung und Bedienhilfen liegen in site/atlas.css und site/atlas.js. Alle
Inhalte stehen im HTML und sind ohne JavaScript lesbar.
"""

from __future__ import annotations

import json
import re
import shutil
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
}
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
    if milestone["status"] == "erreicht":
        return "reached"
    if milestone["status"] == "nicht_erreicht":
        return "failed"
    if milestone["open_proposals"]:
        return "proposed" if milestone["open_proposals"][-1]["outcome"] == "erreicht" else "proposed-failed"
    return "open"


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


def legend() -> str:
    items = "".join(f'<li class="is-{state}">{node(state)}{e(text)}</li>' for state, (text, _) in STATIONS.items())
    return f'<ul class="legend" aria-label="Legende der Stationen">{items}</ul>'


# --------------------------------------------------------------------------
# Seiten
# --------------------------------------------------------------------------


def render_index(state: dict, ctx: dict) -> str:
    goals = state["goals"]
    fields = sorted({g["field"] for g in goals})
    total = sum(g["milestones_total"] or 0 for g in goals)
    reached = sum(g["milestones_reached"] or 0 for g in goals)
    proposed = sum(g["milestones_proposed"] for g in goals)
    summary = f"""<ul class="summary">
<li><b>{len(goals)}</b><span>{'Forschungsziel' if len(goals) == 1 else 'Forschungsziele'} in {plural(len(fields), 'Fach', 'Fächern')}</span></li>
<li><b>{reached} von {total}</b><span>Meilensteinen erreicht</span></li>
<li><b>{proposed}</b><span>vorgeschlagen, Zweitprüfung offen</span></li>
<li><b>{len(ctx['queue'])}</b><span><a href="pruefen.html">offene Prüfungen</a></span></li>
</ul>"""
    pills = '<button class="pill" type="button" data-field="" aria-pressed="true">Alle Fächer</button>' + "".join(
        f'<button class="pill" type="button" data-field="{e(f)}" aria-pressed="false">{e(f)}</button>' for f in fields)
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
<h3><a href="ziele/{e(goal['id'])}.html">{e(goal['title'])}</a></h3>
<p class="goal-count">{count_text(goal)}</p>
{nxt}
</div>
{route(goal, "")}
</li>"""
        sections += (f'<section class="field" id="fach-{slug(field)}" data-field="{e(field)}">'
                     f'<h2>{e(field)} <small>{plural(len(mine), "Ziel", "Ziele")}</small></h2>'
                     f'<ul class="goals">{rows}</ul></section>')
    body = f"""<h1>{e(ctx['config']['title'])}</h1>
<p class="lead">Für jedes Forschungsziel zeigt der Atlas, welche Meilensteine erreicht sind, welche
Veröffentlichungen das tragen und welche Prüfung als Nächstes ansteht.</p>
{summary}
<h2>So liest du eine Route</h2>
<p class="scope">Jedes Ziel ist eine Route aus Meilensteinen. Als erreicht gilt eine Station erst, wenn zwei Personen
die Einstufung freigegeben haben. Bis dahin bleibt sie ein Vorschlag.</p>
{legend()}
<div class="filters" id="filter" role="search" hidden>
<div class="search">{icon("search")}<label class="sr" for="suche">Ziele, Aussagen und Quellen durchsuchen</label>
<input type="search" id="suche" placeholder="Ziele, Aussagen und Quellen durchsuchen" autocomplete="off"></div>
<div class="pills" role="group" aria-label="Nach Fach filtern">{pills}</div>
</div>
<p class="result" id="treffer" role="status" aria-live="polite"></p>
{sections}
<div class="empty" id="leer" hidden><p>Kein Ziel passt zu dieser Suche.</p>
<button class="btn ghost s" type="button" id="zuruecksetzen">Suche zurücksetzen</button></div>
<p class="small muted" style="margin-top:2rem">Die Zählung bezieht sich auf den jeweiligen Zielkatalog. Aus einem Zählerstand
lässt sich keine Aussage zum gesamten Forschungsstand eines Fachs ableiten.</p>"""
    return page("Übersicht", body, ctx, current="index",
                description="Forschungsziele, erreichte Meilensteine und die Veröffentlichungen, die sie tragen.")


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
    body = f"""<ol class="crumbs"><li><a href="../index.html">Übersicht</a></li>
<li><a href="../index.html#fach-{slug(goal['field'])}">{e(goal['field'])}</a></li></ol>
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
    body = f"""<ol class="crumbs"><li><a href="../index.html">Übersicht</a></li>
<li><a href="../index.html#fach-{slug(field)}">{e(field)}</a></li>
<li><a href="../ziele/{e(goal['id'])}.html">{e(goal['title'])}</a></li></ol>
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
    body = f"""<h1>Verlauf</h1>
<p class="lead">Jede Änderung mit dem Datum der Atlasentscheidung, altem und neuem Stand, Grund und Quelle.
Vorschläge erscheinen hier erst nach ihrer Freigabe.</p>
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
        "queue": [],
    }
    ctx["queue"] = build_queue(state, ctx)
    files = {
        "index.html": render_index(state, ctx),
        "pruefen.html": render_queue(ctx),
        "verlauf.html": render_history(state, ctx),
        "progress.json": json.dumps({k: state[k] for k in ("as_of", "goals", "claims")},
                                    ensure_ascii=False, indent=2) + "\n",
        "history.json": json.dumps(state["history"], ensure_ascii=False, indent=2) + "\n",
    }
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
