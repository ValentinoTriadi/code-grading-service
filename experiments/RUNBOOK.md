# Experiment Runbook

Operational guide for running the prompt-engineering experiment on Gemini Batch.

For the **why** (research goals, statistical methodology, factor design, budget) read [`docs/design/experiment-plan.md`](../docs/design/experiment-plan.md). For prompt structure read [`docs/design/prompt-structure.md`](../docs/design/prompt-structure.md). This file is the **how** — what commands to run, in what order, and what to expect.

---

## TL;DR

```bash
# 1. Fill in human_score for every entry in experiments/dataset/submissions.json
# 2. export GEMINI_API_KEY=...
# 3. python -m experiments.runner all
```

Re-run the same command if interrupted — it resumes from `state.json`.

---

## What this experiment does

A **two-phase** comparison of 8 prompt configurations against 144 hand-graded student submissions across 6 problems (sum-array, palindrome-check, lru-cache, dijkstra, BST, worker-pool).

> **Sync with production.** `experiments/prompt.py` is a thin wrapper around `src/engine/prompt_orchestrator.PromptOrchestrator`, so the prompt the experiment grades with is byte-for-byte the prompt the production grading service will send once you set `with_reason` and pick the rubric for the winning scenario. Production's `PromptOrchestrator.build()` returns a `StructuredPrompt(cacheable_prefix, dynamic_suffix)` with the cacheable framing (system + rubric + CoT + few-shot + output-format) ahead of the per-call task section — same split the experiment relies on.

| Phase | What it does | Runs |
|---|---|---:|
| **Phase 1 — accuracy** | Each of 8 scenarios grades each of 144 submissions once. Computes MAE + Pearson per scenario. Picks the best scenario (lowest MAE, Pearson r as tiebreaker) and the worst case (problem with highest avg case-MAE across scenarios). | 1,152 |
| **Phase 2 — consistency** | The winning scenario re-grades the worst-case submissions 7× each. Computes ICC(A,1) with 95% CI on the resulting `n × 7` matrix. | ~140 |
| **Total** | | ~1,292 |

Output: 8 `(MAE, Pearson r)` pairs plus one `ICC(A,1)` for the **(best scenario, worst case)** stress test.

---

## Prerequisites

### 1. Fill in `human_score`

Open `experiments/dataset/submissions.json`. Every entry has `"human_score": null`. Manually grade each submission against the matching problem's `rubric_structured` (in `problems.json`) and write the score (0–100, integer or one decimal).

The runner refuses to start while any `human_score` is null:

```
RuntimeError: 144 submission(s) have human_score=null. Fill in
experiments/dataset/submissions.json before Phase 1.
```

> Score against a single rubric per problem so accuracy comparisons are fair across scenarios. Use the same human grader for all 144 (or document inter-grader reliability separately).

### 2. Pick a Gemini backend — AI Studio (default) **or** Vertex AI

The experiment runs on one of two Google batch backends. Pick one.

**Option A — AI Studio (default).** Simple, no GCP setup; uses inline batch.

```bash
export GEMINI_API_KEY=ya29-...   # or GOOGLE_API_KEY
```

Get one from https://aistudio.google.com/app/apikey.

**Option B — Vertex AI.** Authenticates via Application Default Credentials against a GCP project; uses GCS-backed batch. Required if you can't (or don't want to) manage an AI Studio API key, or you want to keep everything inside one GCP project. Setup, once:

```bash
# 1. Install gcloud + auth
brew install --cask google-cloud-sdk
gcloud auth login
gcloud auth application-default login
gcloud config set project ta-project-492309

# 2. Enable APIs
gcloud services enable aiplatform.googleapis.com storage.googleapis.com \
  --project=ta-project-492309

# 3. Create a regional bucket in the SAME region as your Vertex calls
#    (bucket names are globally unique — adjust if it collides)
gsutil mb -p ta-project-492309 -l asia-southeast1 -b on \
  gs://ta-project-492309-vertex-batch-sg
```

Then before running the experiment:

```bash
export EXPERIMENT_USE_VERTEX=true
export GOOGLE_CLOUD_PROJECT=ta-project-492309
export GOOGLE_CLOUD_LOCATION=asia-southeast1
export EXPERIMENT_GCS_BUCKET=gs://ta-project-492309-vertex-batch-sg
# GEMINI_API_KEY is unused when EXPERIMENT_USE_VERTEX=true.
```

