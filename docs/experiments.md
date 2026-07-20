# `experiments/` Architecture

This document summarizes the experiment harness — a standalone CLI toolset that measures
which LLM-grading prompt configuration is most accurate and consistent, using the
production `src/engine/prompt_orchestrator.PromptOrchestrator` so the winning prompt is
byte-for-byte what production would send.

## What it measures

An 8-way factorial comparison of three binary prompting factors — **structured rubric**,
**chain-of-thought**, **few-shot examples** — against 144 hand-graded student submissions
across 6 problems, run in two phases:

| Phase | Question | Method |
|---|---|---|
| **Phase 1 — accuracy** | Which of the 8 scenarios grades most like a human? | Each scenario grades all 144 submissions once; compute MAE + Pearson r per scenario; pick the best scenario and the hardest ("worst") problem case |
| **Phase 2 — consistency** | Does the winning scenario reproduce its own scores? | The best scenario re-grades the worst-case submissions 7× each at temperature > 0; compute ICC(A,1) on the resulting n×7 matrix |

## Directory map

```
experiments/
├── runner.py            CLI entry point — orchestrates both phases, checkpointing
├── scenarios.py          The 8 concrete Scenario definitions (factorial design)
├── config.py              Env-driven config (model, temperature, batch vs. direct, Vertex vs. AI Studio)
├── prompt.py               Thin wrapper delegating prompt assembly to src/engine/prompt_orchestrator
├── metrics.py               Pure-Python Pearson, MAE, ICC(A,1)
├── analysis.py                Per-scenario metrics, composite scenario picker, 3-way ANOVA, report formatting
├── gemini_batch.py              Gemini Batch API client (AI Studio + Vertex AI backends)
├── state.py                       state.json + JSONL append/read (checkpoint persistence)
├── sanity_grade.py                 One-off ad-hoc sanity check against the live production service
├── RUNBOOK.md                        Operator's how-to guide (setup, commands, troubleshooting, cost)
├── grading/
│   ├── rubric.py         Parses a problem's rubric_structured string into typed Criterion objects
│   ├── cli.py              Interactive terminal UI for entering human_score on submissions.json
│   ├── worksheet.py          Generates printable/offline Markdown grading worksheets
│   └── sanity.py               Structural sanity checks on submissions.json (no LLM calls)
├── dataset/
│   ├── problems.json      6 problems × {description, structured rubric, unstructured rubric}
│   ├── submissions.json    144 submissions × {code, human_score, human_score_breakdown}
│   └── few_shot.json         Worked examples used by few-shot scenarios
├── results/               phase1.jsonl, phase2.jsonl, summary.txt (gitignored raw dumps; summary.txt tracked)
└── state.json            Checkpoint: batch resource names/status + Phase 1 picker outputs
```

## The 8 scenarios (`scenarios.py`)

Full factorial of three binary factors:

| ID | Label | Structured rubric | CoT | Few-shot |
|---|---|:---:|:---:|:---:|
| S1 | baseline | – | – | – |
| S2 | rubric-only | ✓ | – | – |
| S3 | cot-only | – | ✓ | – |
| S4 | fewshot-only | – | – | ✓ |
| S5 | rubric+cot | ✓ | ✓ | – |
| S6 | rubric+fewshot | ✓ | – | ✓ |
| S7 | cot+fewshot | – | ✓ | ✓ |
| S8 | all-on | ✓ | ✓ | ✓ |

## Prompt parity with production (`prompt.py`)

`experiments/prompt.py` is a thin wrapper — it builds a `GradingRequest` from a scenario's
flags and the dataset, then hands off entirely to the same `PromptOrchestrator` used by
`src/services/grading_service.py`. There is no experiment-specific prompt logic: the same
`StructuredPrompt(cacheable_prefix, dynamic_suffix)` split production uses is what the
harness sends to Gemini. This means the "winning" scenario's config (rubric on/off,
`with_reason`, few-shot examples) can be applied to production directly with no risk of
prompt drift between what was measured and what ships.

## Runner orchestration (`runner.py`)

### Cell model

Every individual grading call is a `Cell` (scenario, problem, submission, replicate,
rendered prompt, max tokens). Phase 1 builds one cell per (scenario × submission) —
~8 × 144 = 1,152 cells. Phase 2 builds one cell per (winning scenario × worst-case
submission × 7 replicates) — ~140 cells.

