"""Interactive CLI grader for human_score on submissions.json.

Walks every submission for the selected problem(s). For each one, renders a
single-screen view with problem + rubric + code at the top and per-criterion
score prompts at the bottom. The screen is cleared and re-rendered between
inputs so the code stays in view while you score. The total is summed
automatically and written back along with the per-criterion breakdown:

    "human_score": 78,
    "human_score_breakdown": [
      {"name": "Correctness", "score": 50, "max_score": 60},
      {"name": "Code Quality", "score": 18, "max_score": 25},
      {"name": "Efficiency", "score": 10, "max_score": 15}
    ],
    "human_score_notes": "optional free-text"

Run:
    uv run python -m experiments.grading.cli            # grade all problems
    uv run python -m experiments.grading.cli --problem P3
    uv run python -m experiments.grading.cli --regrade  # include already-graded
    uv run python -m experiments.grading.cli --no-clear  # for piping/debugging

Keys (single-press, no enter needed):
    digit / .   start typing a score for the current criterion (then enter)
    ← / →       previous / next submission (also lets you edit graded ones)
    e           toggle expected/reference notes for this submission
    s           skip this submission (don't write)
    b           undo the last entry (or step back from the accept prompt)
    q           save and quit
    ?           show keybind help
"""

from __future__ import annotations

import argparse
import contextlib
import json
import re
import select
import shutil
import sys
import termios
import textwrap
import tty
from dataclasses import dataclass
from pathlib import Path

from experiments.grading.rubric import Criterion, parse


REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET = Path(__file__).resolve().parents[1] / "dataset"
PROBLEMS_PATH = DATASET / "problems.json"
SUBMISSIONS_PATH = DATASET / "submissions.json"

_CLEAR_SCREEN_AND_SCROLLBACK = "\x1b[H\x1b[2J\x1b[3J"
_DIM = "\x1b[2m"
_BOLD = "\x1b[1m"
_GREEN = "\x1b[32m"
_YELLOW = "\x1b[33m"
_CYAN = "\x1b[36m"
_RESET = "\x1b[0m"

CLEAR_SCREEN = True


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------