The experiment will upload one `input.jsonl` per scenario to
`gs://<bucket>/phase1-<S?>/input.jsonl`, submit a Vertex Batch job, and
read the results back from `gs://<bucket>/phase1-<S?>/output/`. A
`run_ids.json` sidecar is written alongside each input so responses can be
matched back to cells (Vertex Batch preserves input row order but has no
per-row metadata field).

> **Region tip.** Keep the bucket and `GOOGLE_CLOUD_LOCATION` in the same
> region — cross-region GCS reads add latency and per-GB egress charges.
> Verify model availability in your region:
>
> ```bash
> python -c "from google import genai; print(genai.Client(vertexai=True, project='ta-project-492309', location='asia-southeast1').models.generate_content(model='gemini-2.5-flash', contents='ping').text)"
> ```

### 3. (Optional) Install `pingouin` and `statsmodels` for richer analysis

```bash
pip install pingouin pandas statsmodels
```

| Package | What it unlocks |
|---|---|
| `pingouin` + `pandas` | Proper two-way mixed absolute-agreement 95% CIs for both Phase 1 per-scenario human↔LLM ICC and the Phase 2 ICC. Without it, Phase 1 / Phase 2 fall back to a Fisher-z normal approximation. |
| `statsmodels` | 3-way ANOVA on Phase 1 per-row absolute error with factors {Structured Rubric, CoT, Few-Shot}. Without it, the ANOVA block prints a "skipped" notice — Phase 1 / Phase 2 still complete. |

The thesis numbers should use these libraries; the fallbacks are sanity-check quality only.

---

## Configuration

All via env vars — no code edits needed for tuning.

| Variable | Default | What it does |
|---|---|---|
| `GEMINI_API_KEY` | — | Required in AI Studio mode (Option A). Unused on Vertex. |
| `EXPERIMENT_USE_VERTEX` | `false` | Set `true` to route through Vertex Batch instead of AI Studio Batch. |
| `GOOGLE_CLOUD_PROJECT` | — | Required when `EXPERIMENT_USE_VERTEX=true`. |
| `GOOGLE_CLOUD_LOCATION` | `asia-southeast1` | Vertex region. Must match the GCS bucket region for no egress. |
| `EXPERIMENT_GCS_BUCKET` | — | Required when `EXPERIMENT_USE_VERTEX=true`. `gs://bucket-name` or `gs://bucket/prefix`. |
| `EXPERIMENT_MODEL` | `gemini-2.5-flash` | Use `gemini-2.5-pro` for higher quality (~5× more expensive). |
| `EXPERIMENT_TEMPERATURE` | `0.5` | Must be > 0 or Phase 2 ICC will artificially inflate (no variance). |
| `EXPERIMENT_MAX_OUTPUT_TOKENS` | `2500` | Cap on response length. CoT scenarios use ~1,500 of this. |
| `EXPERIMENT_FEW_SHOT_COUNT` | `2` | How many of the 2 examples in `few_shot.json` to include when few-shot is on. |
| `EXPERIMENT_POLL_INTERVAL` | `60` | Seconds between batch polls. |
| `EXPERIMENT_POLL_TIMEOUT_HOURS` | `24` | Hard cap on a single batch's poll loop. |

---

## Commands

All commands are run from the repo root.

### `status` — see where you are

```bash
python -m experiments.runner status
```

Shows: per-scenario Phase 1 batch state, Phase 1 picker outputs (if computed), Phase 2 batch state, ICC (if computed). Read-only — never makes API calls.

### `phase1` — run / resume Phase 1

```bash
python -m experiments.runner phase1
```

For each of the 8 scenarios:
1. If no batch submitted yet → builds `~144` inline requests, submits a batch, records its resource name in `state.json`.
2. If batch submitted but not done → polls every 60s until `JOB_STATE_SUCCEEDED`.
3. If batch done → fetches responses, parses with `ResponseParser`, appends valid rows to `experiments/results/phase1.jsonl`.

After all 8 scenarios finish, computes per-scenario MAE/Pearson and per-case avg MAE, then picks the **best scenario** and **worst case**, persists them to `state.json`, and prints the Phase 1 table.

### `phase2` — run / resume Phase 2

```bash
python -m experiments.runner phase2
```

Requires Phase 1 complete. Builds ~140 cells for **(best scenario × worst-case submissions × 7 reps)**, submits one batch, polls, fetches, computes ICC(A,1) + 95% CI, prints the Phase 2 summary.

### `all` — phase1 then phase2

```bash
python -m experiments.runner all
```

Runs Phase 1 to completion, then automatically starts Phase 2.

### `reset --yes` — wipe everything

```bash
python -m experiments.runner reset --yes
```

