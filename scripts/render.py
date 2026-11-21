"""Erzeugt aus dem berechneten Stand die statische Übersicht und die JSON-Dateien."""

from __future__ import annotations

import json
from html import escape as e
from pathlib import Path
from urllib.parse import quote

LABELS = {
    # Meilensteine
    "erreicht": "erreicht",
    "nicht_erreicht": "nicht erreicht",
    "offen": "offen",
    # Evidenzlage
    "vorlaeufig_gestuetzt": "vorläufig gestützt",
    "mehrfach_gestuetzt": "mehrfach gestützt",
    "widerspruechlich": "widersprüchlich",
    "spricht_dagegen": "Evidenz spricht dagegen",
    # Redaktioneller Stand
    "vorgeschlagen": "vorgeschlagen",
    "in_pruefung": "in Prüfung",
    "freigegeben": "freigegeben",
    "erneut_zu_pruefen": "erneut zu prüfen",
    # Beziehung Beleg -> Aussage
    "stuetzt": "stützt",
    "nicht_entscheidend": "nicht entscheidend",
    # Art der Absicherung
    "quellenabgleich": "Quellenabgleich",
    "nachrechnung": "Nachrechnung",
    "neue_daten": "neue Daten",
    "anderes_team": "anderes Team",
    "anderes_instrument": "anderes Instrument",
    "beweisreview": "fachliches Beweisreview",
}
RELATION_LABELS = {"spricht_dagegen": "spricht dagegen"}

CSS = """
:root { --bg:#fbfaf7; --fg:#1d1d1b; --muted:#66645e; --line:#dcd9d0; --card:#ffffff;
        --accent:#1f6f5c; --warn:#a15c00; --bad:#a3312b; --track:#e7e4da; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#161715; --fg:#ecebe6; --muted:#a3a199; --line:#34352f; --card:#1f201d;
          --accent:#6cc5ad; --warn:#e0a458; --bad:#ef8a84; --track:#2c2d28; } }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--fg);
       font: 16px/1.55 system-ui, -apple-system, "Segoe UI", sans-serif; }
main, header.site { max-width: 62rem; margin: 0 auto; padding: 0 1rem; }
header.site { padding-top: 1.25rem; display:flex; gap:1.25rem; align-items:baseline; flex-wrap:wrap; }
header.site a { color:var(--muted); text-decoration:none; }
header.site a.home { color:var(--fg); font-weight:700; }
h1 { font-size:1.6rem; line-height:1.25; margin:1.5rem 0 .5rem; text-wrap:balance; }
h2 { font-size:1.15rem; margin:2rem 0 .75rem; }
p.lead { color:var(--muted); max-width:46rem; }
a { color:var(--accent); }
.tablewrap { overflow-x:auto; }
table { border-collapse:collapse; width:100%; font-size:.95rem; }
th, td { text-align:left; vertical-align:top; padding:.6rem .75rem .6rem 0; border-bottom:1px solid var(--line); }
th { color:var(--muted); font-weight:600; font-size:.8rem; text-transform:uppercase; letter-spacing:.04em; }
.bar { height:.5rem; background:var(--track); border-radius:1rem; overflow:hidden; min-width:7rem; margin-top:.3rem; }
.bar span { display:block; height:100%; background:var(--accent); }
.num { font-variant-numeric: tabular-nums; white-space:nowrap; font-weight:600; }
.sub { color:var(--muted); font-size:.85rem; }
.card { background:var(--card); border:1px solid var(--line); border-radius:.6rem; padding:1rem 1.1rem; margin:.75rem 0; }
.card h3 { margin:0 0 .35rem; font-size:1.05rem; }
.badge { display:inline-block; font-size:.8rem; font-weight:600; padding:.1rem .55rem; border-radius:1rem;
         border:1px solid var(--line); color:var(--muted); white-space:nowrap; }
.badge.good { color:var(--accent); border-color:var(--accent); }
.badge.warn { color:var(--warn); border-color:var(--warn); }
.badge.bad { color:var(--bad); border-color:var(--bad); }
dl { display:grid; grid-template-columns:minmax(9rem, max-content) 1fr; gap:.3rem 1rem; margin:.6rem 0 0; }
dt { color:var(--muted); }
dd { margin:0; overflow-wrap:anywhere; }
.facts { display:grid; grid-template-columns:repeat(auto-fit, minmax(13rem, 1fr)); gap:.75rem; }
.facts .card { margin:0; }
.facts .k { color:var(--muted); font-size:.8rem; text-transform:uppercase; letter-spacing:.04em; }
.notice { border-left:3px solid var(--warn); padding:.2rem 0 .2rem .8rem; margin:.6rem 0; }
.button { display:inline-block; margin-top:1rem; padding:.5rem .9rem; border-radius:.5rem;
          background:var(--accent); color:var(--bg); text-decoration:none; font-weight:600; }
footer { color:var(--muted); font-size:.85rem; margin:3rem 0 2rem; }
@media (max-width: 34rem) { dl { grid-template-columns:1fr; } dt { margin-top:.4rem; } }
"""


