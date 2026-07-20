# Cost Optimization for the Prompt Experiment

How to drive the ≥6,720-invocation experiment cost down by 60–80% without changing the experimental design.

## TL;DR — what actually saves money

Ranked by leverage, biggest first:

| # | Lever | Typical savings | Effort |
|---|---|---|---|
| 1 | **Prompt caching** | 60–75% of *input* cost | 1 afternoon refactor |
| 2 | **Batch API** | 50% off both input and output | 1 afternoon |
| 3 | **Adaptive replicates** (3 → 7 only if ICC unstable) | up to 30% of total | 1 day analysis logic |
| 4 | **Drop `<THINKING>` persistence** when not analyzed | 0–20% of output | minor |
| 5 | **Local pilot** for runner / dataset validation | 100% on the pilot run | half day (Ollama) |
| 6 | Reduce per-run output cap | 5–15% | trivial |

What does **not** save money:
- **LangChain / LlamaIndex / LiteLLM** — they are routing and orchestration libraries. They don't change the price per token. LiteLLM gives unified billing tracking, which is useful for *reporting*, but not for *reducing* cost. Adding LangChain is pure overhead for this workload.
- "Switching to a smaller model" naively — that *does* change cost, but it changes the experiment too. Picking a smaller model is a research decision, not an optimization.

## 1. Prompt caching — the single biggest win

### Why it matters here

Roughly **70–80% of every prompt is identical across all 840 runs of a scenario**: system prompt, rubric block, CoT instruction, few-shot examples, output-format header. Only the task section (`# Submission to grade ...`) and a tiny tail change between runs.

If you split the prompt into a cacheable prefix and a dynamic suffix, providers will charge you ~10% (Anthropic) or ~50% (OpenAI / Gemini) of the normal input rate for the prefix on every run after the first.

### Required refactor

`src/engine/prompt_orchestrator.py` currently returns a single string. The LLM clients in `src/llm/openai.py` and `src/llm/gemini.py` send it as a single user message. To enable caching, change the orchestrator to return a **structured prompt** with two parts:

```python
@dataclass
class StructuredPrompt:
    cacheable_prefix: str   # system + rubric + CoT + few-shot + output-format header
    dynamic_suffix: str     # task section (problem + code) + result-schema tail
```

Then update each provider to mark the prefix as cacheable.

### Provider-specific mechanics

#### Anthropic (Claude)

Caches via `cache_control` markers on message blocks. The cache TTL is 5 minutes by default (longer with Sonnet/Opus latest versions). With 840 runs of a scenario submitted within the cache window, every run after the first hits the cache.

```python
# Pseudocode for Anthropic SDK (you'd add `anthropic` to deps)
response = await client.messages.create(
    model="claude-sonnet-4-6",
    system=[
        {
            "type": "text",
            "text": cacheable_prefix,
            "cache_control": {"type": "ephemeral"},
        }
    ],
    messages=[{"role": "user", "content": dynamic_suffix}],
)
```

Pricing impact at Sonnet 4.6 ($3 / $15 per M):
- Cache write: ~$3.75 / M (1.25× input rate, charged once per cache key)
- Cache read: ~$0.30 / M (0.1× input rate)
- Effective input cost ≈ 25–30% of un-cached.

#### OpenAI

Prompt caching on OpenAI is **automatic** for prompts ≥ 1,024 tokens — no API changes required, *but* the cacheable content must be at the **start of the prompt and identical byte-for-byte** across requests. Concretely: put the prefix first, the dynamic task at the end, and don't reformat the prefix between runs.

Cache hits are billed at 50% of base input rate (some models 25%). Cache misses pay normal rate.

The current code already sends the full prompt as one string, so the refactor here is just:
- Always emit prefix → suffix in the same byte order.
- Don't re-randomize anything in the prefix (e.g., few-shot order) within a scenario.

#### Google Gemini

