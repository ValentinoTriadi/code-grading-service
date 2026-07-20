# `src/` Architecture

This document summarizes the production backend (`src/`) — a FastAPI service that grades
student code submissions against a rubric using an LLM, with pluggable providers
(OpenAI, Gemini, Anthropic).

## Directory map

```
src/
├── api/
│   ├── routes/grading.py         FastAPI route definitions (HTTP layer)
│   ├── controllers/grading.py    Decodes uploads, dispatches to the service, formats responses
│   ├── schemas/request.py        Request models (InlineGradingRequest, GradingRequest, FewShotExample)
│   ├── schemas/response.py       Response models (GradingResponse, FeedbackDetail, CriterionResult)
│   └── dependencies.py           FastAPI DI wiring — builds the whole pipeline per request
├── engine/
│   ├── input_handler.py          Sanitizes/validates a GradingRequest
│   ├── prompt_orchestrator.py    Assembles the LLM prompt (StructuredPrompt)
│   ├── llm_interface.py          Rate-limited call to the configured provider
│   └── response_parser.py        Parses raw LLM text into a GradingResponse
├── llm/
│   ├── base.py                   BaseLLMProvider ABC — one method: generate(prompt) -> str
│   ├── openai.py                 OpenAI Chat Completions
│   ├── gemini.py                 Google Gemini — AI Studio API key or Vertex AI (ADC)
│   └── anthropic.py               Anthropic Messages API
├── prompts/
│   ├── builder.py                Loads template files, injects rubric/few-shot content
│   └── templates/{system,rubric,cot_instruction}.txt
├── services/
│   └── grading_service.py        Orchestrates the 4-step pipeline for one submission
└── config/
    ├── settings.py                Env-driven settings (pydantic-settings)
    └── logging.py
```

## Request lifecycle

```
route (grading.py)
  → GradingController               (decode upload / zip, build internal GradingRequest)
    → GradingService.grade()
        1. InputHandler.validate()        — normalize line endings, strip, reject empty code
        2. PromptOrchestrator.build()     — assemble StructuredPrompt (see below)
        3. LLMInterface.generate()        — rate-limit, call BaseLLMProvider.generate()
        4. ResponseParser.parse()         — extract <RESULT> JSON → GradingResponse
    → GradingController                (format as JSON or Excel; strip reasoning if not requested)
  → route returns GradingResponse / StreamingResponse / EventSourceResponse
```

Every step can report progress via an `on_progress(step, total, message)` callback, which the
`/stream` route variants use to emit Server-Sent Events instead of waiting for the full pipeline.

### Three input modes, one pipeline

All three ways of submitting code funnel into the same `GradingService.grade()`:

| Endpoint | Input | Output |
|---|---|---|
| `POST /api/v1/grade/inline` | JSON body (`problems`, `code`, `rubric?`, `few_shot_examples?`) | `GradingResponse` |
| `POST /api/v1/grade/file` | multipart form + uploaded source file | `GradingResponse` |
| `POST /api/v1/grade/batch` | multipart form + zip of source files | `.xlsx` (one row per file) |

Each has an `/stream` variant returning SSE progress events instead of a single blocking response.
Batch grading runs submissions concurrently, bounded by an `asyncio.Semaphore` sized from
`BATCH_CONCURRENCY`; per-file errors (bad UTF-8, LLM failure) are captured per-row rather than
failing the whole batch.

## Prompt assembly (`prompt_orchestrator.py`)

The prompt is built as a `StructuredPrompt` with two parts:

- **`cacheable_prefix`** — system prompt + rubric + (optional) chain-of-thought instructions +
  (optional) few-shot examples + the strict output-format spec. Identical for every submission
  under the same configuration (same rubric, same `with_reason` flag, same examples) — the part
  a provider's prompt cache should key on.
- **`dynamic_suffix`** — the problem statement + student code for *this* submission. Always
  different, deliberately kept out of the cacheable part.

The output-format spec forces every response into a single `<RESULT>{...}</RESULT>` JSON block
(preceded by `<THINKING>...</THINKING>` when reasoning is requested), with a fixed schema:
`score`, `summary`, per-criterion `criteria[]`, `suggestions[]`, `exemplary_points[]`,
`complexity {time, space}`, and a `confidence` float. The system/rubric templates additionally
instruct the model to cite line-level evidence for every deduction rather than inferring defects
from the rubric's failure-mode list (see `system.txt`, `cot_instruction.txt`).