def label(value: str | None) -> str:
    return LABELS.get(value, value or "offen")


def badge(value: str) -> str:
    tone = {"erreicht": "good", "freigegeben": "good", "vorlaeufig_gestuetzt": "good",
            "mehrfach_gestuetzt": "good", "stuetzt": "good",
            "erneut_zu_pruefen": "warn", "widerspruechlich": "warn", "in_pruefung": "warn",
            "nicht_erreicht": "bad", "spricht_dagegen": "bad"}.get(value, "")
    return f'<span class="badge {tone}">{e(label(value))}</span>'


def number(value) -> str:
    if isinstance(value, float):
        return str(value).replace(".", ",")
    return str(value)


def page(title: str, body: str, config: dict, depth: int = 0) -> str:
    up = "../" * depth
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} · {e(config['title'])}</title>
<link rel="stylesheet" href="{up}style.css">
</head>
<body>
<header class="site">
<a class="home" href="{up}index.html">{e(config['title'])}</a>
<a href="{up}verlauf.html">Verlauf</a>
<a href="{up}progress.json">Daten (JSON)</a>
<a href="{e(config['repo_url'])}">Quelltext und Methodik</a>
</header>
<main>
{body}
<footer>Erzeugt aus den versionierten Daten im Repository. Jede Zahl lässt sich über die
verlinkten Entscheidungen und Belege bis zur Fundstelle zurückverfolgen.</footer>
</main>
</body>
</html>
"""


def bar(goal: dict) -> str:
    if goal["milestones_total"] is None:
        return '<span class="num">Katalog offen</span>'
    total = goal["milestones_total"]
    share = 100 * goal["milestones_reached"] / total if total else 0
    return (f'<span class="num">{goal["milestones_reached"]} von {total} Meilensteinen erreicht</span>'
            f'<div class="sub">Zielkatalog v{goal["catalog_version"]}</div>'
            f'<div class="bar" role="img" aria-label="{e(goal["display"])} Meilensteinen erreicht">'
            f'<span style="width:{share:.0f}%"></span></div>')


def notices(item: dict) -> str:
    out = ""
    if item.get("conflict"):
        out += ('<p class="notice">Zu diesem Eintrag liegen widersprechende Entscheidungen vor ('
                + e(", ".join(item["conflict"])) + "). Bis zur fachlichen Klärung gilt der Stand davor.</p>")
    for reason in item.get("reexamine", []):
        out += f'<p class="notice">Erneut zu prüfen: {e(reason)}</p>'
    return out


def decision_block(dec: dict | None, heading: str = "Gültige Entscheidung") -> str:
    if not dec:
        return ""
    rows = [("Entscheidung", f"{e(dec['id'])} vom {e(dec['date'])}"),
            ("Ergebnis", badge(dec["outcome"])),
            ("Begründung", e(dec["rationale"]))]
    if dec.get("dissent"):
        rows.append(("Abweichende Einschätzung", e(dec["dissent"])))
    if dec.get("assurance"):
        rows.append(("Art der Absicherung", e(", ".join(label(a) for a in dec["assurance"]))))
    people = [p for p in (dec.get("extracted_by"), dec.get("reviewed_by")) if p]
    if people:
        rows.append(("Geprüft von", e(" und ".join(people))))
    if dec.get("evidence_ids"):
        rows.append(("Belege", e(", ".join(dec["evidence_ids"]))))
    body = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows)
    return f"<h2>{e(heading)}</h2><div class=\"card\"><dl>{body}</dl></div>"


def render_index(state: dict, config: dict) -> str:
    rows = ""
    for goal in state["goals"]:
        rows += f"""<tr>
<td>{e(goal['field'])}</td>
<td><a href="ziele/{e(goal['id'])}.html">{e(goal['title'])}</a></td>
<td>{bar(goal)}<div class="sub">{goal['claims_reviewed']} von {goal['claims_total']} erfassten Aussagen geprüft</div></td>
<td>{e(goal['last_change'] or 'offen')}<div class="sub">{e(goal.get('last_work') or '')}</div></td>
<td>{e(goal.get('open_question') or 'offen')}</td>
</tr>"""
    body = f"""<h1>{e(config['title'])}</h1>