Deletes `state.json`, `phase1.jsonl`, `phase2.jsonl`. **Destructive.** Refuses without `--yes`. Use this only if you want to start the entire experiment over.

---

## Checkpoint / resume — how it works

The Gemini Batch API runs server-side asynchronously. Once you submit, the job lives on Google's infrastructure and runs whether or not your laptop is on. The CLI just records the batch resource names in `state.json`, polls for completion, and fetches results when done.

Two layers of persistence:

1. **`experiments/state.json`** — small JSON tracking each batch's resource name + status:
   ```json
   {
     "phase1": {
       "batches": {
         "S1": {"batch_name": "batches/abc...", "status": "JOB_STATE_RUNNING", "request_count": 144}
       },
       "complete": false,
       "best_scenario_id": null,
       "worst_case_id": null
     },
     "phase2": {...}
   }
   ```

2. **`experiments/results/phase{1,2}.jsonl`** — append-only result rows. Each completed grading is one JSON object on its own line.

### What "interrupted" means in practice

| What happened | What re-running `phase1` does |
|---|---|
| Ctrl-C during submission | Re-submits any scenario without a `batch_name` in `state.json`. |
| Ctrl-C while polling | Re-polls the existing `batch_name` (no resubmit, no extra cost). |
| Network drop / laptop sleep | Same as above. |
| Server-side `JOB_STATE_FAILED` | Logs the error and **skips** that scenario. Manually clear that scenario from `state.json` (or `reset --yes`) to retry. |
| Re-run after success | Detects all rows already in `phase1.jsonl`, marks each batch SUCCEEDED if not already, recomputes metrics, prints the table. Idempotent. |

You can safely close the laptop during a 24-hour batch wait. When you come back, run `status` to see if it's done; if yes, `phase1` again will fetch.

---

## File structure

```
experiments/
├── RUNBOOK.md          ← this file
├── config.py           ← env-driven config
├── scenarios.py        ← 8 prompt configurations (concrete)
├── prompt.py           ← thin wrapper that delegates to src/engine/prompt_orchestrator.PromptOrchestrator
├── metrics.py          ← Pearson, MAE, ICC(A,1) — pure-Python
├── analysis.py         ← per-scenario metrics + pickers, human↔LLM ICC, 3-way ANOVA
├── gemini_batch.py     ← Gemini Batch API wrapper
├── state.py            ← state.json + JSONL append/read
├── runner.py           ← CLI orchestration (this is the entry point)
│
├── dataset/
│   ├── problems.json     ← 6 problems × {description, structured rubric, unstructured rubric}
│   ├── submissions.json  ← 144 submissions × {code, human_score}  ← FILL IN human_score
│   └── few_shot.json     ← 2 Two-Sum examples (independent from dataset)
│
├── results/              ← append-only outputs (gitignored output area)
│   ├── phase1.jsonl
│   └── phase2.jsonl
│
└── state.json            ← checkpoint state (created on first run)
```

---

## Reading the results

### Phase 1 console output

```
============================================================================================
PHASE 1 — accuracy
============================================================================================
scenario      n      MAE   MAE/100   Pearson   ICC(A,1)  ICC 95% CI
--------------------------------------------------------------------------------------------
S1          144    8.512    0.0851     0.819      0.802  [0.738, 0.853]
S2          144    8.187    0.0819     0.834      0.821  [0.760, 0.868]
...
S5          144    2.505    0.0251     0.983      0.978  [0.969, 0.984]   <-- best
...

case          avg MAE
--------------------------------------------------------------------------------------------
P1              8.467
...
P5              8.533  <-- worst
============================================================================================

==============================================================================
PHASE 1 — 3-way ANOVA on |human − LLM|  (n=1152)
==============================================================================
source                             sum_sq      df         F         p
------------------------------------------------------------------------------
C(rubric)                         123.456       1    12.345    0.0005
C(cot)                             45.678       1     4.567    0.0331
C(fewshot)                         89.012       1     8.901    0.0029
C(rubric):C(cot)                   12.345       1     1.234    0.2670
...
Residual                         1234.567    1144         —         —
==============================================================================
```

**Reading the table:**
- `MAE` is on the 0–100 score scale; `MAE/100` is the normalized 0–1 figure expected by the thesis brief.
- `Pearson` is rank-pattern correlation; `ICC(A,1)` is two-way mixed absolute-agreement between human and LLM as two raters across the 144 submissions — a stricter accuracy view that penalizes both miscalibration and ranking errors.
- The ANOVA attributes the spread of per-row absolute errors to the three binary factors and their interactions. Significant `C(rubric)` etc. means that factor genuinely shifts accuracy; significant interactions mean factors don't act independently.