## Response parsing (`response_parser.py`)

Parses the `<RESULT>` JSON block into `GradingResponse`. Built to be tolerant of imperfect model
output:

- **Truncation repair** — if generation stops mid-JSON, walks the text tracking open
  `{`/`[` depth and appends the missing closers before re-parsing, recovering partial results
  instead of discarding the whole response.
- **Malformed tags** — tolerates a missing `>` on the opening tag, or a missing closing tag
  entirely (falls back to "everything after the opening tag").
- **Code-fence stripping** — strips a ` ```json ` fence if the model wrapped the block in one.
- **Legacy fallback** — an older multi-tag format (`<SCORE>`, `<FEEDBACK>`, `<FEEDBACK_JSON>`,
  `<REASONING>`) is still parsed if no `<RESULT>` block is found, for backward compatibility.
- **Score coercion** — clamps to `[0, 100]` and extracts a number even from a stringly-typed or
  slightly-malformed score value.

## LLM providers (`llm/`)

All three providers implement `BaseLLMProvider.generate(prompt) -> str` and are selected in
`api/dependencies.py::get_llm_provider()` from `LLM_PROVIDER` (`openai` | `gemini` | `anthropic`).

- **OpenAI** — standard Chat Completions call.
- **Gemini** — two auth modes: AI Studio (`LLM_API_KEY`) or Vertex AI (`GEMINI_USE_VERTEX=true` +
  `GOOGLE_CLOUD_PROJECT`/`GOOGLE_CLOUD_LOCATION`, authenticating via Application Default
  Credentials — `gcloud auth application-default login` locally, or the attached service account
  on GCP).
- **Anthropic** — defaults to Claude Opus 4.7; drops the `temperature` param for that model
  specifically (the API 400s if it's sent), since adaptive thinking replaced the old
  extended-thinking budget knob and the grading prompt already has its own `<THINKING>` block via
  chain-of-thought instructions.

`LLMInterface` wraps whichever provider is selected with a `RequestRateLimiter` — an async
sliding-window limiter (`LLM_REQUESTS_PER_MINUTE`) shared across all requests via a single
module-level instance in `dependencies.py`.

## Configuration

`src/config/settings.py` is a `pydantic-settings` `BaseSettings` reading from `.env`:
`LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL_NAME`, `LLM_MAX_TOKENS`, `LLM_TEMPERATURE`,
`LLM_REQUESTS_PER_MINUTE`, Vertex AI settings (`GEMINI_USE_VERTEX`, `GOOGLE_CLOUD_PROJECT`,
`GOOGLE_CLOUD_LOCATION`), and API-level settings (`API_HOST`, `API_PORT`, `DEBUG`,
`BATCH_CONCURRENCY`).

## Notable design choices

- **Dependency injection over singletons** — every component (`InputHandler`,
  `PromptOrchestrator`, `LLMInterface`, `ResponseParser`, and the provider itself) is constructed
  per-request via FastAPI `Depends()` chains in `dependencies.py`, making each layer trivially
  mockable in tests (see `tests/_fakes.py`, `tests/conftest.py`).
- **Internal vs. external request models** — `InlineGradingRequest` (API-facing, Pydantic
  validation + OpenAPI example) is translated into `GradingRequest` (internal, shared by all
  three input modes) inside the controller, so the engine layer doesn't care whether the code
  came from JSON, a file, or a zip entry.
- **Prefix/suffix prompt split exists specifically for provider-side prompt caching** — since the
  rubric/CoT/few-shot/output-format text is identical across a batch of submissions, providers
  that support prompt caching (Anthropic, Gemini) only pay full input-token cost once per
  configuration, not once per submission.
- **Parser resilience is load-bearing** — the `experiments/` harness (see root `README.md`)
  measures parse rate as a first-class metric per prompting configuration, so the repair/fallback
  logic in `response_parser.py` isn't defensive-programming for its own sake — it's tuned against
  observed failure modes from real model output (see `docs/thesis/hasil-eksperimen.md`).