Two flavors:
- **Implicit caching** (Gemini 2.5+ models): automatic, similar to OpenAI. Cache hits at ~25% of input rate.
- **Explicit caching** (`cachedContent` API): you upload the prefix once, get a cache ID, and reference it on every request. Better hit rate but adds plumbing.

For an experiment with hundreds of runs per scenario, **explicit caching** is the right call.

```python
# Pseudocode using google-genai
cache = client.caches.create(
    model="gemini-2.5-pro",
    contents=cacheable_prefix,
    ttl="3600s",
)
# Per-run:
response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents=dynamic_suffix,
    config=types.GenerateContentConfig(cached_content=cache.name),
)
```

### Estimated input savings on the experiment

Assume 75% of input tokens are cacheable (≈ 9.6 M of 12.8 M):

| Provider | Without cache | With cache | Savings |
|---|---:|---:|---:|
| Claude Sonnet 4.6 input  | $38  | ~$13  | ~$25 |
| GPT-4o input             | $32  | ~$16  | ~$16 |
| Gemini 2.5 Pro input     | $16  | ~$8   | ~$8  |

Output costs unchanged. So caching mostly helps when input is a non-trivial share of total — which is true for non-CoT scenarios (S1, S2, S4, S6).

## 2. Batch API — flat 50% off, no design changes

All three providers offer a non-realtime batch tier with a 50% discount on both input and output. SLA is typically "within 24 hours". Your experiment is offline analysis, not user-facing — perfect fit.

| Provider | Endpoint | Format | SLA |
|---|---|---|---|
| Anthropic | Message Batches API | JSONL of `MessageCreateParams` | Up to 24h, usually < 1h |
| OpenAI | Batch API | JSONL of `/v1/chat/completions` requests | Up to 24h |
| Gemini | Batch API (`batches.create`) | JSONL or BigQuery table | Up to 24h |

**Stacks with caching**: cache reads in batch mode are still discounted — you get both savings.

**Trade-off**: you can't see results streaming in real time. Run the batch overnight, analyze in the morning. For an experiment this size, that's a feature, not a bug.

### Workflow change

1. Build all ≥6,720 requests as JSONL up front.
2. Submit one batch per scenario (8 batches total). Why split: batches are atomic, so a failure in one doesn't stall the others.
3. Poll for completion. Persist results to your results table.

Estimated savings stacked with caching:

| Provider | Realtime list | + Caching | + Batch | **All three** |
|---|---:|---:|---:|---:|
| Claude Sonnet 4.6 | $143 | ~$118 | ~$72 | **~$59** |
| GPT-4o            | $102 | ~$86  | ~$51 | **~$43** |
| Gemini 2.5 Pro    | $51  | ~$43  | ~$26 | **~$22** |

(The "all three" column is approximate — exact stacking depends on whether the provider applies the batch discount before or after the cache-read rate. Confirm with your billing dashboard.)

## 3. Adaptive replicates — only run 7 reps when needed

The plan calls for 7 reps per `(scenario, submission)` to compute ICC(A,1). But if the LLM is highly consistent on a given submission, the first 3 reps will already show that. Conversely, if it's noisy, you want all 7.

### Strategy

1. Run **3 reps** for every cell first. Compute the per-cell sample standard deviation `σ̂`.
2. For cells where `σ̂` is below some threshold (e.g., < 2 points on the 0–100 scale), accept the 3-rep estimate.
3. For cells above the threshold, run the remaining **4 reps**.

Rough savings: if ~60% of cells are stable at 3 reps, total runs drop from 6,720 → ~5,250 (~22% saved on output cost too).

**Caveat**: ICC computation requires a balanced design (same `k` for every cell) for the standard formula. With unbalanced data you'd need a mixed-effects model (e.g., `pingouin.intraclass_corr` doesn't natively handle missing reps; `rpy2` + R's `lme4` does, or use `psych` package). If you don't want statistical complexity, skip this lever.

## 4. Drop `<THINKING>` persistence when not analyzing it