### Two-pass batch submission (Phase 1)

Phase 1 submits all 8 scenario batches up-front (pass 1), then polls/fetches each in
sequence (pass 2). Because Gemini Batch jobs run concurrently server-side once submitted,
this makes wall time roughly `submit_time + max(batch_duration)` instead of
`sum(submit_time + batch_duration)` — close to an 8× speedup over submitting and waiting
for one scenario at a time.

### Checkpoint / resume

Two persistence layers make the whole run interruption-safe:

- **`state.json`** — tracks each scenario's Gemini batch resource name + status
  (`PENDING`/`RUNNING`/`SUCCEEDED`/`FAILED`), plus Phase 1's picker outputs
  (`best_scenario_id`, `worst_case_id`, computed metrics) once available.
- **`results/phase{1,2}.jsonl`** — append-only result rows, one JSON object per completed
  grading call.

Re-running the same CLI command is always safe: batches already submitted are re-fetched
by resource name rather than resubmitted, and `run_id`s already present in the JSONL are
skipped. A batch job itself lives on Google's infrastructure once submitted, so a laptop
sleeping or losing network mid-poll doesn't lose work. To wipe this state cleanly between
runs, use `runner.py reset --yes` (not `rm`) so `state.json` and both JSONLs are cleared
consistently.

### Response validation

Each response is parsed with the production `ResponseParser`. A row is `schema_valid` only
if `feedback_detail` parses; otherwise `_detect_schema_error` classifies the failure
(`missing_result_block`, `unterminated_result_block`, `invalid_result_json`) and
distinguishes truncation (hit `max_output_tokens`) from a genuine malformed response via
`truncated_output:` prefixing. `runner.py reprocess` can retroactively re-annotate an
existing JSONL if the classification logic changes after the fact.

### Vertex AI vs. AI Studio (`gemini_batch.py`)

Two Gemini Batch backends, selected by `EXPERIMENT_USE_VERTEX`:

- **AI Studio (default)** — inline batch requests/responses over the API, no GCS needed.
- **Vertex AI** — requests are uploaded to GCS as JSONL, processed asynchronously, and
  results streamed back from a GCS output prefix. Because Vertex Batch doesn't preserve
  input/output row order or expose a metadata field, output rows are matched back to
  `run_id`s by hashing each request's prompt text and popping from a per-hash queue
  recorded in a sidecar file at submit time (duplicate prompts, e.g. Phase 2's 7 identical
  replicates per submission, are handled via per-hash FIFO ordering).

Both backends also support a non-batch **direct mode** (`EXPERIMENT_USE_BATCH=false`) that
calls `generate_content` concurrently via a thread pool — useful for quick pilots or when
per-request latency stats are wanted (batch mode has no per-row timing).

## Metrics (`metrics.py`, `analysis.py`)

- **MAE** and **Pearson r** — straightforward implementations over (human, LLM) score
  pairs.
- **ICC(A,1)** — Two-Way Mixed, Absolute Agreement, single rater — implemented from
  scratch in pure Python as the canonical result; `pingouin` is used opportunistically for
  a proper 95% CI (falls back to a Fisher-z normal approximation if not installed).
- **3-way ANOVA** — on per-row `|human − LLM|`, with `rubric`, `cot`, `fewshot` as factors
  (`statsmodels`, optional — skipped with a notice if not installed). Reports partial η²
  per source alongside significance, and `format_phase1_anova`/`_summarize_anova` render a
  human-readable significance/effect-size table plus a one-line "key finding".

### Scenario picker — composite score

`pick_best_scenario` doesn't just take the lowest MAE. It applies a two-tier rule
(`composite_score` in `analysis.py`):

1. **Parse-rate deployability gate** — a scenario whose schema-valid rate falls below
   `PARSE_RATE_FLOOR` (90%) is disqualified regardless of accuracy, since a prompt that
   fails to parse >10% of the time isn't operationally usable in production.
2. **Among survivors**, scenarios are ranked by a z-scored weighted sum:
   `2×z(MAE) + 1×z(1−Pearson)` — MAE counts twice as much as Pearson because absolute
   grading error is the primary accuracy signal and Pearson is a secondary ordering check.

