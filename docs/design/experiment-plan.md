# Prompt Experimentation Plan

A full-factorial experiment to find the prompt-engineering combination that maximizes **agreement with human graders (Kesesuaian)** and **run-to-run reliability (Konsistensi)**.

## Goals

1. Identify the prompt configuration that produces the **highest accuracy** (alignment with human scores) and **highest consistency** (stable scores across repeated runs).
2. Measure the **isolated effect** of each feature (Structured Rubric, Chain of Thought, Few-Shot) and their interactions.
3. Confirm that the chosen configuration generalizes across problems of varying complexity.

## Factors (independent variables)

Three binary factors, all toggleable from the prompt request:

| Factor | Off (✘) | On (✓) |
|---|---|---|
| **Structured Rubric** | Free-form rubric paragraph, no explicit weights or numbered criteria | Numbered criteria with explicit weights (e.g., `1. Correctness (50%): ...`) |
| **Chain of Thought** | `with_reason=False` — model goes straight to `<RESULT>` | `with_reason=True` — model emits `<THINKING>` before `<RESULT>` |
| **Few-Shot** | `few_shot_examples=None` | A fixed pool of worked examples |

## Scenarios (full factorial — 2³ = 8)

| # | Structured Rubric | Chain of Thought | Few-Shot | Short label |
|---|:-:|:-:|:-:|---|
| S1 | ✘ | ✘ | ✘ | baseline |
| S2 | ✓ | ✘ | ✘ | rubric-only |
| S3 | ✘ | ✓ | ✘ | cot-only |
| S4 | ✘ | ✘ | ✓ | fewshot-only |
| S5 | ✓ | ✓ | ✘ | rubric+cot |
| S6 | ✓ | ✘ | ✓ | rubric+fewshot |
| S7 | ✘ | ✓ | ✓ | cot+fewshot |
| S8 | ✓ | ✓ | ✓ | all-on |

## Data (Eksperimen)

The dataset is built directly from `tests/test-case/<problem>/`, with one programming language per problem and hand-graded reference scores so accuracy can be measured.