<p class="lead">Für jedes Forschungsziel: welche Meilensteine erreicht sind, welche Veröffentlichungen
diese Einschätzung tragen und welche Prüfung als Nächstes ansteht.</p>
<div class="tablewrap"><table>
<thead><tr><th>Fach</th><th>Forschungsziel</th><th>Fortschritt</th><th>Letzte Änderung</th><th>Nächste offene Prüfung</th></tr></thead>
<tbody>{rows}</tbody>
</table></div>
<p class="sub">Die Anzeige bezieht sich auf die Arbeit am jeweiligen Zielkatalog. Aus einem Zählerstand
lässt sich keine Aussage zum gesamten Forschungsstand eines Fachs ableiten.</p>"""
    return page("Übersicht", body, config)


def render_goal(goal: dict, config: dict) -> str:
    cards = ""
    for ms in goal["milestones"]:
        claims = ", ".join(f'<a href="../aussagen/{e(c)}.html">{e(c)}</a>' for c in ms["claims"]) or "noch keine"
        dec = ms["decision"]
        reason = (f"<dt>Begründung</dt><dd>{e(dec['rationale'])} "
                  f"<span class=\"sub\">({e(dec['id'])}, {e(dec['date'])})</span></dd>") if dec else ""
        note = f"<dt>Stand</dt><dd>{e(ms['note'])}</dd>" if ms.get("note") and not dec else ""
        cards += f"""<div class="card" id="{e(ms['id'])}">
<h3>{e(ms['title'])} {badge(ms['status'])}</h3>
{notices(ms)}
<dl><dt>Erfüllungskriterium</dt><dd>{e(ms['criterion'])}</dd>
{note}{reason}
<dt>Verknüpfte Aussagen</dt><dd>{claims}</dd>
<dt>Meilenstein-ID</dt><dd>{e(ms['id'])}</dd></dl>
</div>"""
    if not goal["milestones"]:
        cards = '<p class="notice">Für dieses Ziel sind noch keine Meilensteine definiert.</p>'
    body = f"""<p class="sub">{e(goal['field'])}</p>
<h1>{e(goal['title'])}</h1>
<p>{bar(goal)}</p>
<p class="sub">{goal['claims_reviewed']} von {goal['claims_total']} erfassten Aussagen geprüft.
Nächste offene Prüfung: {e(goal.get('open_question') or 'offen')}</p>
<h2>Meilensteine</h2>
{cards}"""
    return page(goal["title"], body, config, depth=1)


def render_claim(claim: dict, config: dict) -> str:
    assurance = ", ".join(label(a) for a in claim["assurance"]) or "noch keine"
    facts = f"""<div class="facts">
<div class="card"><div class="k">Redaktioneller Stand</div>{badge(claim['editorial_status'])}</div>
<div class="card"><div class="k">Evidenzlage zur Aussage</div>{badge(claim['evidence_status'])}</div>
<div class="card"><div class="k">Art der Absicherung</div>{e(assurance)}</div>
</div>"""
    counts = (f"{claim['supporting_sources']} stützende Quelle(n), "
              f"{claim['supporting_observations']} zugrunde liegende Beobachtung(en).")
    if claim["shared_dependencies"]:
        counts += " Gemeinsame Abhängigkeiten: " + ", ".join(claim["shared_dependencies"]) + "."
    cards = ""
    for ev in claim["evidence"]:
        study = ev["study"]
        values = ", ".join(f"{k}: {number(v)}" for k, v in ev["values"].items())
        rows = [("Quelle", f"{e(study['label'])} ({e(study['version'])})"),
                ("Fundstelle", f"{e(ev['locator'])} · <a href=\"{e(study['url'])}\">Original öffnen</a>"),
                ("Messgröße", e(ev["metric"])),
                ("Ergebnis", e(values)),
                ("Unsicherheit", e(ev["uncertainty"]))]
        if ev.get("conditions"):
            rows.append(("Bedingungen", e(ev["conditions"])))
        rows.append(("Beobachtung", e(", ".join(ev["observations"]))))
        if study["status"] != "aktiv":
            rows.append(("Status der Studie", e(f"{study['status']} am {study.get('status_date')}: {study.get('status_note')}")))
        people = [p for p in (ev.get("extracted_by"), ev.get("reviewed_by")) if p]
        rows.append(("Prüfvermerk", badge(ev["review_status"]) + (" " + e(" und ".join(people)) if people else "")))
        if ev.get("note"):
            rows.append(("Anmerkung", e(ev["note"])))
        body = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows)
        relation = RELATION_LABELS.get(ev["relation"], label(ev["relation"]))
        tone = {"stuetzt": "good", "spricht_dagegen": "bad"}.get(ev["relation"], "")
        cards += (f'<div class="card" id="{e(ev["id"])}"><h3>{e(ev["id"])} '
                  f'<span class="badge {tone}">{e(relation)}</span></h3><dl>{body}</dl></div>')
    if not cards:
        cards = '<p class="notice">Zu dieser Aussage ist noch kein Beleg erfasst.</p>'
    earlier = "".join(decision_block(d, "Frühere Entscheidung") for d in reversed(claim["earlier_decisions"]))
    proposals = "".join(decision_block(d, "Offener Vorschlag") for d in claim["open_proposals"])
    issue = (f"{config['repo_url']}/issues/new?template=einwand.md&title="
             + quote(f"Einwand zu {claim['id']}"))
    milestones = ", ".join(e(m) for m in claim["milestone_ids"])
    body = f"""<p class="sub">Aussage · {e(claim['id'])}</p>