`pick_worst_case` separately finds the problem with the highest average MAE across all 8
scenarios — this becomes the stress-test target for Phase 2, on the theory that the
hardest case for accuracy is also the most informative case for a consistency check.

## Human grading tools (`grading/`)

A separate mini-toolkit for producing the `human_score` ground truth that Phase 1
validates against — entirely decoupled from the LLM pipeline:

- **`rubric.py`** — parses a problem's free-text `rubric_structured` field (e.g.
  `"1. Correctness (60%): ..."`) into typed `Criterion(name, max_score, description)`
  objects, validating that weights sum to 100.
- **`cli.py`** — a full-screen terminal grader: renders problem + rubric + code, prompts
  for a score per criterion via raw single-keypress input, supports navigating
  backward/forward to re-edit already-graded submissions, and writes
  `human_score`/`human_score_breakdown`/`human_score_notes` back into `submissions.json`
  after every accepted entry (so a crash loses at most one in-progress submission).
- **`worksheet.py`** — generates offline Markdown worksheets (one per problem, with a
  scoring table and every submission's code) for grading away from a terminal, to be
  transcribed back via the CLI grader afterward.
- **`sanity.py`** — pure structural validation of `submissions.json` with no LLM calls:
  missing scores, out-of-range scores, breakdown/rubric mismatches, identical code with
  divergent scores, and per-problem outlier detection (z-score threshold) — meant to catch
  fatigue-driven mistakes after a long grading session.

## Configuration (`config.py`)

All tunable via env vars, no code edits required for a re-run:

| Variable | Default | Purpose |
|---|---|---|
| `EXPERIMENT_MODEL` | `gemini-2.5-flash` | Model under test |
| `EXPERIMENT_TEMPERATURE` | `0.5` | Must be > 0 or Phase 2 ICC is trivially 1.0 (deterministic sampling has no variance to measure) |
| `EXPERIMENT_MAX_OUTPUT_TOKENS(_COT)` | `2500` | Output token cap; CoT scenarios can override separately |
| `EXPERIMENT_USE_BATCH` | `true` | Batch API vs. direct concurrent calls |
| `EXPERIMENT_USE_VERTEX` | `false` | Vertex AI (ADC + GCS) vs. AI Studio (API key) |
| `EXPERIMENT_FEW_SHOT_COUNT` | `2` | How many few-shot examples to inject when enabled |
| `EXPERIMENT_DIRECT_CONCURRENCY` | `6` | Thread pool size for direct mode |
| `EXPERIMENT_POLL_INTERVAL` / `_TIMEOUT_HOURS` | `60` / `24` | Batch polling cadence and hard timeout |

## CLI surface (`runner.py`)

```
python -m experiments.runner status              # read-only: show batch/phase state
python -m experiments.runner phase1               # run/resume Phase 1 (idempotent)
python -m experiments.runner phase2                # run/resume Phase 2 (requires phase1 complete)
python -m experiments.runner all                    # phase1 then phase2, writes results/summary.txt
python -m experiments.runner summary                 # reprint summary from already-complete state
python -m experiments.runner reprocess [--phase] [--in-place]  # re-annotate schema errors in existing JSONL
python -m experiments.runner reset --yes               # delete state.json + both JSONLs (destructive)
```

## Notable design choices

- **Byte-identical prompts with production** — the entire point of routing through
  `PromptOrchestrator` instead of hand-rolling experiment prompts is that the accuracy
  numbers measured here transfer directly to production behavior with the winning
  scenario's config, with zero risk of the experiment quietly testing a different prompt
  than what ships.
- **Deployability is part of the ranking, not an afterthought** — the parse-rate floor in
  `composite_score` encodes that an inaccurate-but-parseable prompt can beat an
  accurate-but-flaky one, matching what actually matters for a production service.
- **Everything is resumable by construction** — because Gemini Batch jobs run
  server-side, the CLI's job is reduced to bookkeeping (`state.json`) plus idempotent
  re-fetching; this is why long 24h-SLA batches are safe to run unattended and pick back
  up after any interruption.
- **Sampling temperature is recorded per result row**, not just read from the current env,
  so a Phase 2 summary regenerated later from old data reflects the temperature that data
  was actually collected under — relevant since temp=0 makes the consistency ICC a
  meaningless 1.0 (no sampling variance to measure).
