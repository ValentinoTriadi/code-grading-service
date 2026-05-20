"""Generate per-problem grading worksheets in Markdown.

For each problem, writes a single file at
`experiments/dataset/worksheets/<problem_id>-<slug>.md` containing:

  - Problem description and rubric at the top
  - Every submission's code in a fenced block
  - A blank score line per criterion plus a Total

You fill the worksheet in by hand (paper, iPad, anywhere), then transcribe
into submissions.json via the CLI grader (or by hand).

Run:
    uv run python -m experiments.grading.worksheet
    uv run python -m experiments.grading.worksheet --problem P3
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from experiments.grading.rubric import Criterion, parse


DATASET = Path(__file__).resolve().parents[1] / "dataset"
PROBLEMS_PATH = DATASET / "problems.json"
SUBMISSIONS_PATH = DATASET / "submissions.json"
OUT_DIR = DATASET / "worksheets"


_LANG_FENCE = {
    "python": "python",
    "py": "python",
    "java": "java",
    "typescript": "ts",
    "ts": "ts",
    "cpp": "cpp",
    "c++": "cpp",
    "go": "go",
}


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _fence(language: str) -> str:
    return _LANG_FENCE.get(language.lower(), "")


def _render(problem: dict, criteria: list[Criterion], submissions: list[dict]) -> str:
    lines: list[str] = []
    lines.append(f"# {problem['problem_id']} — {problem['name']}")
    lines.append(f"_{problem['difficulty']} · {problem['language']} · {len(submissions)} submissions_")
    lines.append("")
    lines.append("## Description")
    lines.append("")
    lines.append(problem["description"])
    lines.append("")
    lines.append("## Rubric")
    lines.append("")
    for c in criteria:
        lines.append(f"- **{c.name} ({c.max_score})** — {c.description}")
    lines.append("")
    lines.append("## Score sheet")
    lines.append("")
    header = "| Submission | " + " | ".join(f"{c.name} ({c.max_score})" for c in criteria) + " | **Total** | Notes |"
    sep = "|---" * (len(criteria) + 3) + "|"
    lines.append(header)
    lines.append(sep)
    for sub in submissions:
        lines.append("| " + sub["submission_id"] + " | " + " | ".join(["    "] * len(criteria)) + " |        |       |")
    lines.append("")
    lines.append("## Submissions")
    lines.append("")
    fence_lang = _fence(problem["language"])
    for i, sub in enumerate(submissions, start=1):
        lines.append(f"### {i}. `{sub['submission_id']}`")
        lines.append("")
        lines.append(f"```{fence_lang}")
        lines.append(sub["code"].rstrip())
        lines.append("```")
        lines.append("")
        score_bullets = "  ".join(f"{c.name}: ____/{c.max_score}" for c in criteria)
        lines.append(f"> {score_bullets}  →  **Total: ____/100**")
        lines.append(">")
        lines.append("> Notes:")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--problem", help="Only generate the worksheet for this problem_id")
    args = ap.parse_args()

    problems = json.loads(PROBLEMS_PATH.read_text(encoding="utf-8"))
    submissions = json.loads(SUBMISSIONS_PATH.read_text(encoding="utf-8"))

    by_problem: dict[str, list[dict]] = defaultdict(list)
    for s in submissions:
        by_problem[s["problem_id"]].append(s)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for p in problems:
        pid = p["problem_id"]
        if args.problem and pid != args.problem:
            continue
        criteria = parse(p["rubric_structured"])
        subs = by_problem.get(pid, [])
        if not subs:
            print(f"  {pid}: no submissions, skipping")
            continue
        path = OUT_DIR / f"{pid}-{_slug(p['name'])}.md"
        path.write_text(_render(p, criteria, subs), encoding="utf-8")
        print(f"  wrote {path.relative_to(DATASET.parent.parent)} ({len(subs)} submissions)")
        written.append(path)

    if not written:
        print("Nothing written.")
        return 1
    print()
    print(f"Done. {len(written)} worksheet(s) under {OUT_DIR}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