### Phase 2 console output

```
======================================================================
PHASE 2 — consistency (winner stress test)
======================================================================
scenario     : S5
worst case   : P5
matrix       : n=23 submissions × k=7 replicates
ICC(A,1)     : 0.892  (95% CI 0.812 … 0.946)
interpretation : good  (Koo & Li 2016)
======================================================================
```

ICC interpretation thresholds (Koo & Li 2016):
- `< 0.5` poor
- `0.5 – 0.75` moderate
- `0.75 – 0.9` good
- `≥ 0.9` excellent

### Per-row JSONL schema

Each row in `phase1.jsonl` / `phase2.jsonl`:

```json
{
  "run_id": "P1-S5-sum_array_a1-r0",
  "phase": 1,
  "scenario_id": "S5",
  "problem_id": "P1",
  "submission_id": "sum_array_a1",
  "replicate": 0,
  "score": 75.0,
  "criterion_scores": [
    {"name": "Correctness", "score": 50, "max_score": 50},
    {"name": "Readability", "score": 15, "max_score": 25},
    {"name": "Efficiency", "score": 10, "max_score": 25}
  ],
  "raw_response": "<THINKING>...</THINKING>\n<RESULT>...</RESULT>",
  "tokens_in": 1672,
  "tokens_out": 1421,
  "cached_tokens": 0,
  "schema_valid": true,
  "error": null
}
```

For thesis analysis, load these JSONLs into pandas:

```python
import pandas as pd
phase1 = pd.read_json("experiments/results/phase1.jsonl", lines=True)
phase2 = pd.read_json("experiments/results/phase2.jsonl", lines=True)
```

---

## Troubleshooting

### `RuntimeError: ... human_score=null`

You haven't graded all submissions. Open `submissions.json` and fill in every `"human_score": null`.

### `RuntimeError: Set GEMINI_API_KEY ...`

`export GEMINI_API_KEY=...` before running.

### `JOB_STATE_FAILED` on a batch

Check the error in `state.json`. Common causes:
- Token-per-request limit exceeded → some submission is too long. Inspect `submissions.json`.
- Quota exceeded → check Google AI Studio dashboard.
- Model deprecated → set `EXPERIMENT_MODEL` to a current model.

To retry: open `state.json`, delete the offending scenario from `phase1.batches` (or the whole `phase2.batch` block), then re-run.

### `ResponseParser: ... non valid JSON ...`

Means the model produced text that didn't parse into the `<RESULT>` schema. Those rows have `schema_valid: false` and are excluded from MAE/Pearson/ICC. Check the rate via:

```bash
jq -s 'group_by(.scenario_id) | map({scenario: .[0].scenario_id, total: length, valid: map(select(.schema_valid)) | length})' experiments/results/phase1.jsonl
```

If the rate is high (>10%), tighten the output-format header in the prompt or switch to a stronger model.

### Want to retry just one scenario

Edit `state.json`, remove that scenario's entry from `phase1.batches`, then run `phase1` again. The runner detects the gap, builds a new batch for it, and merges with the existing JSONL.

### Lost `state.json` but `phase1.jsonl` still exists

Re-running `phase1` will see all rows already in the JSONL, mark the batches SUCCEEDED automatically, and recompute the picker outputs. State will reconstruct itself.

---

## Cost expectations

With Gemini Batch API discount (50% off, no caching yet):

| Model | List | After batch |
|---|---:|---:|
| Gemini 2.5 Flash-Lite | $0.80 | **~$0.40** |
| Gemini 2.5 Flash | $4 | **~$2** |
| Gemini 2.5 Pro | $10 | **~$5** |

Run `EXPERIMENT_MODEL=gemini-2.5-pro` for thesis quality, `gemini-2.5-flash` for development pilots.

---

## Going further

- **Pilot first.** Set `EXPERIMENT_MODEL=gemini-2.5-flash-lite` and run on a 5-submission subset first to verify the pipeline. Edit `submissions.json` to keep only 5 entries, run, then restore the full dataset.
- **Add prompt caching** for ~60% additional savings. `gemini_batch.py` has a TODO marker — wire `client.caches.create` per `(scenario, problem)`, attach `cached_content` to each `InlinedRequest.config`. Worth ~$3 on a Pro run.
- **3-way ANOVA** on the Phase 1 metrics with factors `{Structured Rubric, CoT, Few-Shot}` — see `experiment-plan.md` § Selection criterion. Compute it from `phase1.jsonl` in your analysis notebook.
