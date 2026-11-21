"""Gemeinsame Testhilfen.

Die Tests arbeiten mit erfundenen Daten in einem temporären Ordner. Nur
test_pilotdaten.py liest die echten Daten unter data/.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import atlas  # noqa: E402


class World:
    """Ein kleiner Atlas aus erfundenen Daten, den jeder Test verändern kann."""

    def __init__(self, root: Path):
        self.root = root
        for folder in atlas.FOLDERS:
            (root / folder).mkdir()

    def put(self, folder: str, record: dict) -> dict:
        path = self.root / folder / f"{record['id']}.yaml"
        path.write_text(yaml.safe_dump(record, allow_unicode=True, sort_keys=False), encoding="utf-8")
        return record

    def errors(self) -> list[str]:
        return atlas.load_checked(self.root)[1]

    def state(self) -> dict:
        loaded, errors = atlas.load_checked(self.root)
        assert errors == [], errors
        return atlas.build_state(loaded)

    def goal(self) -> dict:
        return self.state()["goals"][0]

    def claim(self, claim_id: str = "cl-a") -> dict:
        return next(c for c in self.state()["claims"] if c["id"] == claim_id)

    # Bausteine -------------------------------------------------------------

    def study(self, sid: str, team: str = "team-eins", **extra) -> dict:
        return self.put("studies", {
            "id": sid, "label": f"Studie {sid}", "team": team, "status": "aktiv",
            "versions": [{"id": "v1", "kind": "Journalfassung", "url": f"https://example.org/{sid}"}],
            **extra})

    def dataset(self, did: str, **extra) -> dict:
        return self.put("datasets", {"id": did, "title": did, "source": "erfunden", **extra})

    def evidence(self, eid: str, study: str = "st-eins", relation: str = "stuetzt",
                 claim: str = "cl-a", released: bool = True, **extra) -> dict:
        record = {
            "id": eid, "claim_id": claim, "study_id": study, "study_version": "v1",
            "locator": "Tabelle 1, Zeile 2", "metric": "Kennzahl", "values": {"a": 0.9, "b": 0.7},
            "uncertainty": "nicht berichtet", "relation": relation,
            "review_status": "freigegeben" if released else "vorgeschlagen"}
        if released:
            record |= {"extracted_by": "Ada", "reviewed_by": "Ben"}
        if not {"dataset_id", "event_ids", "basis_ids"} & set(extra):
            record["dataset_id"] = "ds-eins"
        return self.put("evidence", record | extra)

    def decide(self, did: str, target: str, outcome: str, date: str, **extra) -> dict:
        kind = "meilenstein" if target.startswith("ms-") else "aussage"
        record = {
            "id": did, "date": date, "kind": kind, "target_id": target, "outcome": outcome,
            "rationale": "Begründung der Prüfenden.", "assurance": ["quellenabgleich"],
            "extracted_by": "Ada", "reviewed_by": "Ben", "evidence_ids": ["ev-a"],
            "status": "freigegeben"}
        if kind == "meilenstein":
            record["catalog_version"] = 1
        record |= extra
        return self.put("decisions", {k: v for k, v in record.items() if v is not None})


MILESTONES = ["ms-a", "ms-b", "ms-c", "ms-d"]


@pytest.fixture
def world(tmp_path: Path) -> World:
    """Ein Ziel mit vier Meilensteinen, eine Aussage, eine Studie, ein freigegebener Beleg."""
    w = World(tmp_path)
    w.put("goals", {
        "id": "goal-test", "field": "Testfach", "title": "Erfundenes Ziel",
        "milestones": [{"id": m, "title": m, "criterion": "Kriterium"} for m in MILESTONES],
        "catalog": [{"version": 1, "date": "2026-01-01", "reason": "Erster Katalog", "milestones": MILESTONES}],
    })
    w.put("claims", {"id": "cl-a", "statement": "Erfundene Aussage.", "scope": "Testdaten",
                     "milestone_ids": ["ms-a", "ms-b"]})
    w.study("st-eins")
    w.dataset("ds-eins")
    w.evidence("ev-a")
    return w