<h1>{e(claim['statement'])}</h1>
<dl><dt>Geltungsbereich</dt><dd>{e(claim['scope'])}</dd>
<dt>Meilensteine</dt><dd>{milestones}</dd></dl>
{notices(claim)}
<h2>Einordnung</h2>
{facts}
<p class="sub">{e(counts)}</p>
{decision_block(claim['decision'])}
{proposals}
<h2>Belege</h2>
{cards}
{earlier}
<a class="button" href="{e(issue)}">Einwand oder Korrektur einreichen</a>"""
    return page(claim["id"], body, config, depth=1)


def render_history(state: dict, config: dict) -> str:
    rows = ""
    for event in reversed(state["history"]):
        if event["type"] == "katalog":
            change = "Neue Katalogversion"
            if event["added"]:
                change += ": " + ", ".join(event["added"]) + " aufgenommen"
            if event["removed"]:
                change += "; " + ", ".join(event["removed"]) + " entfernt"
            sources = ""
        else:
            before = " / ".join(label(o) for o in event["old"]) or "keine Entscheidung"
            change = f"{before} → {label(event['new'])}"
            sources = "<br>".join(
                f'<a href="{e(s["url"])}">{e(s["study"])}</a>, {e(s["locator"])}'
                + (f' <span class="sub">(veröffentlicht {e(s["published"])})</span>' if s.get("published") else "")
                for s in event["sources"])
        stand = "<br>".join(f"{e(v['display'])} · v{v['catalog_version']}" if v["catalog_version"] else e(v["display"])
                            for v in event["stand"].values())
        rows += f"""<tr><td class="num">{e(event['date'])}</td><td>{e(event['subject'])}</td>
<td>{e(change)}</td><td>{e(event['reason'])}</td><td>{sources}</td><td class="num">{stand}</td></tr>"""
    if not rows:
        rows = '<tr><td colspan="6">Noch keine Einträge.</td></tr>'
    body = f"""<h1>Verlauf</h1>
<p class="lead">Jede Änderung mit Datum der Atlasentscheidung, altem und neuem Stand, Grund und Quelle.
Die letzte Spalte zeigt den Zählerstand des Ziels nach der Änderung.</p>
<div class="tablewrap"><table>
<thead><tr><th>Datum</th><th>Gegenstand</th><th>Änderung</th><th>Grund</th><th>Quelle</th><th>Stand danach</th></tr></thead>
<tbody>{rows}</tbody></table></div>"""
    return page("Verlauf", body, config)


def write_site(state: dict, config: dict, out: Path) -> list[Path]:
    files = {
        "style.css": CSS.strip() + "\n",
        "index.html": render_index(state, config),
        "verlauf.html": render_history(state, config),
        "progress.json": json.dumps({k: state[k] for k in ("as_of", "goals", "claims")},
                                    ensure_ascii=False, indent=2) + "\n",
        "history.json": json.dumps(state["history"], ensure_ascii=False, indent=2) + "\n",
    }
    for goal in state["goals"]:
        files[f"ziele/{goal['id']}.html"] = render_goal(goal, config)
    for claim in state["claims"]:
        files[f"aussagen/{claim['id']}.html"] = render_claim(claim, config)
    written = []
    for name, content in files.items():
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        written.append(target)
    return written
