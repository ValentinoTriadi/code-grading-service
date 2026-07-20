#!/usr/bin/env python3
"""run_cases.py — run every Concurrent Worker Pool (P6) submission.

Each pool_*.go file in this directory implements `ParallelMap` in
`package pool`. They cannot be compiled together (duplicate symbols), and
several deadlock, race, or panic by design, so every submission is run in
isolation in a throwaway Go module.

Two modes:

  flow (default)  — copies a submission into a temp module and runs a driver
                    (_demo_main.go) that instruments `fn` and prints a
                    timestamped timeline: which input each call picks up, the
                    completion order, peak concurrency, and the final output.
                    You watch the submission actually execute.

  --test          — copies a submission next to a go-test harness
                    (_harness_test.go) and runs `go test -race`, printing a
                    pass/fail verdict per submission.

Both modes use the race detector (catches data races) and a timeout (catches
deadlocks / hangs).

Usage:
    python run_cases.py                      # flow mode, every submission
    python run_cases.py --file pool_a3.go    # one submission (repeatable)
    python run_cases.py --test               # go-test harness instead
    python run_cases.py --verbose            # also dump raw tool output
    python run_cases.py --go-version 1.22    # see note below
    python run_cases.py --no-race            # skip the race detector
    python run_cases.py --timeout 30         # per-submission run timeout
    python run_cases.py --keep               # keep the temp modules

Go version note:
    The generated go.mod declares `go 1.21` by default, which keeps the
    pre-1.22 loop-variable semantics — so pool_e1.go reproduces its documented
    "captures loop variable" bug. Pass --go-version 1.22 to use per-iteration
    loop variables, under which pool_e1.go becomes correct.

Requires the Go toolchain on PATH.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS = HERE / "_harness_test.go"
DEMO_MAIN = HERE / "_demo_main.go"
README = HERE / "README.md"

BUILD_TIMEOUT = 240  # seconds; first race-instrumented build is the slow one

# ANSI styling — disabled automatically when stdout is not a terminal.
_TTY = sys.stdout.isatty()


def _c(code: str) -> str:
    return code if _TTY else ""


GREEN, RED, YELLOW, CYAN, MAGENTA = (
    _c("\033[32m"), _c("\033[31m"), _c("\033[33m"), _c("\033[36m"), _c("\033[35m")
)
DIM, BOLD, RESET = _c("\033[2m"), _c("\033[1m"), _c("\033[0m")

# Verdict -> colour. PASS/OK are the clean outcomes (test / flow respectively).
VERDICT_COLOUR = {
    "PASS": GREEN,
    "OK": GREEN,
    "WRONG ORDER": RED,
    "FAIL": RED,
    "PANIC": RED,
    "RACE": MAGENTA,
    "DEADLOCK": YELLOW,
    "TIMEOUT": YELLOW,
    "BUILD ERROR": CYAN,
}
SUMMARY_ORDER = (
    "PASS", "OK", "WRONG ORDER", "FAIL", "RACE", "DEADLOCK", "TIMEOUT", "PANIC", "BUILD ERROR"
)
GOOD_VERDICTS = {"PASS", "OK"}


# --- environment -----------------------------------------------------------


def find_go() -> str:
    """Return the path to the `go` binary, or exit with a clear message."""
    go = shutil.which("go")
    if not go:
        sys.exit(
            f"{RED}error:{RESET} the Go toolchain was not found on PATH.\n"
            "Install Go (https://go.dev/dl/) and make sure `go version` works,\n"
            "then re-run this script."
        )
    return go


_ENV_CACHE: dict[str, str] | None = None


def go_env() -> dict[str, str]:
    """Inherited environment + GOTOOLCHAIN=local (no surprise toolchain pulls)."""
    global _ENV_CACHE
    if _ENV_CACHE is None:
        _ENV_CACHE = {**os.environ, "GOTOOLCHAIN": "local"}
    return _ENV_CACHE


# --- README expectations ---------------------------------------------------


def load_readme_notes() -> dict[str, str]:
    """Map `pool_x.go` -> the README table note, for side-by-side context.

    The README mixes 3-column rows (File | Quality | Notes) and 2-column rows
    (File | Bug); both are flattened into one ` · `-joined string.
    """
    notes: dict[str, str] = {}
    if not README.exists():
        return notes
    for line in README.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|") or "pool_" not in line or ".go" not in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells or not cells[0].startswith("pool_"):
            continue
        notes[cells[0].strip("`")] = " · ".join(c for c in cells[1:] if c)
    return notes


# --- external dependency detection -----------------------------------------


def external_imports(src: str) -> list[str]:
    """Return non-stdlib import paths (first path segment contains a dot)."""
    paths: list[str] = []
    for m in re.finditer(r'^\s*import\s+"([^"]+)"', src, re.M):
        paths.append(m.group(1))
    for blk in re.finditer(r"import\s*\(\s*(.*?)\s*\)", src, re.S):
        paths += re.findall(r'"([^"]+)"', blk.group(1))
    return [p for p in paths if "." in p.split("/")[0]]


# --- subprocess helpers ----------------------------------------------------


def run_proc(cmd: list[str], cwd: Path, timeout: int) -> tuple[int, str, str, bool]:
    """Run a command in its own process group; kill the whole group on timeout.

    Returns (returncode, stdout, stderr, killed). stdout carries the driver's
    flow log; stderr carries any panic / deadlock / race report. The new
    session means a deadlocked submission's child is killed too, not orphaned.
    """
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=go_env(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        out, err = proc.communicate(timeout=timeout)
        return proc.returncode, out, err, False
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        out, err = proc.communicate()
        return -1, out or "", err or "", True


def maybe_tidy(go: str, src: str, work: Path) -> str:
    """`go mod tidy` when the submission imports a non-stdlib package."""
    if not external_imports(src):
        return ""
    tidy = subprocess.run(
        [go, "mod", "tidy"],
        cwd=work,
        env=go_env(),
        capture_output=True,
        text=True,
        timeout=BUILD_TIMEOUT,
    )
    return tidy.stdout + tidy.stderr


# --- flow mode -------------------------------------------------------------


def classify_flow(rc: int, text: str, killed: bool) -> tuple[str, str]:
    """Reduce a driver run to a (verdict, one-line detail) pair.

    `text` is stdout + stderr combined. A crash (deadlock / race / panic)
    outranks everything. A clean run is `OK` only if every scenario preserved
    input order; a clean run with any `order preserved: NO` is `WRONG ORDER`.
    """
    if killed:
        return "TIMEOUT", "program never exited — killed after the timeout"
    if "all goroutines are asleep - deadlock" in text:
        return "DEADLOCK", "every goroutine blocked — the Go runtime aborted"
    if "DATA RACE" in text:
        return "RACE", "data race detected by -race"
    panic = re.search(r"^panic:.*$", text, re.M)
    if panic:
        return "PANIC", panic.group(0).strip()
    fatal = re.search(r"^fatal error:.*$", text, re.M)
    if fatal:
        return "PANIC", fatal.group(0).strip()
    if rc == 0:
        if re.search(r"order preserved:\s*NO", text):
            return "WRONG ORDER", "ran cleanly, but output does not match input order"
        return "OK", "ran to completion — output matches input order"
    return "FAIL", f"exited with code {rc}"


def _trim_dump(text: str, limit: int = 12) -> str:
    """Shorten a runtime stack dump / race report for non-verbose output."""
    lines = text.splitlines()
    if len(lines) <= limit:
        return text
    return "\n".join(lines[:limit]) + f"\n… ({len(lines) - limit} more lines — pass --verbose)"


def run_flow_submission(
    go: str,
    submission: Path,
    tmp_root: Path,
    *,
    go_version: str,
    use_race: bool,
    timeout: int,
) -> dict:
    """Build a temp module (driver + submission sub-package) and run it."""
    work = Path(tempfile.mkdtemp(prefix=f"p6flow_{submission.stem}_", dir=tmp_root))
    src = submission.read_text(encoding="utf-8")

    (work / "go.mod").write_text(f"module p6demo\n\ngo {go_version}\n", encoding="utf-8")
    pkg = work / "pool"
    pkg.mkdir()
    (pkg / "pool.go").write_text(src, encoding="utf-8")          # submission, verbatim
    shutil.copyfile(DEMO_MAIN, work / "main.go")                  # the flow driver

    tidy_out = maybe_tidy(go, src, work)

    # Build and run as two steps so the (variable) build time does not eat into
    # the hang-detection timeout for the run.
    build_cmd = [go, "build", "-o", "p6prog"] + (["-race"] if use_race else []) + ["."]
    build = subprocess.run(
        build_cmd, cwd=work, env=go_env(), capture_output=True, text=True, timeout=BUILD_TIMEOUT
    )
    if build.returncode != 0:
        bout = tidy_out + build.stdout + build.stderr
        errs = re.findall(r"^.*\.go:\d+:\d+:.*$", bout, re.M)
        return {
            "file": submission.name,
            "verdict": "BUILD ERROR",
            "detail": errs[0].strip() if errs else "does not compile",
            "output": bout.rstrip(),
            "diag": "",
            "extra": "",
        }

    rc, out, err, killed = run_proc([str(work / "p6prog")], work, timeout)
    verdict, detail = classify_flow(rc, f"{out}\n{err}", killed)
    return {
        "file": submission.name,
        "verdict": verdict,
        "detail": detail,
        "output": out.strip("\n"),   # the driver's flow timeline
        "diag": err.strip("\n"),     # panic / deadlock / race report, if any
        "extra": tidy_out,
    }


def print_flow_result(result: dict, notes: dict[str, str], verbose: bool) -> None:
    verdict = result["verdict"]
    colour = VERDICT_COLOUR.get(verdict, "")
    bar = "─" * max(4, 60 - len(result["file"]))
    print(f"{BOLD}{result['file']}{RESET}  {DIM}── flow {bar}{RESET}")

    note = notes.get(result["file"])
    if note:
        print(f"  {DIM}readme  {note}{RESET}")

    body = result["output"]
    if body:
        for ln in body.splitlines():
            print(f"  {ln}")
    else:
        print(f"  {DIM}(no flow output before the program stopped){RESET}")

    diag = result.get("diag", "")
    if diag and verdict != "OK":
        print(f"  {DIM}── why {'─' * 54}{RESET}")
        shown = diag if verbose else _trim_dump(diag)
        for ln in shown.splitlines():
            print(f"  {DIM}│ {ln}{RESET}")

    print(f"  {colour}{BOLD}status: {verdict}{RESET}  {result['detail']}")
    if verbose and result.get("extra"):
        print(f"  {DIM}[go mod tidy]{RESET}")
        for ln in result["extra"].rstrip().splitlines():
            print(f"  {DIM}│ {ln}{RESET}")
    print()


# --- test mode (go-test harness) -------------------------------------------


def classify_test(rc: int, out: str, runner_killed: bool) -> tuple[str, str]:
    """Reduce a `go test` run to a (verdict, one-line detail) pair."""
    if runner_killed:
        return "TIMEOUT", "go test never returned — killed by run_cases.py"
    if "panic: test timed out" in out or "*** Test killed" in out:
        return "TIMEOUT", "a test never returned — deadlock or hang"
    if "[build failed]" in out or "no required module provides package" in out:
        errs = re.findall(r"^.*\.go:\d+:\d+:.*$", out, re.M)
        missing = re.findall(r"^.*(?:cannot find package|no required module provides).*$", out, re.M)
        detail = "; ".join(e.strip() for e in (errs or missing)[:2]) or "does not compile"
        return "BUILD ERROR", detail
    if "DATA RACE" in out:
        return "RACE", _first_fail_message(out) or "data race detected by -race"
    if rc == 0:
        return "PASS", "all harness checks passed"
    panic = re.search(r"^panic:.*$", out, re.M)
    if panic:
        return "PANIC", panic.group(0).strip()
    return "FAIL", _first_fail_message(out) or "one or more harness checks failed"


def _first_fail_message(out: str) -> str:
    """Pull the first `t.Fatalf/Errorf` message printed by the harness."""
    m = re.search(r"_test\.go:\d+: (.+)", out)
    return m.group(1).strip() if m else ""


def per_test_results(out: str) -> list[tuple[str, str]]:
    """Return [(TestName, PASS|FAIL|SKIP), ...] from `go test -v` output."""
    return [
        (m.group(2), m.group(1))
        for m in re.finditer(r"^\s*--- (PASS|FAIL|SKIP): (\S+)", out, re.M)
    ]


def run_test_submission(
    go: str,
    submission: Path,
    tmp_root: Path,
    *,
    go_version: str,
    use_race: bool,
    timeout: int,
) -> dict:
    """Build a temp module (harness + submission) and run `go test`."""
    work = Path(tempfile.mkdtemp(prefix=f"p6test_{submission.stem}_", dir=tmp_root))
    src = submission.read_text(encoding="utf-8")

    (work / "pool.go").write_text(src, encoding="utf-8")
    shutil.copyfile(HARNESS, work / "pool_test.go")
    (work / "go.mod").write_text(f"module pool\n\ngo {go_version}\n", encoding="utf-8")

    tidy_out = maybe_tidy(go, src, work)

    cmd = [go, "test", "-count=1", "-vet=off", "-run", ".", "-v", f"-timeout={timeout}s"]
    if use_race:
        cmd.insert(2, "-race")

    runner_killed = False
    try:
        proc = subprocess.run(
            cmd, cwd=work, env=go_env(), capture_output=True, text=True,
            timeout=timeout + 150,  # generous margin for the first race build
        )
        rc, out = proc.returncode, proc.stdout + proc.stderr
    except subprocess.TimeoutExpired as exc:
        runner_killed = True
        rc = -1
        out = (exc.stdout or "") + (exc.stderr or "")
        if isinstance(out, bytes):
            out = out.decode(errors="replace")

    out = tidy_out + out
    verdict, detail = classify_test(rc, out, runner_killed)
    return {
        "file": submission.name,
        "verdict": verdict,
        "detail": detail,
        "tests": per_test_results(out),
        "output": out,
    }


def print_test_result(result: dict, notes: dict[str, str], verbose: bool) -> None:
    verdict = result["verdict"]
    colour = VERDICT_COLOUR.get(verdict, "")
    name = result["file"].ljust(14)
    label = f"{colour}{BOLD}{verdict:<11}{RESET}"
    print(f"  {BOLD}{name}{RESET} {label} {result['detail']}")

    tests = result["tests"]
    if tests:
        passed = sum(1 for _, s in tests if s == "PASS")
        failed = [n for n, s in tests if s == "FAIL"]
        line = f"{passed}/{len(tests)} harness tests passed"
        if failed:
            line += f"  ·  failed: {', '.join(failed)}"
        print(f"  {' ' * 14} {DIM}tests   {line}{RESET}")

    note = notes.get(result["file"])
    if note:
        print(f"  {' ' * 14} {DIM}readme  {note}{RESET}")

    if verbose:
        print(f"  {DIM}{'─' * 70}{RESET}")
        for ln in result["output"].rstrip().splitlines():
            print(f"  {DIM}│{RESET} {ln}")
        print(f"  {DIM}{'─' * 70}{RESET}")
    print()


# --- shared ----------------------------------------------------------------


def print_summary(results: list[dict]) -> None:
    counts: dict[str, int] = {}
    for r in results:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    parts = []
    for verdict in SUMMARY_ORDER:
        if counts.get(verdict):
            colour = VERDICT_COLOUR.get(verdict, "")
            parts.append(f"{colour}{counts[verdict]} {verdict}{RESET}")
    print(f"{BOLD}Summary:{RESET} " + "  ·  ".join(parts) + f"   ({len(results)} total)")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--test", action="store_true", help="run the go-test harness instead of the flow runner")
    ap.add_argument("--file", action="append", help="run only this submission (repeatable)")
    ap.add_argument("--verbose", "-v", action="store_true", help="dump raw tool output as well")
    ap.add_argument("--go-version", default="1.21", help="go directive for the generated go.mod (default: 1.21)")
    ap.add_argument("--no-race", action="store_true", help="skip the -race detector")
    ap.add_argument("--timeout", type=int, default=20, help="per-submission run timeout in seconds (default: 20)")
    ap.add_argument("--keep", action="store_true", help="keep the temp modules instead of deleting them")
    args = ap.parse_args()

    flow_mode = not args.test
    template = DEMO_MAIN if flow_mode else HARNESS
    if not template.exists():
        sys.exit(f"{RED}error:{RESET} required file not found: {template}")

    go = find_go()
    go_ver = subprocess.run([go, "version"], capture_output=True, text=True).stdout.strip()

    submissions = sorted(HERE.glob("pool_*.go"))
    if args.file:
        wanted = {f if f.endswith(".go") else f + ".go" for f in args.file}
        submissions = [s for s in submissions if s.name in wanted]
        missing = wanted - {s.name for s in submissions}
        if missing:
            sys.exit(f"{RED}error:{RESET} no such submission(s): {', '.join(sorted(missing))}")
    if not submissions:
        sys.exit(f"{RED}error:{RESET} no pool_*.go submissions found in {HERE}")

    notes = load_readme_notes()
    mode_label = "flow runner" if flow_mode else "go-test harness"

    print(f"{BOLD}Concurrent Worker Pool (P6) — {mode_label}{RESET}")
    print(f"  {DIM}toolchain : {go_ver}{RESET}")
    print(
        f"  {DIM}settings  : go.mod 'go {args.go_version}' · "
        f"race {'off' if args.no_race else 'on'} · timeout {args.timeout}s{RESET}"
    )
    if args.go_version.startswith(("1.1", "1.20", "1.21")):
        print(f"  {DIM}note      : pre-1.22 loop semantics — pool_e1.go reproduces its loop-capture bug{RESET}")
    print(f"  {DIM}{'─' * 70}{RESET}\n")

    run_one = run_flow_submission if flow_mode else run_test_submission
    print_one = print_flow_result if flow_mode else print_test_result

    tmp_root = Path(tempfile.mkdtemp(prefix="p6_run_"))
    results: list[dict] = []
    try:
        for submission in submissions:
            result = run_one(
                go,
                submission,
                tmp_root,
                go_version=args.go_version,
                use_race=not args.no_race,
                timeout=args.timeout,
            )
            results.append(result)
            print_one(result, notes, args.verbose)
            sys.stdout.flush()
    finally:
        if args.keep:
            print(f"{DIM}temp modules kept under {tmp_root}{RESET}")
        else:
            shutil.rmtree(tmp_root, ignore_errors=True)

    print(f"{DIM}{'─' * 70}{RESET}")
    print_summary(results)

    # Non-zero exit if anything is not a clean PASS / OK — handy in CI.
    return 0 if all(r["verdict"] in GOOD_VERDICTS for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