- **6 problems** spanning three difficulty tiers: 2 easy + 2 medium + 2 hard.
- **20–28 student submissions per problem**, all written in a single programming language **per problem** (language differs across problems, but is fixed within a problem).
- Submissions cover the natural diversity of **correctness, quality, and readability** (groups A–I in each problem's `README.md` walk through clean implementations, alternative approaches, logic bugs, edge-case bugs, and compile/syntax errors) so all rubric criteria are exercised.
- **Each submission is graded manually by a human** against the same rubric, producing a reference score `y_i` per submission.

| Tier   | Problems                                 | Languages         | Submissions per problem | Total |
|---|---|---|---|---|
| Easy   | sum-array, palindrome-check              | Python, Java      | 28, 20 | 48  |
| Medium | lru-cache, dijkstra-shortest-path        | TypeScript, C++   | 25, 25 | 50  |
| Hard   | binary-search-tree, concurrent-worker-pool | Java, Go        | 23, 23 | 46  |
| **Total** | **6** | — | — | **144** |

> Freeze the dataset before any runs start. Storage layout under `experiments/`:
> - `experiments/dataset/problems.json` — 6 entries with `problem_id`, `difficulty`, `language`, `description`, `rubric_structured`, `rubric_unstructured`, plus a `source_dir` pointer back to `tests/test-case/<problem>/`.
> - `experiments/dataset/submissions.json` — 144 entries built by walking each problem directory; each entry carries `submission_id` (= source filename stem), `problem_id`, `language`, `source_file`, `code`, and `human_score` (initially `null` — fill in before running).
> - `experiments/dataset/few_shot.json` — independent few-shot example pool (problem / code / grading), drawn from a different problem (Two-Sum) so it never overlaps with the dataset.

## Two-phase design

The experiment is split into an **accuracy phase** and a **consistency phase** so we don't pay for 7 replicates on every cell.

### Phase 1 — Accuracy (1 rep per cell, all cells)

Every scenario is run **once** against every submission across all 6 cases.

| Quantity | Count |
|---|---|
| Scenarios | 8 |
| Cases (problems) | 6 |
| Submissions (varies per problem) | 144 (28 + 20 + 25 + 25 + 23 + 23) |
| Replicates per cell | 1 |
| **Phase 1 invocations** | **8 × 144 × 1 = 1,152** |

Phase 1 yields per-scenario MAE and Pearson over all 144 submissions per scenario — i.e., 8 MAE values, 8 Pearson values, one accuracy score per scenario.

### Phase 2 — Consistency (winner stress test)

After Phase 1, pick **two** things:

1. The **best scenario** — the one with the **lowest MAE** across all 144 submissions, with **highest Pearson r as tiebreaker**. From the 8 (MAE, Pearson) pairs.
2. The **worst case** — the problem with the **highest average case-level MAE across all 8 scenarios**. From the 6 averaged-over-scenarios MAEs.

Phase 2 then re-grades only the **(best scenario, worst case)** pair **7 times** per submission, producing one ICC(A,1) on an `n × 7` matrix where `n` is the worst case's submission count (20–28). This is a deliberate stress test: if the most accurate prompt holds up on the hardest problem, we have high confidence it's reliable.

| Quantity | Count |
|---|---|
| Scenarios | 1 (the Phase 1 winner) |
| Cases | 1 (the highest-avg-MAE problem) |
| Submissions in that case | 20–28 |
| Replicates per submission | 7 |
| **Phase 2 invocations** | **1 × ~20 × 7 ≈ 140** |

We deliberately do not repeat Phase 2 on the other 7 scenarios or the other 5 cases. Phase 1's accuracy ranking is enough to deselect the other scenarios, and the worst case is the only one where consistency variance is most likely to surface — easier cases tend to score near the ceiling for any prompt and produce inflated ICCs.

### Total

| Phase | Runs |
|---|---:|
| Phase 1 (accuracy) | 1,152 |
| Phase 2 (consistency) | ~140 |
| **Total** | **~1,292** |

Versus a balanced 7-rep design (8 × 144 × 7 = 8,064), the two-phase plan saves ~84% of invocations while keeping both Pearson/MAE and ICC(A,1) statistically well-defined.

## Metrics

Two reporting axes: **Accuracy (Kesesuaian)** vs human scores, and **Consistency (Konsistensi)** across the 7 replicates.

### Per run, capture

- Final `score` (0–100), per-criterion `score` / `max_score`
- `summary`, `comment`, `suggestions`
- Latency (ms), tokens in / out
- `<THINKING>` text (if present)
- Raw response (audit)
- `schema_valid` flag

### Accuracy (Kesesuaian)

In Phase 1, every submission is graded **once** by every scenario (1 replicate). For each scenario, the LLM score `ŷ_i` for submission `i` is therefore that single grading. Phase 1 accuracy compares these `(y_i, ŷ_i)` pairs over all 144 submissions per scenario.

> Note: in Phase 2 the winning scenario is re-run 7 times on the worst case only. For *that scenario, on that case*, you may also report the 7-rep mean against `y_i` as a cross-check on Phase 1's single-rep accuracy.

#### Pearson correlation — `r_xy`

How well the LLM's scoring *pattern* tracks the human's. Range `-1 ≤ r ≤ 1`. Higher = better.

```
        n·Σxy − (Σx)(Σy)
r_xy = ────────────────────────────────────────
       √[ n·Σx² − (Σx)² ] · √[ n·Σy² − (Σy)² ]
```

Where `x` = human scores, `y` = system scores, `n` = number of submissions.

#### Mean Absolute Error — MAE

How far apart the absolute scores are. Lower = better.

```
        Σ |y_i − ŷ_i|
MAE = ─────────────────
             n
```

Scale note: scores are 0–100, so raw MAE will be 0–100. Report **both raw MAE and normalized MAE = raw / 100** so the `0 ≤ MAE ≤ 1` convention from the brief is satisfied.

#### Reporting granularity for accuracy

- **Aggregate per scenario** — Pearson and MAE over all 144 submissions. **This is the headline accuracy number — 8 values total, one per scenario.** The Phase 2 winning scenario is selected from this ranking (lowest MAE, Pearson tiebreaker).
- **Per case** — 8 × 6 = 48 case-level MAE numbers; for each problem, the average across the 8 scenarios is also reported. **The case with the highest average MAE is the Phase 2 worst case.**
- **Per difficulty tier** (easy / medium / hard) — optional diagnostic, not part of the headline.

### Consistency (Konsistensi) — ICC(A,1)

Repeat the same scenario on the same submission 7 times and measure how stable the score is. The brief specifies **Two-Way Mixed, Absolute Agreement, single-rater intrarater reliability** — written **ICC(A,1)**. This is the right form because the "rater" (a fixed prompt configuration) is a constant being measured at multiple times against the same objects (submissions), and absolute-agreement is more demanding than consistency-only (which would ignore systematic shifts between runs).

#### Data layout for one scenario

| Submission | Run 1 | Run 2 | ... | Run k |
|---|---|---|---|---|
| M₁  | x₁₁ | x₁₂ | ... | x₁ₖ |
| M₂  | x₂₁ | x₂₂ | ... | x₂ₖ |
| ... | ... | ... | ... | ... |
| Mₙ  | xₙ₁ | xₙ₂ | ... | xₙₖ |

With `n` = number of submissions in the worst case (20–28), `k` = 7 replicates.

#### Computation

1. **Grand mean**
   ```
   x̄_grand = (Σ all values) / (n · k)
   ```

2. **Row means** (per submission)
   ```
   x̄_i = (Σ values in row i) / k
   ```

3. **Column means** (per run)
   ```
   x̄_j = (Σ values in column j) / n
   ```

4. **Sums of squares**
   ```
   SS_rows  = k · Σᵢ (x̄_i − x̄_grand)²
   SS_cols  = n · Σⱼ (x̄_j − x̄_grand)²
   SS_total = Σᵢⱼ (x_ij − x̄_grand)²
   SS_error = SS_total − SS_rows − SS_cols
   ```

5. **Mean squares**
   ```
   MS_BS = SS_rows  / (n − 1)
   MS_BM = SS_cols  / (k − 1)
   MS_E  = SS_error / [(n − 1)(k − 1)]
   ```

6. **ICC(A,1)**
   ```
                          MS_BS − MS_E
   ICC(A,1) = ─────────────────────────────────────────────────────
              MS_BS + (k − 1)·MS_E + (k / n)·(MS_BM − MS_E)
   ```

Conventional thresholds (Koo & Li, 2016): `< 0.5` poor, `0.5–0.75` moderate, `0.75–0.9` good, `≥ 0.9` excellent.

#### Reporting granularity for consistency

- **Headline** — one ICC(A,1) for the **(best scenario, worst case)** pair, computed on a single `n × 7` matrix where `n` is the worst case's submission count (20–28). **This is the headline consistency number — a stress test of the deployed configuration on the hardest problem.**
- Report the 95% CI alongside the point estimate; with `n ≈ 20` and `k = 7` the CI half-width is typically ±0.10–0.15, so the headline should be read together with that interval.
- We deliberately do **not** compute ICC for the other 7 scenarios or the other 5 cases — that would require running 7 reps on every cell (back to the 8,064-run baseline). The worst-case stress test is the most discriminating cell, so an acceptable ICC there is strong evidence of overall consistency.

> Use a vetted library (`pingouin.intraclass_corr` in Python, `irr::icc` in R) instead of hand-rolling the formula — they also produce 95% CIs, which the writeup should include.

### Operational metrics (per scenario)

- **Schema validity rate** — fraction of invocations that yielded parseable `<RESULT>` JSON. Failures count as a metric, not noise.
- **Mean latency** (ms) and **mean output tokens**.
- **Total cost** (tokens × pricing).

## Selection criterion

Phase 1 selects the deploy candidate by **lowest MAE**, with **highest Pearson r** as tiebreaker. Phase 1 also identifies the worst case — the problem with the **highest average case-level MAE across all 8 scenarios**. Phase 2 then stress-tests the winner on that worst case.

Final reporting:
- For all 8 scenarios — the pair `(Pearson r, MAE)` from Phase 1, plus per-difficulty breakdowns.
- For each of the 6 cases — the average case-level MAE across scenarios, identifying which problem is hardest.
- For the **(winning scenario, worst case)** pair only — `(Pearson r, MAE, ICC(A,1))` with 95% CI. This is the headline.

If Phase 2 reveals poor consistency (`ICC < 0.75` by the Koo & Li thresholds), surface this as a finding — it means the most accurate prompt is *not* the most reliable one on the hardest case, and the deployment decision needs to weigh the trade-off.

Optional add-on: 3-way ANOVA on the Phase 1 MAE and Pearson with factors {Structured Rubric, CoT, Few-Shot} to attribute the headline accuracy effect to specific features and detect interactions.

## Procedure

1. **Build the dataset**: 6 problems (2 easy / 2 medium / 2 hard), 20–28 submissions each, single language per problem, hand-graded by a human against the same rubric the LLM will see. The dataset is built directly from `tests/test-case/<problem>/` and frozen under `experiments/dataset/{problems,submissions,few_shot}.json` with stable IDs (`submission_id` is the source filename stem).
2. **Author both rubric forms per problem**: a Structured rubric (numbered, weighted criteria) and an Unstructured rubric (free-form paragraph) that cover identical content.
3. **Author the few-shot example pool**: independent from the dataset; never use an experiment submission as its own example.
4. **Pin model + sampling settings**: same model, temperature (> 0; suggest 0.3–0.7), top_p, etc. across all ~1,292 runs. Record in the run log.
5. **Wire prompt caching**: refactor `PromptOrchestrator.build()` to return `(cacheable_prefix, dynamic_suffix)` and have the chosen provider client mark the prefix as cacheable (see `cost-optimization.md`). Verify cache hits in the logs before scaling up.
6. **Wire batch submission**: implement a JSONL writer that turns each `(scenario, submission, replicate)` cell into one batch request, plus a poller that fetches the completed batch and merges results into the run log.

### Phase 1 — accuracy (1,152 runs)

7. **Build Phase 1 batch**: 8 scenarios × 144 submissions × 1 rep. Randomize the run order so API / time-of-day drift is spread evenly across scenarios. Submit as one batch (or 8 per-scenario batches for atomic failure isolation).
8. **Wait for the batch to complete**, ingest results into the run log. Each invocation is independent — no response reuse.
9. **Compute accuracy per scenario**: Pearson r and MAE over the 144 (human, LLM) score pairs → 8 MAE + 8 Pearson values.
10. **Compute case-level MAE per scenario**: 8 × 6 = 48 case-level MAE numbers, then average across the 8 scenarios for each case → 6 averaged MAEs.
11. **Pick the Phase 2 winner (scenario)**: rank the 8 scenarios on `(MAE asc, Pearson r desc)` → the scenario with the **lowest MAE** (Pearson r as tiebreaker) is the winner.
12. **Pick the Phase 2 worst case (problem)**: from the 6 averaged case-level MAEs, take the problem with the **highest** average MAE.

### Phase 2 — consistency (~140 runs)

13. **Build Phase 2 batch**: 1 winning scenario × ~20 submissions of the worst case × 7 reps. Randomize run order and submit as one batch.
14. **Wait, ingest, and compute ICC(A,1)** for the (winner, worst case) pair on the resulting `n × 7` matrix, with 95% CI.

### Common

15. **Logging schema (one row per invocation)**:
    `run_id, phase, batch_id, scenario, problem_id, submission_id, difficulty, language, replicate, structured_rubric, cot, few_shot, score, criterion_scores_json, human_score, latency_ms, tokens_in, tokens_out, cached_tokens, schema_valid, raw_response_path`.
    The `cached_tokens` column lets you verify cache hits are actually happening; it should approach 70–80% of `tokens_in` once the batch is past the first call of each scenario.
16. **Failure handling**: retry schema-invalid responses up to 2× and log every attempt. Never silently drop. For batch failures, resubmit only the failed rows.
17. **Analysis**:
    - Build a final per-scenario table with `(scenario, MAE, Pearson)` from Phase 1.
    - Add a single row for the **(winner, worst case)** with `ICC(A,1)` and 95% CI from Phase 2.
    - Plot the 8 scenarios on the (MAE, Pearson) plane and mark the winner; report the winner's stress-test ICC alongside.
    - Optionally run a 3-way ANOVA on each Phase 1 metric to attribute effects to {Structured Rubric, CoT, Few-Shot}.

## Budget estimation

### Token estimates per run

Derived from the actual prompt content (`src/prompts/templates/*.txt` and `_OUTPUT_FORMAT_*` in `src/engine/prompt_orchestrator.py`), using the heuristic 1 token ≈ 4 characters of English text:

| Section | Tokens (approx) | When included |
|---|---|---|
| System prompt (`system.txt`) | ~405 | Always |
| Rubric block (`rubric.txt` + content) | ~200 | Always |
| CoT instruction (`cot_instruction.txt`) | ~280 | When `with_reason=True` |
| Few-shot examples (2 worked examples) | ~800 | When few-shot ON |
| Task section (problem + code) | ~325 | Always (varies with submission size) |
| Output format block (no reason) | ~400 | When `with_reason=False` |
| Output format block (with reason) | ~465 | When `with_reason=True` |

Output assumed at ~600 tokens for `<RESULT>`-only responses, ~1,500 tokens when `<THINKING>` is also emitted.

### Per-scenario averages (two-phase design)

Phase 1 distributes evenly across all scenarios; Phase 2 only contributes to the *winner* on the *worst case*.

- **Phase 1 per scenario**: 144 runs (1 rep × 144 submissions across 6 cases)
- **Phase 2 (winner on worst case only)**: ~140 runs (7 reps × ~20 submissions)
- **Phase 2 (other 7 scenarios, other 5 cases)**: 0 runs

| Scenario | Input/run | Output/run | Phase 1 input (× 144) | Phase 1 output (× 144) |
|---|---:|---:|---:|---:|
| S1 baseline           | 1,330 |   600 | 0.19 M | 0.09 M |
| S2 rubric-only        | 1,330 |   600 | 0.19 M | 0.09 M |
| S3 cot-only           | 1,675 | 1,500 | 0.24 M | 0.22 M |
| S4 fewshot-only       | 2,130 |   600 | 0.31 M | 0.09 M |
| S5 rubric+cot         | 1,675 | 1,500 | 0.24 M | 0.22 M |
| S6 rubric+fewshot     | 2,130 |   600 | 0.31 M | 0.09 M |
| S7 cot+fewshot        | 2,475 | 1,500 | 0.36 M | 0.22 M |
| S8 all-on             | 2,475 | 1,500 | 0.36 M | 0.22 M |
| **Phase 1 subtotal (1,152 runs)** | — | — | **~2.19 M** | **~1.21 M** |
| Phase 2 (1 × ~140 runs, *if* winner = mid-cost S5/S3) | 1,675 | 1,500 | ~0.23 M | ~0.21 M |
| **Experiment total (mid-estimate, ~1,292 runs)** | — | — | **~2.42 M** | **~1.42 M** |

The Phase 2 row depends on which scenario wins and how many submissions the worst case has (20–28). Range across all possible winners is roughly **2.4–2.6 M input** and **1.3–1.5 M output** tokens. The mid-estimate row above assumes a CoT-on winner on a 20-submission worst case.

*(Adjust upward if your test submissions are larger than ~800 chars, or if the LLM produces longer thinking traces.)*

### Provider pricing (USD) — full experiment, no discounts

Prices reflect public per-million-token list pricing as of early 2026. **Verify the live pricing page before committing** — model lineups and pricing change frequently. Costs assume the mid-estimate of ~2.42 M input + ~1.42 M output tokens (full two-phase experiment, ~1,292 runs, CoT-on winner on a 20-submission worst case).

> Note on "GPT Codex": OpenAI Codex was retired years ago and isn't currently offered as a separate API. For code-grading use cases, the modern OpenAI lineup is GPT-4-class chat models or the o-series reasoning models. I've priced those instead.

#### Anthropic Claude

| Model | $/M input | $/M output | Input cost | Output cost | **Total** |
|---|---:|---:|---:|---:|---:|
| Claude Opus 4.7    | $15.00 | $75.00 | $36.30 | $106.50 | **~$143** |
| Claude Sonnet 4.6  | $3.00  | $15.00 | $7.26  | $21.30  | **~$29**  |
| Claude Haiku 4.5   | $1.00  | $5.00  | $2.42  | $7.10   | **~$10**  |

#### OpenAI

| Model | $/M input | $/M output | Input cost | Output cost | **Total** |
|---|---:|---:|---:|---:|---:|
| o1 (reasoning)     | $15.00 | $60.00 | $36.30 | $85.20  | **~$122** |
| GPT-4o             | $2.50  | $10.00 | $6.05  | $14.20  | **~$20**  |
| GPT-4o mini        | $0.15  | $0.60  | $0.36  | $0.85   | **~$1.20**|

#### Google Gemini

| Model | $/M input | $/M output | Input cost | Output cost | **Total** |
|---|---:|---:|---:|---:|---:|
| Gemini 2.5 Pro       | $1.25 | $5.00 | $3.03 | $7.10  | **~$10**  |
| Gemini 2.5 Flash     | $0.30 | $2.50 | $0.73 | $3.55  | **~$4**   |
| Gemini 2.5 Flash-Lite| $0.10 | $0.40 | $0.24 | $0.57  | **~$0.80**|

### Required cost levers — prompt caching + batch API

Both **prompt caching** and **batch submission** are part of the recommended experiment workflow, not optional optimizations. See `docs/design/cost-optimization.md` for the full implementation walkthrough; this section gives the contract the runner must satisfy.

#### Prompt caching

The system prompt + rubric + CoT instruction + few-shot block + output-format header are byte-for-byte identical across all 144 Phase 1 invocations of a scenario, and across all ~140 Phase 2 invocations of the winner. That's roughly 70–80% of input tokens that should be cached.

**Required runner contract:**
- The orchestrator splits the assembled prompt into `(cacheable_prefix, dynamic_suffix)`. Prefix = everything except the task section; suffix = `# Submission to grade ...`.
- The provider client marks the prefix as cacheable using the provider's native mechanism:
  - **Anthropic** — `system: [{"type": "text", "text": prefix, "cache_control": {"type": "ephemeral"}}]`.
  - **OpenAI** — automatic for prompts ≥ 1,024 tokens, but the prefix must be at the *start* of the request and identical byte-for-byte across runs. Don't reformat or shuffle within a scenario.
  - **Gemini** — explicit cache via `client.caches.create(...)` once per scenario, then pass `cached_content=cache.name` on every per-run call.
- Cache TTL: long enough to cover the duration of a scenario's runs (Anthropic 5 min default — bunch the runs of one scenario together; Gemini explicit cache supports configurable TTL).

Expected effect: input tokens drop to ~10% rate (Anthropic) or ~25–50% rate (OpenAI/Gemini) on the prefix portion. Net input savings ~60–70%.

#### Batch submission

The experiment is fully offline. There is no benefit to realtime invocation. **All ~1,292 runs go through the provider's batch API** for an automatic 50% discount on both input and output.

**Required runner contract:**
- Two batch jobs per provider: one Phase 1 batch (1,152 requests), one Phase 2 batch (~140 requests). Optional: split Phase 1 by scenario (8 batches) for atomic failure isolation. Phase 2 is small enough to stay as one batch.
- Provider endpoints:
  - **Anthropic** — Message Batches API; submit JSONL of `MessageCreateParams`.
  - **OpenAI** — Batch API; submit JSONL of `/v1/chat/completions` requests.
  - **Gemini** — `batches.create` with JSONL or BigQuery input.
- SLA: up to 24 h, usually under 1 h. Plan for one overnight cycle.
- Caching stacks with batch — cache reads in batch mode are still discounted.

#### Optional further savings

- **Skip persisting `<THINKING>`** when not analyzed. Doesn't lower API cost (the model still generates it) but reduces storage + analysis-time memory.
- **Local pilot** on Ollama (`llama3.1:8b` or `qwen2.5-coder:7b`) to validate the runner end-to-end before any paid call. Free.
- **Lower `max_tokens`** cap from 4,096 to ~2,500. Doesn't change cost but prevents runaway generations.

### Indicative real-world spend (with caching + batch)

Applying ~60% off list (caching + batch combined) to the totals above:

| Provider | List | After caching + batch (~60% off) |
|---|---:|---:|
| Claude Opus 4.7      | $143  | **~$57**   |
| Claude Sonnet 4.6    | $29   | **~$11**   |
| Claude Haiku 4.5     | $10   | **~$4**    |
| OpenAI o1            | $122  | **~$49**   |
| GPT-4o               | $20   | **~$8**    |
| GPT-4o mini          | $1.20 | **~$0.50** |
| Gemini 2.5 Pro       | $10   | **~$4**    |
| Gemini 2.5 Flash     | $4    | **~$1.70** |
| Gemini 2.5 Flash-Lite| $0.80 | **~$0.30** |

### Recommendation

With the two-phase design **and** caching + batch wired in, expected real spend is small enough that model choice can be driven by the research question, not by budget. Pick **one** model and run all ~1,292 invocations on it.

The realistic ("with caching + batch") column from the table above is the spend you should plan against:

- **"Does prompt engineering help a strong model become more accurate/consistent?"** → Sonnet 4.6 (~$11), GPT-4o (~$8), or Gemini 2.5 Pro (~$4). Best value/quality trade-off.
- **"What's the ceiling of LLM-based grading?"** → Opus 4.7 (~$57) or o1 (~$49).
- **"Can a cheap model do this if we engineer the prompt well?"** → Haiku 4.5 (~$4), GPT-4o-mini (~$0.50), or Gemini Flash / Flash-Lite (~$0.30–1.70). Effectively free.

If budget is tight, **Gemini 2.5 Pro** is the best raw cost/quality at this scale; **Sonnet 4.6** with prompt caching is comparable. Validate the runner end-to-end on a free local Ollama pilot before any paid call, regardless of the chosen model.

> ⚠️ Verify live pricing on each provider's pricing page before running. Listed numbers are estimates current to early 2026 and can change without notice. The "with caching + batch" column also depends on the provider applying both discounts cleanly together — confirm with a small pilot batch before scaling.

## Repository layout

The experiment lives in `experiments/` at the repo root:

```
experiments/
├── __init__.py
├── scenarios.py          # 8 prompt-engineering configurations (concrete)
├── metrics.py            # Pearson, MAE, ICC(A,1) implementations
├── runner.py             # Phase 1 + Phase 2 batch orchestration (skeleton)
├── dataset/
│   ├── problems.json     # 6 problems with structured + unstructured rubrics
│   ├── submissions.json  # ~120 hand-graded submissions
│   └── few_shot.json     # independent few-shot example pool
└── results/
    └── (Phase 1 / Phase 2 JSONL outputs land here, gitignored)
```

`scenarios.py` and `metrics.py` are concrete and ready to import. `runner.py` is a skeleton — `build_prompt` and `submit_batch` need to be wired against the chosen provider once the prompt prefix/suffix refactor is done.

## Implementation checklist

### Code changes (in `src/`)
- [ ] Add a `structured_rubric: bool` flag to `GradingRequest` in `src/api/schemas/request.py`, or carry both rubric strings on the request and switch externally.
- [ ] Refactor `PromptOrchestrator.build()` in `src/engine/prompt_orchestrator.py` to return `(cacheable_prefix, dynamic_suffix)` instead of a single string.
- [ ] Update the chosen provider client (`src/llm/openai.py`, `src/llm/gemini.py`, or a new `src/llm/anthropic.py`) to mark the prefix as cacheable using the provider's native mechanism.
- [ ] Add a `cached_tokens` field to the usage log so cache hits can be verified.

### Batch infrastructure (in `experiments/runner.py`)
- [ ] Implement `build_prompt(scenario, problem, submission, few_shot_pool)` to call into the refactored `PromptOrchestrator` and return `(prefix, suffix)`.
- [ ] Implement `submit_batch(requests)` against the chosen provider (Anthropic Message Batches / OpenAI Batch / Gemini Batch). Cache the prompt prefix per scenario.
- [ ] Verify ingest joins completed batch responses back to the run log by `run_id`.

### Dataset + fixtures (in `experiments/dataset/`)
- [x] `problems.json` populated with 6 problems (2 easy / 2 medium / 2 hard, structured + unstructured rubrics, single language per problem).
- [x] `submissions.json` populated with 144 submissions (28 / 20 / 25 / 25 / 23 / 23 across the 6 problems) — `submission_id` = source filename stem, `code` = the file content, `human_score` initially `null`.
- [x] `few_shot.json` populated with 2 Two-Sum examples (independent from the dataset).
- [ ] Fill in `human_score` for every entry in `submissions.json` against the matching problem's rubric — this is the manual grading step and must be done before any LLM run.

### Analysis
- [ ] Build an analysis notebook (suggest `experiments/analysis.ipynb`) that loads `results/phase1.jsonl` + `results/phase2.jsonl` and computes Pearson, MAE per scenario (Phase 1, 8 values each) and ICC(A,1) for the winner (Phase 2, 1 headline + 6 per-problem), all with 95% CIs.
- [ ] For ICC, prefer `pingouin.intraclass_corr` over the in-house `experiments/metrics.py:icc_a1` once a pilot validates that the two agree (the in-house version is for reference / minimal-deps use).

### Validation
- [ ] Local pilot via Ollama (`OllamaProvider(BaseLLMProvider)` next to existing `src/llm/openai.py`) before any paid call — runs the entire Phase 1 + Phase 2 flow on a free local model to verify the runner end-to-end.
- [ ] After the first ~10 batched calls of the real run, inspect `cached_tokens / tokens_in` in the run log — should be ≥ 0.6 once the cache is warm. If it's near zero, caching isn't actually working.

## Open questions / assumptions to confirm

Resolved (locked in by `experiments/dataset/`):

- ~~Structured vs unstructured rubric definition~~ — both forms authored in `problems.json` for each of the 6 problems; structured = numbered + weighted (Correctness 50% / Readability 25% / Efficiency 25%), unstructured = free-form paragraph covering the same content.
- ~~Per-problem vs shared rubric~~ — per-problem (each entry has its own `rubric_structured` / `rubric_unstructured`).
- ~~Submission count~~ — variable: 28 / 20 / 25 / 25 / 23 / 23 = 144 total. Variable counts are fine for ICC.
- ~~Programming languages~~ — locked in: P1 Python, P2 Java, P3 TypeScript, P4 C++, P5 Java, P6 Go.

Still open:

1. **Few-shot example count** — currently 2 in `few_shot.json` (Two-Sum, poor + good). Use 1, 2, or all of them in a "few-shot ON" run? Hold the count constant across all such runs.
2. **Temperature** — must be > 0 or consistency variance collapses. Suggest 0.3–0.7. Pick once and pin.
3. **MAE scale** — report raw (0–100) and normalized (÷100), per the `0 ≤ MAE ≤ 1` convention?
4. **ANOVA add-on** — do you want per-feature attribution on top of per-scenario ranking, or is the ranking enough?
5. **Tiebreaker for the Phase 2 winner** — the picker uses `(MAE asc, Pearson r desc)`. Confirm this ordering rather than the reverse, or a composite score.