The 4 CoT scenarios (S3, S5, S7, S8) generate ~1,500 output tokens per run, of which ~900 are inside `<THINKING>`. If you only need the final scores for ICC and Pearson/MAE, you still **pay** for the thinking tokens (the model has to generate them) — but you can:

- Compress the result schema (already small) and lower `max_tokens` to ~1,800 to prevent runaway thinking.
- Skip *storing* the thinking text to disk. It doesn't reduce API cost but reduces audit-trail storage and analysis-time memory.

If you don't need any reasoning analysis, drop CoT-only and CoT+anything scenarios — but that defeats the experiment. Don't do this for cost reasons alone.

## 5. Local pilot to validate plumbing — free

Before spending real money, run a **mini-experiment** locally:

- 1 scenario × 6 problems × 1 submission × 1 rep = 6 invocations.
- Run on a local model via Ollama (e.g., `llama3.1:8b` or `qwen2.5-coder:7b`).
- Goal is *not* good grading — it's to verify:
  - The runner script ends up with the right rows in the results table.
  - Schema parsing works for whatever weirdness the model emits.
  - ICC computation pipeline runs end-to-end.
  - The fixtures file is well-formed.

Once the plumbing works, switch to the real provider and run the full experiment.

A small `OllamaProvider(BaseLLMProvider)` next to the existing `openai.py` / `gemini.py` is ~30 lines of code.

## 6. Reduce `max_tokens` cap

Currently `max_tokens=4096` in `src/llm/openai.py` and `src/llm/gemini.py`. The biggest realistic completion (CoT + JSON) is ~2,000 tokens. Drop the cap to ~2,500 for safety margin. This doesn't change the price you pay (you only pay for tokens actually generated), but it's a safety net against runaway generations.

## What about LangChain / LiteLLM / LlamaIndex?

Honest assessment, in case it comes up later:

- **LangChain**: orchestration framework. Adds chains, prompt templates, callbacks. **Does not reduce token cost**. Adds non-trivial complexity for a workload that already has clean per-provider clients. Skip it.
- **LiteLLM**: unified API across providers + spend tracking + retries. Useful as a thin proxy if you want one client object for OpenAI / Gemini / Anthropic. **Does not reduce token cost**, but its spend tracker is genuinely useful for reporting in a thesis. Optional.
- **LlamaIndex**: RAG-focused. Not relevant to grading-from-rubric.
- **Instructor / Outlines**: structured-output libraries that constrain the LLM to a JSON schema. They reduce *parsing failures* (saving retry costs) but don't directly reduce per-call cost. Useful if your `<RESULT>` parsing breaks frequently — measure your schema-validity rate first.

If you want one piece of cross-provider tooling worth adding, it's **LiteLLM** — for unified billing logs you can put in the thesis. Not for cost reduction.

## Combined savings — full picture

Assuming all three core levers (caching + batch + adaptive replicates) on Sonnet 4.6:

| Path | Approx total |
|---|---:|
| List price, all 6,720 runs realtime | $143 |
| + Prompt caching | $118 (−18%) |
| + Batch API | $72 (−50%) |
| + Adaptive replicates (~22% fewer runs) | **~$56 (−61%)** |

That's the realistic floor for a "do it properly" run on a strong model. Bring in **Gemini 2.5 Pro** instead and the same path lands around **$13–18**.

## Recommended implementation order

If you want to act on this rather than plan it:

1. **Ollama pilot** — half day. Validates the runner before any real money is spent.
2. **Refactor prompt assembly** to expose a `(prefix, suffix)` split. Half day.
3. **Wire prompt caching** for whichever provider you choose. Half day per provider.
4. **Wire batch submission** as an alternative to realtime. Half day per provider.
5. **(Optional) adaptive replicate logic** in the runner. One day.
6. Run the experiment.

Skipping (3) and (4) is fine if you only have a small budget — the plain `Sonnet × realtime` run at ~$143 or `Gemini Pro × realtime` at ~$51 is already affordable for a thesis. Caching + batch is what makes it cheap enough that you can re-run if you find a bug.
