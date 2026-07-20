"""Structural sanity checks for human-graded submissions.json.

Run after grading (or partway through) to surface mistakes that are easy to
make under fatigue. NO LLM call — purely structural.

Checks:
  1. Missing scores  — `human_score` is null.
  2. Score out of range — outside [0, 100].
  3. Breakdown mismatch — sum of `human_score_breakdown` scores != `human_score`,
     or any sub-score outside [0, max_score], or breakdown criteria don't match
     the rubric for that problem.
  4. Identical code, different scores — submissions whose normalized code
     (whitespace-collapsed) is identical but `human_score` differs.
  5. Intra-problem outliers — submissions whose `human_score` is more than
     2.5 z-scores from the per-problem mean.

Exit code is 0 if no issues, 1 otherwise.

Run:
    uv run python -m experiments.grading.sanity
    uv run python -m experiments.grading.sanity --problem P3
    uv run python -m experiments.grading.sanity --z-threshold 2.0
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from math import sqrt
from pathlib import Path

from experiments.grading.rubric import parse


DATASET = Path(__file__).resolve().parents[1] / "dataset"
PROBLEMS_PATH = DATASET / "problems.json"
SUBMISSIONS_PATH = DATASET / "submissions.json"


def _normalize_code(code: str) -> str:
    return re.sub(r"\s+", " ", code).strip()


def _check_missing(submissions: list[dict]) -> list[str]:
    issues: list[str] = []
    for s in submissions:
        if s.get("human_score") is None:
            issues.append(f"  {s['submission_id']}: missing human_score")
    return issues


def _check_range(submissions: list[dict]) -> list[str]:
    issues: list[str] = []
    for s in submissions:
        score = s.get("human_score")
        if score is None:
            continue
        if not isinstance(score, (int, float)):
            issues.append(f"  {s['submission_id']}: human_score is {type(score).__name__}, expected number")
            continue
        if score < 0 or score > 100:
            issues.append(f"  {s['submission_id']}: human_score={score} outside [0, 100]")
    return issues


def _check_breakdown(submissions: list[dict], criteria_by_problem: dict[str, list]) -> list[str]:
    issues: list[str] = []
    for s in submissions:
        breakdown = s.get("human_score_breakdown")
        if breakdown is None:
            continue
        score = s.get("human_score")
        criteria = criteria_by_problem.get(s["problem_id"], [])
        rubric_names = [c.name for c in criteria]
        rubric_max = {c.name: c.max_score for c in criteria}

        if not isinstance(breakdown, list):
            issues.append(f"  {s['submission_id']}: breakdown is not a list")
            continue

        breakdown_names = [item.get("name") for item in breakdown]
        if breakdown_names != rubric_names:
            issues.append(
                f"  {s['submission_id']}: breakdown criteria {breakdown_names} "
                f"don't match rubric {rubric_names}"
            )
            continue

        for item in breakdown:
            sub_score = item.get("score")
            sub_max = item.get("max_score")
            name = item.get("name")
            expected_max = rubric_max.get(name)
            if sub_max != expected_max:
                issues.append(
                    f"  {s['submission_id']}: breakdown[{name}].max_score={sub_max}, "
                    f"rubric expects {expected_max}"
                )
            if not isinstance(sub_score, (int, float)) or sub_score < 0 or sub_score > (expected_max or 100):
                issues.append(
                    f"  {s['submission_id']}: breakdown[{name}].score={sub_score} "
                    f"outside [0, {expected_max}]"
                )

        total = sum(item.get("score", 0) for item in breakdown)
        if score is not None and abs(total - score) > 0.05:
            issues.append(
                f"  {s['submission_id']}: breakdown sums to {total} but human_score={score}"
            )
    return issues


def _check_duplicate_code(submissions: list[dict]) -> list[str]:
    by_code: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for s in submissions:
        if s.get("human_score") is None:
            continue
        key = (s["problem_id"], _normalize_code(s["code"]))
        by_code[key].append(s)
    issues: list[str] = []
    for (pid, _code), group in by_code.items():
        if len(group) <= 1:
            continue
        scores = {s["submission_id"]: s["human_score"] for s in group}
        if len(set(scores.values())) > 1:
            issues.append(
                f"  {pid}: identical code, different scores → "
                + ", ".join(f"{sid}={sc}" for sid, sc in scores.items())
            )
    return issues


def _check_outliers(submissions: list[dict], threshold: float) -> list[str]:
    by_problem: dict[str, list[dict]] = defaultdict(list)
    for s in submissions:
        if isinstance(s.get("human_score"), (int, float)):
            by_problem[s["problem_id"]].append(s)
    issues: list[str] = []
    for pid, group in by_problem.items():
        if len(group) < 5:
            continue
        scores = [s["human_score"] for s in group]
        mean = sum(scores) / len(scores)
        var = sum((x - mean) ** 2 for x in scores) / len(scores)
        std = sqrt(var)
        if std == 0:
            continue
        for s in group:
            z = (s["human_score"] - mean) / std
            if abs(z) > threshold:
                issues.append(
                    f"  {s['submission_id']} ({pid}): score={s['human_score']} "
                    f"is {z:+.2f} sigma from problem mean ({mean:.1f}, sd {std:.1f})"
                )
    return issues


def _section(title: str, issues: list[str]) -> bool:
    if not issues:
        print(f"✓ {title}: clean")
        return False
    print(f"✗ {title}: {len(issues)} issue(s)")
    for line in issues:
        print(line)
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--problem", help="Only check submissions for this problem_id")
    ap.add_argument("--z-threshold", type=float, default=2.5, help="Outlier z-score threshold (default 2.5)")
    args = ap.parse_args()

    problems = json.loads(PROBLEMS_PATH.read_text(encoding="utf-8"))
    submissions = json.loads(SUBMISSIONS_PATH.read_text(encoding="utf-8"))
    criteria_by_problem = {p["problem_id"]: parse(p["rubric_structured"]) for p in problems}

    if args.problem:
        submissions = [s for s in submissions if s["problem_id"] == args.problem]

    print(f"Checking {len(submissions)} submission(s)" + (f" for {args.problem}" if args.problem else ""))
    print()

    any_issue = False
    any_issue |= _section("missing scores", _check_missing(submissions))
    any_issue |= _section("score range [0,100]", _check_range(submissions))
    any_issue |= _section("breakdown consistency", _check_breakdown(submissions, criteria_by_problem))
    any_issue |= _section("identical code, different scores", _check_duplicate_code(submissions))
    any_issue |= _section(
        f"intra-problem outliers (|z| > {args.z_threshold})",
        _check_outliers(submissions, args.z_threshold),
    )
    print()
    if any_issue:
        print("Found issues — review above. Outliers may be legitimate; the others usually are not.")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
