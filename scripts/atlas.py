#!/usr/bin/env python3
"""Forschungsatlas: Daten prüfen und die öffentliche Übersicht erzeugen.

    python scripts/atlas.py validate
    python scripts/atlas.py build --out public

Die Regeln stehen in docs/01 bis docs/03. Welche Regel wo geprüft wird,
steht in docs/06-nachweis.md.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent

# Ordner unter data/ -> Name des Schemas
FOLDERS = {
    "goals": "goal",
    "claims": "claim",
    "studies": "study",
    "datasets": "dataset",
    "evidence": "evidence",
    "decisions": "decision",
}

MILESTONE_OUTCOMES = {"erreicht", "nicht_erreicht"}
CLAIM_OUTCOMES = {
    "offen",
    "vorlaeufig_gestuetzt",
    "mehrfach_gestuetzt",
    "widerspruechlich",
    "spricht_dagegen",
}


@dataclass
class Atlas:
    goals: dict = field(default_factory=dict)
    claims: dict = field(default_factory=dict)
    studies: dict = field(default_factory=dict)
    datasets: dict = field(default_factory=dict)
    evidence: dict = field(default_factory=dict)
    decisions: dict = field(default_factory=dict)

    def milestone_goal(self) -> dict:
        """Meilenstein-ID -> Ziel-ID."""
        return {m["id"]: g["id"] for g in self.goals.values() for m in g.get("milestones", [])}


# --------------------------------------------------------------------------
# Laden und Schema-Prüfung
# --------------------------------------------------------------------------


def _plain(value):
    """YAML liest 2026-11-21 als Datum. Für Schema und JSON brauchen wir Text."""
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()[:10]
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_plain(v) for v in value]
    return value


def load(data_dir: Path, schema_dir: Path | None = None) -> tuple[Atlas, list[str]]:
    """Liest alle YAML-Dateien und prüft sie gegen die JSON-Schemas."""
    schema_dir = schema_dir or ROOT / "schemas"
    atlas, errors = Atlas(), []
    for folder, kind in FOLDERS.items():
        schema = json.loads((schema_dir / f"{kind}.schema.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        store = getattr(atlas, folder)
        for path in sorted((data_dir / folder).glob("*.yaml")):
            name = f"{folder}/{path.name}"
            try:
                record = _plain(yaml.safe_load(path.read_text(encoding="utf-8")))
            except yaml.YAMLError as exc:
                errors.append(f"{name}: kein gültiges YAML ({exc})")
                continue
            if not isinstance(record, dict):
                errors.append(f"{name}: die Datei muss ein Objekt mit Feldern enthalten")
                continue
            problems = sorted(validator.iter_errors(record), key=lambda e: list(e.path))
            for problem in problems:
                where = "/".join(str(p) for p in problem.path) or "(Datei)"
                errors.append(f"{name}: {where}: {problem.message}")
            if problems:
                continue
            if record["id"] != path.stem:
                errors.append(f"{name}: die ID '{record['id']}' muss dem Dateinamen entsprechen")
                continue
            store[record["id"]] = record
    return atlas, errors


# --------------------------------------------------------------------------
# Fachliche Prüfungen über Dateigrenzen hinweg
# --------------------------------------------------------------------------


def _root_dataset(atlas: Atlas, dataset_id: str) -> str:
    """Ausschnitte desselben Rohlogs verweisen auf dieselbe Herkunft."""
    seen = set()
    while dataset_id in atlas.datasets and dataset_id not in seen:
        seen.add(dataset_id)
        parent = atlas.datasets[dataset_id].get("derived_from")
        if not parent:
            break
        dataset_id = parent
    return dataset_id


def observations(atlas: Atlas, evidence: dict) -> set[str]:
    """Die Beobachtungen, auf denen ein Beleg beruht (Datensatz und Ereignisse)."""
    ids = list(evidence.get("event_ids", []))
    if evidence.get("dataset_id"):
        ids.append(evidence["dataset_id"])
    return {_root_dataset(atlas, i) for i in ids}


def predecessors(decision: dict) -> list[str]:
    """supersedes ist eine ID oder, wenn ein Konflikt geklärt wird, eine Liste von IDs."""
    value = decision.get("supersedes", [])
    return [value] if isinstance(value, str) else list(value)


def _ancestors(decisions: dict, decision_id: str) -> set[str]:
    seen: set[str] = set()
    stack = predecessors(decisions.get(decision_id, {}))
    while stack:
        current = stack.pop()
        if current in seen or current not in decisions:
            continue
        seen.add(current)
        stack.extend(predecessors(decisions[current]))
    return seen


def _two_people(record: dict) -> bool:
    a = record.get("extracted_by", "").strip().casefold()
    b = record.get("reviewed_by", "").strip().casefold()
    return bool(a) and bool(b) and a != b


def check(atlas: Atlas) -> list[str]:
    """Prüft Verweise, Zählbarkeit und die Regeln für freigegebene Entscheidungen."""
    errors: list[str] = []
    err = errors.append

    # Ziele und Kataloge
    owner: dict[str, str] = {}
    for goal in atlas.goals.values():
        defined = [m["id"] for m in goal.get("milestones", [])]
        for mid in defined:
            if mid in owner:
                err(f"{goal['id']}: Meilenstein {mid} ist bereits in {owner[mid]} definiert")
            owner[mid] = goal["id"]
        catalog = goal.get("catalog", [])
        if defined and not catalog:
            err(f"{goal['id']}: Meilensteine sind definiert, aber es gibt keine Katalogversion")
        for previous, entry in zip([None] + catalog, catalog):
            for mid in entry["milestones"]:
                if mid not in defined:
                    err(f"{goal['id']}: Katalog v{entry['version']} nennt unbekannten Meilenstein {mid}")
            if previous and entry["version"] <= previous["version"]:
                err(f"{goal['id']}: Katalogversionen müssen aufsteigend sein (v{entry['version']})")
            if previous and entry["date"] < previous["date"]:
                err(f"{goal['id']}: Katalog v{entry['version']} ist älter als sein Vorgänger")

    # Datensätze
    for dataset in atlas.datasets.values():
        parent = dataset.get("derived_from")
        if parent and parent not in atlas.datasets:
            err(f"{dataset['id']}: derived_from verweist auf unbekannten Datensatz {parent}")
        chain, current = set(), dataset["id"]
        while current in atlas.datasets and atlas.datasets[current].get("derived_from"):
            if current in chain:
                err(f"{dataset['id']}: derived_from bildet einen Kreis")
                break
            chain.add(current)
            current = atlas.datasets[current]["derived_from"]

    # Aussagen
    for claim in atlas.claims.values():
        for mid in claim["milestone_ids"]:
            if mid not in owner:
                err(f"{claim['id']}: unbekannter Meilenstein {mid}")

    # Belege
    for ev in atlas.evidence.values():
        if ev["claim_id"] not in atlas.claims:
            err(f"{ev['id']}: unbekannte Aussage {ev['claim_id']}")
        study = atlas.studies.get(ev["study_id"])
        if study is None:
            err(f"{ev['id']}: unbekannte Studie {ev['study_id']}")
        elif ev["study_version"] not in {v["id"] for v in study["versions"]}:
            err(f"{ev['id']}: Studie {study['id']} hat keine Fassung {ev['study_version']}")
        for oid in ([ev["dataset_id"]] if ev.get("dataset_id") else []) + ev.get("event_ids", []):
            if oid not in atlas.datasets:
                err(f"{ev['id']}: unbekannter Datensatz oder unbekanntes Ereignis {oid}")
        if ev["review_status"] == "freigegeben" and not _two_people(ev):
            err(f"{ev['id']}: ein freigegebener Beleg braucht extracted_by und reviewed_by von zwei verschiedenen Personen")

    # Entscheidungen
    for dec in atlas.decisions.values():
        did, kind, target = dec["id"], dec["kind"], dec["target_id"]
        released = dec["status"] == "freigegeben"
        if kind == "meilenstein":
            if target not in owner:
                err(f"{did}: unbekannter Meilenstein {target}")
                continue
            if dec["outcome"] not in MILESTONE_OUTCOMES:
                err(f"{did}: für einen Meilenstein ist nur 'erreicht' oder 'nicht_erreicht' möglich")
            goal = atlas.goals[owner[target]]
            versions = {c["version"]: c for c in goal.get("catalog", [])}
            version = dec.get("catalog_version")
            if version is None:
                err(f"{did}: catalog_version fehlt")
            elif version not in versions:
                err(f"{did}: {goal['id']} hat keine Katalogversion {version}")
            elif target not in versions[version]["milestones"]:
                err(f"{did}: {target} gehört nicht zu Katalog v{version}")
            allowed = {e["id"] for e in atlas.evidence.values()
                       if target in atlas.claims.get(e["claim_id"], {}).get("milestone_ids", [])}
        else:
            if target not in atlas.claims:
                err(f"{did}: unbekannte Aussage {target}")
                continue
            if dec["outcome"] not in CLAIM_OUTCOMES:
                err(f"{did}: '{dec['outcome']}' ist keine Evidenzlage für eine Aussage")
            allowed = {e["id"] for e in atlas.evidence.values() if e["claim_id"] == target}

        cited = []
        for eid in dec.get("evidence_ids", []):
            if eid not in atlas.evidence:
                err(f"{did}: unbekannter Beleg {eid}")
            elif eid not in allowed:
                err(f"{did}: Beleg {eid} gehört nicht zu {target}")
            else:
                cited.append(atlas.evidence[eid])

        for pid in predecessors(dec):
            previous = atlas.decisions.get(pid)
            if previous is None:
                err(f"{did}: supersedes verweist auf unbekannte Entscheidung {pid}")
            elif (previous["kind"], previous["target_id"]) != (kind, target):
                err(f"{did}: supersedes verweist auf eine Entscheidung zu einem anderen Gegenstand")
            elif previous["date"] > dec["date"]:
                err(f"{did}: die Entscheidung ist älter als ihr Vorgänger {previous['id']}")
            elif released and previous["status"] != "freigegeben":
                err(f"{did}: der Vorgänger {previous['id']} ist nicht freigegeben")
        if did in _ancestors(atlas.decisions, did):
            err(f"{did}: supersedes bildet einen Kreis")

        if not released:
            continue
        if not _two_people(dec):
            err(f"{did}: eine Freigabe braucht extracted_by und reviewed_by von zwei verschiedenen Personen")
        if not dec.get("evidence_ids"):
            err(f"{did}: eine Freigabe muss ihre Beleg-IDs nennen")
        if not dec.get("assurance"):
            err(f"{did}: eine Freigabe muss die Art der Absicherung nennen")
        for ev in cited:
            if ev["review_status"] != "freigegeben":
                err(f"{did}: Beleg {ev['id']} ist selbst noch nicht freigegeben")
        if kind == "aussage":
            pro = [e for e in cited if e["relation"] == "stuetzt"]
            contra = [e for e in cited if e["relation"] == "spricht_dagegen"]
            outcome = dec["outcome"]
            if outcome in ("vorlaeufig_gestuetzt", "mehrfach_gestuetzt") and not pro:
                err(f"{did}: '{outcome}' braucht mindestens einen stützenden Beleg")
            if outcome == "spricht_dagegen" and not contra:
                err(f"{did}: 'spricht_dagegen' braucht mindestens einen Gegenbeleg")
            if outcome == "widerspruechlich" and not (pro and contra):
                err(f"{did}: 'widerspruechlich' braucht stützende Belege und Gegenbelege")
            if outcome == "mehrfach_gestuetzt":
                seen = set().union(*(observations(atlas, e) for e in pro)) if pro else set()
                if len(seen) < 2:
                    err(f"{did}: 'mehrfach_gestuetzt' braucht mindestens zwei verschiedene Beobachtungen, "
                        f"die Belege beruhen auf {len(seen)} ({', '.join(sorted(seen)) or 'keiner'})")
    return errors


# --------------------------------------------------------------------------
# Auswertung
# --------------------------------------------------------------------------


def resolve(atlas: Atlas, kind: str, target: str, as_of: str | None = None) -> dict:
    """Bestimmt die gültige Entscheidung zu einem Meilenstein oder einer Aussage.

    Gültig ist die letzte eindeutige Freigabe. Gibt es zwei Nachfolger derselben
    Entscheidung oder zwei Erstentscheidungen, bleibt der Stand davor gültig und
    der Konflikt wird gemeldet.
    """
    pool = {d["id"]: d for d in atlas.decisions.values()
            if d["kind"] == kind and d["target_id"] == target and d["status"] == "freigegeben"
            and (as_of is None or d["date"] <= as_of)}
    order = lambda d: (d["date"], d["id"])
    replaced = {p for d in pool.values() for p in predecessors(d)}
    heads = sorted((d for d in pool.values() if d["id"] not in replaced), key=order)
    if not heads:
        return {"valid": None, "conflict": [], "chain": []}
    if len(heads) == 1:
        valid, conflict = heads[0], []
    else:
        # Mehrere offene Enden: gültig bleibt der letzte Stand, auf dem alle aufbauen.
        common = set.intersection(*(_ancestors(pool, h["id"]) for h in heads))
        latest = [c for c in common if not any(c in _ancestors(pool, o) for o in common)]
        valid = max((pool[c] for c in latest), key=order, default=None)
        conflict = [h["id"] for h in heads]
    chain = []
    if valid:
        chain = sorted((pool[a] for a in _ancestors(pool, valid["id"])), key=order) + [valid]
    return {"valid": valid, "conflict": conflict, "chain": chain}


def _reexamine(atlas: Atlas, decision: dict | None, claim_id: str | None = None) -> list[str]:
    """Gründe, aus denen eine gültige Entscheidung erneut zu prüfen ist."""
    if decision is None:
        return []
    reasons = []
    cited = set(decision.get("evidence_ids", []))
    if claim_id:
        for ev in atlas.evidence.values():
            if ev["claim_id"] == claim_id and ev["id"] not in cited:
                reasons.append(f"Beleg {ev['id']} ist in der gültigen Entscheidung nicht berücksichtigt.")
    for eid in sorted(cited):
        study = atlas.studies.get(atlas.evidence.get(eid, {}).get("study_id"))
        if study and study["status"] != "aktiv" and study["status_date"] > decision["date"]:
            word = "korrigiert" if study["status"] == "korrigiert" else "zurückgezogen"
            reasons.append(f"Die Studie {study['id']} wurde am {study['status_date']} {word}.")
    return reasons


def _catalog(goal: dict, as_of: str | None) -> dict | None:
    entries = [c for c in goal.get("catalog", []) if as_of is None or c["date"] <= as_of]
    return entries[-1] if entries else None


def _decision_view(dec: dict | None) -> dict | None:
    if dec is None:
        return None
    keys = ("id", "date", "outcome", "rationale", "dissent", "assurance", "extracted_by",
            "reviewed_by", "evidence_ids", "catalog_version", "supersedes")
    return {k: dec[k] for k in keys if k in dec}


def _evidence_view(atlas: Atlas, ev: dict) -> dict:
    study = atlas.studies[ev["study_id"]]
    version = next(v for v in study["versions"] if v["id"] == ev["study_version"])
    view = {k: ev[k] for k in ("id", "locator", "metric", "values", "uncertainty", "relation",
                               "review_status", "conditions", "dataset_id", "event_ids", "note",
                               "extracted_by", "reviewed_by") if k in ev}
    view["study"] = {"id": study["id"], "label": study["label"], "team": study["team"],
                     "status": study["status"], "version": version["kind"], "url": version["url"]}
    for key in ("doi", "published", "instrument", "status_date", "status_note"):
        if key in study:
            view["study"][key] = study[key]
    view["observations"] = sorted(observations(atlas, ev))
    return view


def claim_state(atlas: Atlas, claim: dict, as_of: str | None = None) -> dict:
    result = resolve(atlas, "aussage", claim["id"], as_of)
    valid = result["valid"]
    evidence = [e for e in atlas.evidence.values() if e["claim_id"] == claim["id"]]
    pro = [e for e in evidence if e["relation"] == "stuetzt"]
    reasons = _reexamine(atlas, valid, claim["id"])
    pending = [d for d in atlas.decisions.values()
               if d["kind"] == "aussage" and d["target_id"] == claim["id"] and d["status"] != "freigegeben"]
    if valid and reasons:
        editorial = "erneut_zu_pruefen"
    elif valid:
        editorial = "freigegeben"
    elif pending or any(e["review_status"] == "in_pruefung" for e in evidence):
        editorial = "in_pruefung"
    else:
        editorial = "vorgeschlagen"
    studies = {e["study_id"] for e in pro}
    shared = []
    if len(studies) > 1:
        for label, key in (("Team", "team"), ("Instrument", "instrument")):
            values = {atlas.studies[s].get(key) for s in studies}
            if len(values) == 1 and None not in values:
                shared.append(f"{label}: {values.pop()}")
    return {
        "id": claim["id"],
        "statement": claim["statement"],
        "scope": claim["scope"],
        "milestone_ids": claim["milestone_ids"],
        "editorial_status": editorial,
        "evidence_status": valid["outcome"] if valid else "offen",
        "assurance": valid.get("assurance", []) if valid else [],
        "supporting_sources": len(studies),
        "supporting_observations": len(set().union(*(observations(atlas, e) for e in pro))) if pro else 0,
        "shared_dependencies": shared,
        "decision": _decision_view(valid),
        "earlier_decisions": [_decision_view(d) for d in result["chain"][:-1]],
        "open_proposals": [_decision_view(d) | {"status": d["status"]} for d in pending],
        "conflict": result["conflict"],
        "reexamine": reasons,
        "evidence": [_evidence_view(atlas, e) for e in sorted(evidence, key=lambda e: e["id"])],
    }


def goal_state(atlas: Atlas, goal: dict, as_of: str | None = None) -> dict:
    catalog = _catalog(goal, as_of)
    definitions = {m["id"]: m for m in goal.get("milestones", [])}
    milestones = []
    for mid in catalog["milestones"] if catalog else []:
        result = resolve(atlas, "meilenstein", mid, as_of)
        valid = result["valid"]
        milestones.append({
            **definitions[mid],
            "status": valid["outcome"] if valid else "offen",
            "decision": _decision_view(valid),
            "earlier_decisions": [_decision_view(d) for d in result["chain"][:-1]],
            "conflict": result["conflict"],
            "reexamine": _reexamine(atlas, valid),
            "claims": sorted(c["id"] for c in atlas.claims.values() if mid in c["milestone_ids"]),
        })
    reached = sum(1 for m in milestones if m["status"] == "erreicht")
    claims = [c for c in atlas.claims.values() if set(c["milestone_ids"]) & set(definitions)]
    reviewed = sum(1 for c in claims if resolve(atlas, "aussage", c["id"], as_of)["valid"])
    display = f"{reached} von {len(milestones)}" if catalog else "Katalog offen"
    return {
        "id": goal["id"],
        "field": goal["field"],
        "title": goal["title"],
        "catalog_version": catalog["version"] if catalog else None,
        "milestones_reached": reached if catalog else None,
        "milestones_total": len(milestones) if catalog else None,
        "display": display,
        "claims_reviewed": reviewed,
        "claims_total": len(claims),
        "last_work": goal.get("last_work"),
        "open_question": goal.get("open_question"),
        "milestones": milestones,
    }


def history(atlas: Atlas) -> list[dict]:
    """Datierte Änderungen: neue Katalogversionen und freigegebene Entscheidungen."""
    owner = atlas.milestone_goal()
    events = []
    for goal in atlas.goals.values():
        previous: list[str] = []
        for entry in goal.get("catalog", []):
            events.append({
                "date": entry["date"], "type": "katalog", "goal_ids": [goal["id"]],
                "subject": f"Zielkatalog v{entry['version']}",
                "reason": entry["reason"],
                "added": [m for m in entry["milestones"] if m not in previous],
                "removed": [m for m in previous if m not in entry["milestones"]],
            })
            previous = entry["milestones"]
    for dec in atlas.decisions.values():
        if dec["status"] != "freigegeben":
            continue
        if dec["kind"] == "meilenstein":
            goal_ids = [owner[dec["target_id"]]]
        else:
            goal_ids = sorted({owner[m] for m in atlas.claims[dec["target_id"]]["milestone_ids"]})
        before = [atlas.decisions[p]["outcome"] for p in predecessors(dec)]
        sources = []
        for eid in dec.get("evidence_ids", []):
            view = _evidence_view(atlas, atlas.evidence[eid])
            sources.append({"evidence_id": eid, "study": view["study"]["label"],
                            "locator": view["locator"], "url": view["study"]["url"],
                            "published": view["study"].get("published")})
        events.append({
            "date": dec["date"], "type": "entscheidung", "goal_ids": goal_ids,
            "decision_id": dec["id"], "kind": dec["kind"], "subject": dec["target_id"],
            "old": before, "new": dec["outcome"],
            "reason": dec["rationale"], "sources": sources,
            "people": [dec.get("extracted_by"), dec.get("reviewed_by")],
        })
    events.sort(key=lambda e: (e["date"], e["type"] != "katalog", e.get("decision_id", "")))
    for event in events:
        event["stand"] = {}
        for gid in event["goal_ids"]:
            state = goal_state(atlas, atlas.goals[gid], as_of=event["date"])
            event["stand"][gid] = {"display": state["display"], "catalog_version": state["catalog_version"]}
    return events


def build_state(atlas: Atlas) -> dict:
    events = history(atlas)
    goals = [goal_state(atlas, g) for g in sorted(atlas.goals.values(), key=lambda g: (g["field"], g["id"]))]
    for goal in goals:
        dates = [e["date"] for e in events if goal["id"] in e["goal_ids"]]
        goal["last_change"] = max(dates) if dates else None
    claims = [claim_state(atlas, c) for c in sorted(atlas.claims.values(), key=lambda c: c["id"])]
    return {
        "as_of": max((e["date"] for e in events), default=None),
        "goals": goals,
        "claims": claims,
        "history": events,
    }


def conflicts(state: dict) -> list[str]:
    notes = []
    for goal in state["goals"]:
        for ms in goal["milestones"]:
            if ms["conflict"]:
                notes.append(f"{ms['id']}: widersprechende Entscheidungen {', '.join(ms['conflict'])}")
    for claim in state["claims"]:
        if claim["conflict"]:
            notes.append(f"{claim['id']}: widersprechende Entscheidungen {', '.join(claim['conflict'])}")
    return notes


# --------------------------------------------------------------------------
# Kommandozeile
# --------------------------------------------------------------------------


def load_checked(data_dir: Path) -> tuple[Atlas, list[str]]:
    atlas, errors = load(data_dir)
    if not errors:
        errors = check(atlas)
    return atlas, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=["validate", "build"])
    parser.add_argument("--data", type=Path, default=ROOT / "data")
    parser.add_argument("--out", type=Path, default=ROOT / "public")
    parser.add_argument("--config", type=Path, default=ROOT / "atlas.yaml")
    args = parser.parse_args(argv)

    atlas, errors = load_checked(args.data)
    if errors:
        for line in errors:
            print(f"FEHLER  {line}", file=sys.stderr)
        print(f"{len(errors)} Fehler. Die Übersicht wird nicht aktualisiert.", file=sys.stderr)
        return 1

    state = build_state(atlas)
    for note in conflicts(state):
        print(f"KONFLIKT  {note}")
    counts = ", ".join(f"{len(getattr(atlas, f))} {f}" for f in FOLDERS)
    print(f"Daten gültig: {counts}.")
    for goal in state["goals"]:
        print(f"  {goal['id']}: {goal['display']} Meilensteinen erreicht, "
              f"{goal['claims_reviewed']} von {goal['claims_total']} Aussagen geprüft")
    if args.command == "build":
        import render

        config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
        written = render.write_site(state, config, args.out)
        print(f"{len(written)} Dateien nach {args.out} geschrieben.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
