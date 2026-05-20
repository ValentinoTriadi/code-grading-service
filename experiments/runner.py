"""End-to-end experiment runner with checkpoint / resume.

Workflow:
    Phase 1 — accuracy:
        8 scenarios × ~144 submissions × 1 rep = ~1,152 batched calls
        compute MAE + Pearson per scenario (8 each)
        pick best scenario  = lowest MAE (Pearson r as tiebreaker)
        pick worst case     = problem with highest avg case-MAE across scenarios

    Phase 2 — consistency (winner stress test):
        1 best scenario × ~20 submissions of the worst case × 7 reps = ~140 calls
        compute ICC(A,1) on the resulting n × 7 matrix, with 95% CI

Checkpoint design:
    - `experiments/state.json` tracks Gemini batch resource names + status
      and the Phase 1 picker outputs.
    - `experiments/results/phase{1,2}.jsonl` are append-only result rows.
    - On resume: re-fetch existing batches by name, skip rows already in the
      JSONL. The CLI is idempotent — running the same command twice does the
      right thing whether or not work is in progress.

Usage:
    python -m experiments.runner status
    python -m experiments.runner phase1
    python -m experiments.runner phase2
    python -m experiments.runner all          # phase1 then phase2
    python -m experiments.runner reset        # WARNING: clears state + results
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass

from src.engine.response_parser import ResponseParser

from experiments import analysis, state
from experiments.config import (
    DATASET_DIR,
    FEW_SHOT_COUNT,
    PHASE1_RESULTS,
    PHASE2_RESULTS,
    RESULTS_DIR,
    STATE_FILE,
)
from experiments.gemini_batch import (
    build_inline_request,
    fetch_results,
    get_client,
    poll_batch,
    submit_batch,
)
from experiments.prompt import build_full_prompt
from experiments.scenarios import SCENARIOS, SCENARIOS_BY_ID, Scenario

logger = logging.getLogger(__name__)
PARSER = ResponseParser()

PHASE1_REPLICATES = 1
PHASE2_REPLICATES = 7


@dataclass
class Cell:
    """One Phase 1 or Phase 2 grading cell."""

    run_id: str
    phase: int
    scenario_id: str
    problem_id: str
    submission_id: str
    replicate: int
    prompt: str


# --- dataset ---------------------------------------------------------------


def load_dataset() -> tuple[list[dict], list[dict], list[dict]]:
    problems = json.loads((DATASET_DIR / "problems.json").read_text())
    submissions = json.loads((DATASET_DIR / "submissions.json").read_text())
    few_shot = json.loads((DATASET_DIR / "few_shot.json").read_text())
    return problems, submissions, few_shot


def assert_human_scores(submissions: list[dict]) -> None:
    missing = [s["submission_id"] for s in submissions if s.get("human_score") is None]
    if missing:
        raise RuntimeError(
            f"{len(missing)} submission(s) have human_score=null. "
            f"Fill in experiments/dataset/submissions.json before Phase 1. "
            f"First few missing: {missing[:5]}"
        )


# --- cell construction -----------------------------------------------------


def _phase1_cells_for_scenario(
    scenario: Scenario,
    problems_by_id: dict[str, dict],
    submissions: list[dict],
    few_shot_pool: list[dict],
) -> list[Cell]:
    cells: list[Cell] = []
    for sub in submissions:
        problem = problems_by_id[sub["problem_id"]]
        prompt = build_full_prompt(scenario, problem, sub, few_shot_pool, FEW_SHOT_COUNT)
        for r in range(PHASE1_REPLICATES):
            cells.append(
                Cell(
                    run_id=f"P1-{scenario.id}-{sub['submission_id']}-r{r}",
                    phase=1,
                    scenario_id=scenario.id,
                    problem_id=sub["problem_id"],
                    submission_id=sub["submission_id"],
                    replicate=r,
                    prompt=prompt,
                )
            )
    return cells


def _phase2_cells(
    scenario: Scenario,
    worst_case_id: str,
    problems_by_id: dict[str, dict],
    submissions: list[dict],
    few_shot_pool: list[dict],
) -> list[Cell]:
    cells: list[Cell] = []
    for sub in submissions:
        if sub["problem_id"] != worst_case_id:
            continue
        problem = problems_by_id[sub["problem_id"]]
        prompt = build_full_prompt(scenario, problem, sub, few_shot_pool, FEW_SHOT_COUNT)
        for r in range(PHASE2_REPLICATES):
            cells.append(
                Cell(
                    run_id=f"P2-{scenario.id}-{sub['submission_id']}-r{r}",
                    phase=2,
                    scenario_id=scenario.id,
                    problem_id=sub["problem_id"],
                    submission_id=sub["submission_id"],
                    replicate=r,
                    prompt=prompt,
                )
            )
    return cells


# --- result row construction ----------------------------------------------


def _row_from_response(cell: Cell, batch_row: dict) -> dict:
    """Parse one batch response into a result row matching the JSONL schema."""
    text = batch_row.get("text") or ""
    err = batch_row.get("error")
    parsed = None
    schema_valid = False
    score = 0.0
    criterion_scores: list[dict] = []
    if text and not err:
        try:
            parsed = PARSER.parse(text)
            schema_valid = parsed.feedback_detail is not None
            score = parsed.score
            if parsed.feedback_detail:
                criterion_scores = [
                    {
                        "name": c.name,
                        "score": c.score,
                        "max_score": c.max_score,
                    }
                    for c in parsed.feedback_detail.criteria
                ]
        except Exception as exc:  # pragma: no cover — parsing failure
            err = err or f"parse_error: {exc!r}"

    return {
        "run_id": cell.run_id,
        "phase": cell.phase,
        "scenario_id": cell.scenario_id,
        "problem_id": cell.problem_id,
        "submission_id": cell.submission_id,
        "replicate": cell.replicate,
        "score": score,
        "criterion_scores": criterion_scores,
        "raw_response": text,
        "tokens_in": batch_row.get("tokens_in", 0),
        "tokens_out": batch_row.get("tokens_out", 0),
        "cached_tokens": batch_row.get("cached_tokens", 0),
        "schema_valid": schema_valid,
        "error": err,
    }


# --- batch lifecycle -------------------------------------------------------


def _ensure_batch_submitted(
    client,
    entry: state.BatchEntry,
    cells: list[Cell],
    completed_run_ids: set[str],
    display_name: str,
) -> tuple[list[Cell], state.BatchEntry]:
    """If no batch yet, build one for the cells that aren't already done.

    Returns (cells_in_batch, updated_entry). `cells_in_batch` aligns 1:1 with
    inline responses so we can match metadata back. If everything's already
    completed in the JSONL, returns ([], entry) and skips submission.
    """
    pending = [c for c in cells if c.run_id not in completed_run_ids]
    if not pending:
        if entry.status != "SUCCEEDED":
            entry.status = "SUCCEEDED"
        return [], entry
    if entry.batch_name:
        # Already submitted — caller will poll/fetch.
        return pending, entry

    inline_requests = [build_inline_request(c.prompt, c.run_id) for c in pending]
    batch_name = submit_batch(client, inline_requests, display_name=display_name)
    entry.batch_name = batch_name
    entry.status = "RUNNING"
    entry.request_count = len(inline_requests)
    return pending, entry


def _ingest_batch(
    client,
    entry: state.BatchEntry,
    cells_in_batch: list[Cell],
    results_path,
) -> tuple[int, int]:
    """Poll, fetch, parse, and append rows for a batch. Returns (succeeded, failed)."""
    if not entry.batch_name:
        return 0, 0
    job = poll_batch(client, entry.batch_name)
    state_name = getattr(job.state, "name", str(job.state))
    if state_name != "JOB_STATE_SUCCEEDED":
        entry.status = state_name
        entry.error = str(getattr(job, "error", None))
        return 0, len(cells_in_batch)

    raw_rows = fetch_results(job)
    by_run_id = {r["run_id"]: r for r in raw_rows if r.get("run_id")}
    rows_to_append: list[dict] = []
    succeeded = 0
    failed = 0
    for cell in cells_in_batch:
        raw = by_run_id.get(cell.run_id)
        if raw is None:
            failed += 1
            rows_to_append.append(
                _row_from_response(
                    cell,
                    {
                        "text": "",
                        "tokens_in": 0,
                        "tokens_out": 0,
                        "cached_tokens": 0,
                        "error": "missing_in_batch_response",
                    },
                )
            )
            continue
        row = _row_from_response(cell, raw)
        rows_to_append.append(row)
        if row["schema_valid"]:
            succeeded += 1
        else:
            failed += 1
    state.append_results(results_path, rows_to_append)
    entry.status = "SUCCEEDED"
    return succeeded, failed


# --- phase orchestration ---------------------------------------------------


def run_phase1(s: state.ExperimentState) -> state.ExperimentState:
    """Run Phase 1: submit ALL 8 scenarios up-front, then poll + fetch each.

    The two passes are the key win — submitting all batches first lets them
    run in parallel on Google's infrastructure. Wall time then becomes
    `submit_time + max(batch_duration)` instead of
    `sum(submit + batch_duration)` per scenario, which is roughly an 8×
    speed-up for the typical case where every scenario finishes within
    minutes of the slowest one.
    """
    problems, submissions, few_shot_pool = load_dataset()
    assert_human_scores(submissions)
    problems_by_id = {p["problem_id"]: p for p in problems}

    client = get_client()
    completed = state.load_completed_run_ids(PHASE1_RESULTS)
    logger.info("Phase 1 — %d run_ids already in %s", len(completed), PHASE1_RESULTS.name)

    # Pass 1 — submit (or recover) every batch up-front so they all run
    # concurrently on the provider side.
    pending_ingest: dict[str, list[Cell]] = {}
    for scenario in SCENARIOS:
        entry = s.phase1.batches.get(scenario.id) or state.BatchEntry()
        if entry.status in {"JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "FAILED"}:
            logger.error(
                "Phase 1 — scenario %s in terminal failure (%s): %s. "
                "Inspect state.json and clear that scenario's entry "
                "(or `python -m experiments.runner reset --yes`) to retry.",
                scenario.id,
                entry.status,
                entry.error,
            )
            continue
        cells = _phase1_cells_for_scenario(
            scenario, problems_by_id, submissions, few_shot_pool
        )
        cells_in_batch, entry = _ensure_batch_submitted(
            client,
            entry,
            cells,
            completed,
            display_name=f"phase1-{scenario.id}",
        )
        s.phase1.batches[scenario.id] = entry
        state.save_state(s)
        if cells_in_batch and entry.batch_name and entry.status != "SUCCEEDED":
            pending_ingest[scenario.id] = cells_in_batch

    logger.info(
        "Phase 1 — submitted/recovered %d batch(es); now polling in parallel",
        len(pending_ingest),
    )

    # Pass 2 — poll + fetch each batch. Polls are sequential in code, but the
    # batches are all running concurrently server-side; once the slowest is
    # done, the others are too, so the second/third/... poll usually returns
    # SUCCEEDED on the first GET.
    for scenario_id, cells_in_batch in pending_ingest.items():
        entry = s.phase1.batches[scenario_id]
        ok, bad = _ingest_batch(client, entry, cells_in_batch, PHASE1_RESULTS)
        logger.info(
            "Phase 1 — scenario %s: %d ok, %d failed", scenario_id, ok, bad
        )
        s.phase1.batches[scenario_id] = entry
        state.save_state(s)

    if not all(e.status == "SUCCEEDED" for e in s.phase1.batches.values()):
        logger.warning("Phase 1 incomplete — some batches not in SUCCEEDED state")
        return s

    # Compute metrics + pickers.
    rows = state.load_results(PHASE1_RESULTS)
    submissions_by_id = {sub["submission_id"]: sub for sub in submissions}
    scenario_metrics = analysis.compute_phase1_metrics(rows, submissions_by_id)
    if not scenario_metrics:
        raise RuntimeError(
            "Phase 1 produced no schema-valid rows — cannot pick a winner."
        )
    best_scenario_id = analysis.pick_best_scenario(scenario_metrics)
    worst_case_id, case_avg_mae = analysis.pick_worst_case(rows, submissions_by_id)

    s.phase1.complete = True
    s.phase1.best_scenario_id = best_scenario_id
    s.phase1.worst_case_id = worst_case_id
    s.phase1.metrics = scenario_metrics
    state.save_state(s)

    print(
        analysis.format_phase1_table(
            scenario_metrics, case_avg_mae, best_scenario_id, worst_case_id
        )
    )
    anova = analysis.compute_phase1_anova(rows, submissions_by_id, SCENARIOS_BY_ID)
    print(analysis.format_phase1_anova(anova))
    return s


def run_phase2(s: state.ExperimentState) -> state.ExperimentState:
    if not s.phase1.complete:
        raise RuntimeError("Phase 1 must complete before Phase 2.")
    if not s.phase1.best_scenario_id or not s.phase1.worst_case_id:
        raise RuntimeError("Phase 1 picker outputs missing — re-run phase 1.")

    problems, submissions, few_shot_pool = load_dataset()
    assert_human_scores(submissions)
    problems_by_id = {p["problem_id"]: p for p in problems}
    scenario = SCENARIOS_BY_ID[s.phase1.best_scenario_id]
    worst_case_id = s.phase1.worst_case_id

    client = get_client()
    completed = state.load_completed_run_ids(PHASE2_RESULTS)
    logger.info("Phase 2 — %d run_ids already in %s", len(completed), PHASE2_RESULTS.name)

    cells = _phase2_cells(
        scenario, worst_case_id, problems_by_id, submissions, few_shot_pool
    )

    entry = s.phase2.batch
    if entry.status in {"JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "FAILED"}:
        raise RuntimeError(
            f"Phase 2 batch in terminal failure ({entry.status}): {entry.error}. "
            f"Clear `phase2.batch` in state.json (or run `reset --yes`) to retry."
        )
    cells_in_batch, entry = _ensure_batch_submitted(
        client,
        entry,
        cells,
        completed,
        display_name=f"phase2-{scenario.id}-{worst_case_id}",
    )
    s.phase2.batch = entry
    state.save_state(s)

    if cells_in_batch and entry.batch_name and entry.status != "SUCCEEDED":
        ok, bad = _ingest_batch(client, entry, cells_in_batch, PHASE2_RESULTS)
        logger.info("Phase 2 — %s: %d ok, %d failed", scenario.id, ok, bad)
        s.phase2.batch = entry
        state.save_state(s)

    if entry.status != "SUCCEEDED":
        logger.warning("Phase 2 incomplete — batch not SUCCEEDED")
        return s

    # Compute ICC.
    rows = state.load_results(PHASE2_RESULTS)
    matrix, sids = analysis.build_icc_matrix(rows)
    if not matrix:
        raise RuntimeError("Phase 2 produced no schema-valid replicate matrix.")
    icc, ci = analysis.compute_icc(matrix)
    n = len(matrix)
    k = len(matrix[0])

    s.phase2.complete = True
    s.phase2.icc = icc
    s.phase2.icc_ci = ci
    state.save_state(s)

    print(
        analysis.format_phase2_summary(
            scenario.id, worst_case_id, icc, ci, n, k
        )
    )
    return s


# --- CLI -------------------------------------------------------------------


def cmd_status(_args: argparse.Namespace) -> int:
    s = state.load_state()
    print(f"state file : {STATE_FILE}")
    print(f"phase 1    : complete={s.phase1.complete}")
    for sid in sorted(s.phase1.batches):
        e = s.phase1.batches[sid]
        print(
            f"  {sid}: status={e.status}, batch={e.batch_name or '-'}, "
            f"requests={e.request_count}"
        )
    if s.phase1.metrics:
        print(f"  best   : {s.phase1.best_scenario_id}")
        print(f"  worst  : {s.phase1.worst_case_id}")
    print(f"phase 2    : complete={s.phase2.complete}")
    e = s.phase2.batch
    print(
        f"  status={e.status}, batch={e.batch_name or '-'}, requests={e.request_count}"
    )
    if s.phase2.icc is not None:
        print(
            f"  ICC(A,1)={s.phase2.icc:.3f} CI={s.phase2.icc_ci}"
        )
    return 0


def cmd_phase1(_args: argparse.Namespace) -> int:
    s = state.load_state()
    run_phase1(s)
    return 0


def cmd_phase2(_args: argparse.Namespace) -> int:
    s = state.load_state()
    run_phase2(s)
    return 0


def cmd_all(_args: argparse.Namespace) -> int:
    s = state.load_state()
    s = run_phase1(s)
    if not s.phase1.complete:
        logger.error("Phase 1 didn't complete — cannot start Phase 2.")
        return 1
    run_phase2(s)
    return 0


def cmd_reset(args: argparse.Namespace) -> int:
    if not args.yes:
        print(
            "Refusing to reset without --yes. This deletes state.json and "
            "results/phase{1,2}.jsonl. Pass --yes to confirm."
        )
        return 1
    for p in (STATE_FILE, PHASE1_RESULTS, PHASE2_RESULTS):
        if p.exists():
            p.unlink()
            print(f"removed {p}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="experiments.runner",
        description="Run the LLM-grading experiment with Gemini Batch + checkpointing.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="Print current state and exit.").set_defaults(
        func=cmd_status
    )
    sub.add_parser(
        "phase1",
        help="Run / resume Phase 1 (accuracy). Idempotent — safe to re-run.",
    ).set_defaults(func=cmd_phase1)
    sub.add_parser(
        "phase2",
        help="Run / resume Phase 2 (consistency). Requires Phase 1 complete.",
    ).set_defaults(func=cmd_phase2)
    sub.add_parser(
        "all",
        help="Run / resume Phase 1, then Phase 2 in one go.",
    ).set_defaults(func=cmd_all)
    reset = sub.add_parser(
        "reset",
        help="Delete state.json and results JSONLs. Requires --yes.",
    )
    reset.add_argument("--yes", action="store_true", help="Confirm destructive reset.")
    reset.set_defaults(func=cmd_reset)

    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    )
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
