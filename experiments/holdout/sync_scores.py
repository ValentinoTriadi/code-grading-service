"""Sync manual grades from grading_sheet.csv into submissions.json.

Reads the four-criteria scoring sheet (Correctness/45, Efficiency/25,
Approach/15, CodeQuality/15, total/100) and writes each submission's
`human_score` (= total) and `human_score_breakdown` (per-criterion, matching
the {name, score, max_score} schema used in experiments/dataset/).

Run from the repo root:
    python -m experiments.holdout.sync_scores
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).parent
# The blind re-grade (graded independently of Gemini/Olympia) is the
# authoritative human reference; fall back to the original sheet if absent.
SHEET = HERE / "grading_sheet_blind.csv"
if not SHEET.exists():
    SHEET = HERE / "grading_sheet.csv"
SUBMISSIONS = HERE / "submissions.json"

# CSV column -> (breakdown name, max_score)
CRITERIA = [
    ("Correctness(/45)", "Correctness", 45),
    ("Efficiency(/25)", "Efficiency", 25),
    ("Approach(/15)", "Approach", 15),
    ("CodeQuality(/15)", "Code Quality", 15),
]


def load_sheet() -> dict[str, dict]:
    graded: dict[str, dict] = {}
    with SHEET.open(newline="") as fh:
        for row in csv.DictReader(fh):
            sid = row["submission_id"].strip()
            breakdown = [
                {"name": name, "score": float(row[col]), "max_score": mx}
                for col, name, mx in CRITERIA
            ]
            total = float(row["total(/100)"])
            component_sum = sum(c["score"] for c in breakdown)
            if abs(component_sum - total) > 1e-6:
                raise ValueError(
                    f"{sid}: components sum to {component_sum} but total is {total}"
                )
            graded[sid] = {"human_score": total, "human_score_breakdown": breakdown}
    return graded


def main() -> int:
    graded = load_sheet()
    submissions = json.loads(SUBMISSIONS.read_text())

    missing = [s["submission_id"] for s in submissions if s["submission_id"] not in graded]
    if missing:
        raise SystemExit(f"No sheet row for: {missing}")

    for sub in submissions:
        g = graded[sub["submission_id"]]
        sub["human_score"] = g["human_score"]
        sub["human_score_breakdown"] = g["human_score_breakdown"]

    SUBMISSIONS.write_text(json.dumps(submissions, indent=2, ensure_ascii=False) + "\n")
    print(f"Synced {len(submissions)} submissions -> {SUBMISSIONS.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
