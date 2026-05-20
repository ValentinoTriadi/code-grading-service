"""Checkpoint / resume state for the experiment.

Two persistence layers:

1. `state.json` — small JSON blob at the experiment root that tracks per-batch
   metadata (Gemini batch resource names + status) plus the Phase 1 picker
   outputs. This is what lets `runner` resume after Ctrl-C / crash / network
   failure: re-running the CLI re-reads the state and continues from the
   batches that were already submitted.

2. `results/phase{1,2}.jsonl` — append-only result rows. Each completed
   grading is one JSON object on its own line. Resume skips run_ids that
   already appear in the file.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from experiments.config import PHASE1_RESULTS, PHASE2_RESULTS, STATE_FILE


@dataclass
class BatchEntry:
    batch_name: str | None = None
    status: str = "PENDING"  # PENDING | RUNNING | SUCCEEDED | FAILED
    request_count: int = 0
    error: str | None = None


@dataclass
class Phase1State:
    batches: dict[str, BatchEntry] = field(default_factory=dict)  # scenario_id -> entry
    complete: bool = False
    best_scenario_id: str | None = None
    worst_case_id: str | None = None
    metrics: dict | None = None  # {"S1": {"mae": ..., "pearson": ...}, ...}


@dataclass
class Phase2State:
    batch: BatchEntry = field(default_factory=BatchEntry)
    complete: bool = False
    icc: float | None = None
    icc_ci: tuple[float, float] | None = None


@dataclass
class ExperimentState:
    phase1: Phase1State = field(default_factory=Phase1State)
    phase2: Phase2State = field(default_factory=Phase2State)


def load_state() -> ExperimentState:
    if not STATE_FILE.exists():
        return ExperimentState()
    raw = json.loads(STATE_FILE.read_text())
    p1 = raw.get("phase1") or {}
    p2 = raw.get("phase2") or {}
    phase1 = Phase1State(
        batches={k: BatchEntry(**v) for k, v in (p1.get("batches") or {}).items()},
        complete=p1.get("complete", False),
        best_scenario_id=p1.get("best_scenario_id"),
        worst_case_id=p1.get("worst_case_id"),
        metrics=p1.get("metrics"),
    )
    phase2 = Phase2State(
        batch=BatchEntry(**(p2.get("batch") or {})),
        complete=p2.get("complete", False),
        icc=p2.get("icc"),
        icc_ci=tuple(p2["icc_ci"]) if p2.get("icc_ci") else None,
    )
    return ExperimentState(phase1=phase1, phase2=phase2)


def save_state(state: ExperimentState) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "phase1": {
            "batches": {k: asdict(v) for k, v in state.phase1.batches.items()},
            "complete": state.phase1.complete,
            "best_scenario_id": state.phase1.best_scenario_id,
            "worst_case_id": state.phase1.worst_case_id,
            "metrics": state.phase1.metrics,
        },
        "phase2": {
            "batch": asdict(state.phase2.batch),
            "complete": state.phase2.complete,
            "icc": state.phase2.icc,
            "icc_ci": list(state.phase2.icc_ci) if state.phase2.icc_ci else None,
        },
    }
    STATE_FILE.write_text(json.dumps(payload, indent=2))


def load_completed_run_ids(path: Path) -> set[str]:
    """Read a phase JSONL and return the set of run_ids already persisted."""
    if not path.exists():
        return set()
    seen: set[str] = set()
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                rid = row.get("run_id")
                if rid:
                    seen.add(rid)
            except json.JSONDecodeError:
                continue
    return seen


def append_results(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def load_results(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


PHASE1_PATH = PHASE1_RESULTS
PHASE2_PATH = PHASE2_RESULTS