def _load_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(path: Path, data: list[dict]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _term_width(default: int = 80) -> int:
    return shutil.get_terminal_size((default, 24)).columns


def _clear() -> None:
    if CLEAR_SCREEN:
        sys.stdout.write(_CLEAR_SCREEN_AND_SCROLLBACK)
        sys.stdout.flush()


def _hr(char: str = "─") -> str:
    return char * _term_width()


def _wrap(text: str, indent: str = "  ") -> str:
    width = max(20, _term_width() - len(indent))
    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        if not paragraph.strip():
            lines.append("")
            continue
        wrapped = textwrap.wrap(paragraph, width=width) or [paragraph]
        lines.extend(indent + line for line in wrapped)
    return "\n".join(lines)


def _fmt_score(value: float) -> str:
    return f"{value:g}"


def _round_score(value: float) -> float:
    rounded = round(value, 1)
    return int(rounded) if rounded == int(rounded) else rounded


# ---------------------------------------------------------------------------
# Reference / README extraction
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ReferenceNote:
    group_heading: str  # "## Group A — Map reinsert trick (idiomatic JS/TS)"
    group_intro: str    # paragraph text under the heading, before the table
    table_row: str      # the row that mentions this submission

    def render(self) -> str:
        return f"{self.group_heading}\n\n{self.group_intro.strip()}\n\n{self.table_row.strip()}"


def _readme_path(problem: dict) -> Path:
    return REPO_ROOT / problem["source_dir"] / "README.md"


_README_CACHE: dict[str, str] = {}


def _load_readme(problem: dict) -> str:
    pid = problem["problem_id"]
    if pid not in _README_CACHE:
        path = _readme_path(problem)
        _README_CACHE[pid] = path.read_text(encoding="utf-8") if path.exists() else ""
    return _README_CACHE[pid]


def _extract_note(readme: str, submission_id: str) -> ReferenceNote | None:
    """Find the README row mentioning this submission and the group heading above it."""
    if not readme:
        return None
    lines = readme.splitlines()
    target_idx: int | None = None
    for i, line in enumerate(lines):
        if line.startswith("|") and submission_id in line:
            target_idx = i
            break
    if target_idx is None:
        return None

    # Walk backward to find the group heading.
    heading_idx = 0
    for j in range(target_idx - 1, -1, -1):
        if lines[j].startswith("## Group") or lines[j].startswith("## "):
            heading_idx = j
            break

    intro_lines: list[str] = []
    for k in range(heading_idx + 1, target_idx):
        line = lines[k]
        if line.startswith("|"):
            break
        if line.strip().startswith("---"):
            continue
        intro_lines.append(line)
    return ReferenceNote(
        group_heading=lines[heading_idx].strip(),
        group_intro="\n".join(intro_lines).strip(),
        table_row=lines[target_idx].strip(),
    )


# ---------------------------------------------------------------------------
# Raw-mode key input
# ---------------------------------------------------------------------------


@contextlib.contextmanager
def _raw_mode():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        yield
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _stdin_is_tty() -> bool:
    return sys.stdin.isatty()


_ARROW_MAP = {
    # Standard CSI cursor keys
    "\x1b[A": "up", "\x1b[B": "down", "\x1b[C": "right", "\x1b[D": "left",
    # SS3 form, sent in application-keypad mode by some terminals
    "\x1bOA": "up", "\x1bOB": "down", "\x1bOC": "right", "\x1bOD": "left",
}

DEBUG_KEYS = False


def _read_raw_key() -> str:
    """Read one logical keypress in raw mode. Tty-only.

    Returns: 'left', 'right', 'up', 'down', 'enter', 'backspace', 'escape',
    or a single character ('e', 's', 'q', 'b', '?', '0'..'9', '.', '-', etc.)
    """
    with _raw_mode():
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            seq = ch
            # Read up to 5 more bytes so we can handle modified-arrow sequences
            # like ESC [ 1 ; 5 D (Ctrl+Left). Use a generous 250ms gap timeout —
            # the trailing bytes of an arrow key arrive within microseconds, but
            # some terminals or remote sessions are slow.
            for _ in range(5):
                if select.select([sys.stdin], [], [], 0.25)[0]:
                    seq += sys.stdin.read(1)
                else:
                    break
            if DEBUG_KEYS:
                sys.stdout.write(f"\n[debug] esc-seq bytes: {seq!r}\n")
                sys.stdout.flush()
            if seq in _ARROW_MAP:
                return _ARROW_MAP[seq]
            # Modified-arrow form: ESC [ <params> <letter> — accept the letter.
            if len(seq) >= 3 and seq[1] == "[" and seq[-1] in "ABCD":
                return {"A": "up", "B": "down", "C": "right", "D": "left"}[seq[-1]]
            return "escape"
        if ch in ("\r", "\n"):
            return "enter"
        if ch in ("\x7f", "\b"):
            return "backspace"
        if ch == "\x03":
            raise KeyboardInterrupt
        if DEBUG_KEYS:
            sys.stdout.write(f"\n[debug] key byte: {ch!r}\n")
            sys.stdout.flush()
        return ch


_CMD_ALIASES: dict[str, str] = {
    "left": "left", "<": "left", "<-": "left",
    "right": "right", ">": "right", "->": "right",
    "q": "quit", "quit": "quit",
    "s": "skip", "skip": "skip", "n": "skip",
    "b": "back", "back": "back",
    "e": "expected", "expected": "expected",
    "?": "help", "help": "help",
    "y": "accept", "yes": "accept",
}


def _read_score_or_command(prompt: str, max_value: float) -> tuple[str, float | None]:
    """Read either a numeric score or a command from the user.

    Returns ('score', value) or ('cmd', None) where the command is one of:
      'left', 'right', 'quit', 'skip', 'back', 'expected', 'help',
      'accept', 'noop' (unknown / ignore).

    Works for both tty (raw single-key + number entry) and non-tty (line mode).
    """
    print(prompt, end="", flush=True)
    if _stdin_is_tty():
        key = _read_raw_key()
        if key in _CMD_ALIASES:
            print()
            return (_CMD_ALIASES[key], None)
        if key in ("enter", "escape", "up", "down", "backspace"):
            print()
            return ("noop", None)
        if key in "0123456789.-":
            # User started a number; collect the rest of the line.
            print(key, end="", flush=True)
            try:
                rest = input()
            except EOFError:
                return ("quit", None)
            raw = (key + rest).strip()
        else:
            print()
            return ("noop", None)
    else:
        # Line mode: read whole line, treat as command if recognized, else number.
        try:
            line = input().strip().lower()
        except EOFError:
            return ("quit", None)
        if line in _CMD_ALIASES:
            return (_CMD_ALIASES[line], None)
        if line == "":
            return ("noop", None)
        raw = line

    # Number parse path (shared by tty and non-tty).
    try:
        value = float(raw)
    except ValueError:
        print(f"    not a number — must be 0..{max_value}")
        return ("noop", None)
    if value < 0 or value > max_value:
        print(f"    out of range — must be 0..{max_value}")
        return ("noop", None)
    return ("score", value)


def _read_command(prompt: str) -> str:
    """Like _read_score_or_command but only commands (no number expected). Returns command name."""
    print(prompt, end="", flush=True)
    if _stdin_is_tty():
        key = _read_raw_key()
        print()
        if key in _CMD_ALIASES:
            return _CMD_ALIASES[key]
        if key == "enter":
            return "accept"
        return "noop"
    else:
        try:
            line = input().strip().lower()
        except EOFError:
            return "quit"
        if line == "":
            return "accept"
        return _CMD_ALIASES.get(line, "noop")


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------


def _render(
    submission: dict,
    problem: dict,
    criteria: list[Criterion],
    scores: list[float],
    progress: str,
    *,
    show_reference: bool,
    reference: ReferenceNote | None,
    state_label: str,
    being_edited: bool,
) -> None:
    """Clear the screen and redraw the full grading view."""
    _clear()
    width = _term_width()

    # Header bar
    edit_tag = f"  {_YELLOW}[EDIT]{_RESET}" if being_edited else ""
    title = (
        f"{_BOLD}{problem['problem_id']} {problem['name']}{_RESET}"
        f"  ·  {_BOLD}{submission['submission_id']}{_RESET}{edit_tag}"
        f"  ·  {problem['difficulty']} · {problem['language']}"
    )
    print(_hr("═"))
    print(f" {progress}")
    print(f" {title}")
    print(_hr("═"))

    # Description
    print()
    print(f"{_DIM}DESCRIPTION{_RESET}")
    print(_wrap(problem["description"]))

    # Rubric
    print()
    print(f"{_DIM}RUBRIC{_RESET}")
    for c in criteria:
        head = f"  • {_BOLD}{c.name}{_RESET} ({c.max_score})  "
        body_indent = "    "
        body_width = max(20, width - len(body_indent))
        body_lines = textwrap.wrap(c.description, width=body_width) or [c.description]
        print(head + body_lines[0])
        for line in body_lines[1:]:
            print(body_indent + line)

    # Reference (if toggled on)
    if show_reference:
        print()
        print(f"{_DIM}REFERENCE — what this submission is meant to show  (press 'e' to hide){_RESET}")
        if reference is None:
            print(_wrap("(no per-submission note found in README)"))
        else:
            print(_wrap(reference.group_heading))
            if reference.group_intro:
                print()
                print(_wrap(reference.group_intro))
            print()
            print(_wrap(reference.table_row))

    # Code
    print()
    print(f"{_DIM}CODE{_RESET}")
    print(_hr("─"))
    print(submission["code"].rstrip())
    print(_hr("─"))

    # Score table
    print()
    print(f"{_DIM}SCORES{_RESET}")
    cursor = len(scores)
    total_so_far = 0.0
    for i, c in enumerate(criteria):
        if i < cursor:
            entered = _fmt_score(scores[i])
            total_so_far += scores[i]
            line = f"  {_GREEN}✓{_RESET} {c.name}: {_BOLD}{entered}{_RESET}/{c.max_score}"
        elif i == cursor and state_label == "scoring":
            line = f"  {_YELLOW}▶{_RESET} {c.name}: ___/{c.max_score}"
        else:
            line = f"    {c.name}: ___/{c.max_score}"
        print(line)
    if scores:
        total = sum(scores)
        if state_label == "confirming":
            print(f"  {_BOLD}TOTAL: {_fmt_score(total)} / 100{_RESET}")
        else:
            print(f"  {_DIM}running total: {_fmt_score(total_so_far)} / 100{_RESET}")
    print()

    # Keybind footer
    keybinds = (
        f"{_DIM}keys: {_RESET}"
        f"{_CYAN}←/→{_RESET} prev/next  "
        f"{_CYAN}e{_RESET} expected  "
        f"{_CYAN}s{_RESET} skip  "
        f"{_CYAN}b{_RESET} back  "
        f"{_CYAN}q{_RESET} quit  "
        f"{_CYAN}?{_RESET} help"
    )
    print(keybinds)


def _print_help_overlay() -> None:
    print()
    print(f"  {_BOLD}Keybinds{_RESET}")
    print("    digits / .   start typing a score (then enter)")
    print("    ← / →        previous / next submission (also enters edit mode for graded ones)")
    print("    e            toggle expected/reference notes for this submission")
    print("    s            skip this submission (do not write)")
    print("    b            undo the last entry / step back from accept prompt")
    print("    q            save and quit")
    print("    ?            show this help")
    print()
    if _stdin_is_tty():
        print("  press any key to continue...")
        _read_raw_key()
    else:
        try:
            input()
        except EOFError:
            pass


# ---------------------------------------------------------------------------
# Per-submission grading loop
# ---------------------------------------------------------------------------


_NavSignal = str  # 'left' | 'right' | 'skip' | 'quit'


def _grade_submission(
    submission: dict,
    problem: dict,
    criteria: list[Criterion],
    progress: str,
    *,
    existing_breakdown: list[dict] | None,
    reference: ReferenceNote | None,
) -> dict | _NavSignal:
    """Grade one submission. Returns:
      - dict: updated submission to save
      - 'left' / 'right': navigate to neighbouring submission
      - 'skip' / 'quit': control signals
    """
    show_reference = False
    being_edited = bool(existing_breakdown)

    # Pre-fill from existing breakdown when revisiting a graded submission.
    scores: list[float] = (
        [float(b["score"]) for b in existing_breakdown] if existing_breakdown else []
    )
    state = "confirming" if len(scores) == len(criteria) else "scoring"

    while True:
        _render(
            submission,
            problem,
            criteria,
            scores,
            progress,
            show_reference=show_reference,
            reference=reference,
            state_label=state,
            being_edited=being_edited,
        )

        if state == "scoring":
            current = criteria[len(scores)]
            kind, value = _read_score_or_command(
                f"  {current.name} (0..{current.max_score}): ", current.max_score
            )
            if kind == "score":
                assert value is not None
                scores.append(value)
                if len(scores) == len(criteria):
                    state = "confirming"
                continue
            if kind in {"left", "right", "quit", "skip"}:
                return kind
            if kind == "expected":
                show_reference = not show_reference
                continue
            if kind == "back":
                if scores:
                    scores.pop()
                continue
            if kind == "help":
                _print_help_overlay()
                continue
            # 'noop' or unknown — redraw
            continue

        elif state == "confirming":
            cmd = _read_command(
                "  accept? [y]es  [n]/[s]kip  [b]ack  [e]xpected  [←/→] nav  [q]uit: "
            )
            if cmd in {"left", "right", "quit", "skip"}:
                return cmd
            if cmd == "expected":
                show_reference = not show_reference
                continue
            if cmd == "help":
                _print_help_overlay()
                continue
            if cmd == "back":
                if scores:
                    scores.pop()
                state = "scoring"
                continue
            if cmd == "accept":
                try:
                    notes = input("  notes (optional, enter to skip): ").strip()
                except EOFError:
                    notes = ""
                breakdown = [
                    {"name": c.name, "score": scores[i], "max_score": c.max_score}
                    for i, c in enumerate(criteria)
                ]
                updated = {
                    **submission,
                    "human_score": _round_score(sum(scores)),
                    "human_score_breakdown": breakdown,
                }
                if notes:
                    updated["human_score_notes"] = notes
                return updated
            continue


# ---------------------------------------------------------------------------
# Outer loop
# ---------------------------------------------------------------------------


def main() -> int:
    global CLEAR_SCREEN
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--problem", help="Only grade submissions for this problem_id (e.g. P3)")
    ap.add_argument("--regrade", action="store_true", help="Start at first submission (graded or not), not the first ungraded")
    ap.add_argument("--no-clear", action="store_true", help="Don't clear the screen between renders (for piping/debugging)")
    ap.add_argument("--debug-keys", action="store_true", help="Print raw bytes for each keypress (diagnose arrow-key issues)")
    args = ap.parse_args()
    CLEAR_SCREEN = not args.no_clear
    global DEBUG_KEYS
    DEBUG_KEYS = args.debug_keys

    problems = {p["problem_id"]: p for p in _load_json(PROBLEMS_PATH)}
    submissions = _load_json(SUBMISSIONS_PATH)
    criteria_by_problem = {pid: parse(p["rubric_structured"]) for pid, p in problems.items()}

    # Queue contains every submission that matches the filter, graded or not.
    # Navigation lets the user move freely; default starting point is the first ungraded one.
    queue_indices: list[int] = []
    for idx, sub in enumerate(submissions):
        if args.problem and sub["problem_id"] != args.problem:
            continue
        queue_indices.append(idx)

    if not queue_indices:
        print("No submissions match the filter.")
        return 0

    if args.regrade:
        pos = 0
    else:
        pos = next(
            (i for i, idx in enumerate(queue_indices) if submissions[idx].get("human_score") is None),
            0,
        )

    completed_this_run = 0
    quit_requested = False

    try:
        while 0 <= pos < len(queue_indices):
            idx = queue_indices[pos]
            sub = submissions[idx]
            problem = problems[sub["problem_id"]]
            criteria = criteria_by_problem[sub["problem_id"]]

            graded_total = sum(1 for s in submissions if s.get("human_score") is not None)
            queue_graded = sum(
                1 for i in queue_indices if submissions[i].get("human_score") is not None
            )
            progress = (
                f"[{pos + 1}/{len(queue_indices)}]  "
                f"queue graded: {queue_graded}/{len(queue_indices)}  ·  "
                f"overall: {graded_total}/{len(submissions)}"
            )

            reference = _extract_note(_load_readme(problem), sub["submission_id"])
            existing = sub.get("human_score_breakdown") if sub.get("human_score") is not None else None

            result = _grade_submission(
                sub,
                problem,
                criteria,
                progress,
                existing_breakdown=existing,
                reference=reference,
            )

            if result == "quit":
                quit_requested = True
                break
            if result == "left":
                pos = max(0, pos - 1)
                continue
            if result == "right":
                pos = min(len(queue_indices) - 1, pos + 1)
                continue
            if result == "skip":
                pos += 1
                continue

            # Saved a submission.
            submissions[idx] = result
            _save_json(SUBMISSIONS_PATH, submissions)
            completed_this_run += 1
            pos += 1
    except KeyboardInterrupt:
        pass

    _clear()
    print(_hr("═"))
    print(f" Saved this session: {completed_this_run}")
    remaining_global = sum(1 for s in submissions if s.get("human_score") is None)
    print(f" Missing human_score: {remaining_global}/{len(submissions)}")
    if quit_requested:
        print(" (quit requested — re-run to resume)")
    print(_hr("═"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
