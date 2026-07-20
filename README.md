# Code Grading Service

LLM-powered grading service for student code submissions, built with structured prompt engineering (rubric + chain-of-thought + few-shot). Built as part of a university thesis (Tugas Akhir) investigating whether prompt engineering improves agreement between LLM and human TA grading.

## Architecture

**Backend** — FastAPI (Python 3.13+), managed with `uv`.

- `src/api/` — routes, controllers, and Pydantic request/response schemas.
- `src/engine/` — the grading pipeline: input validation, prompt assembly (`prompt_orchestrator.py`), rate-limited LLM calls, response parsing.
- `src/prompts/` — prompt templates (system prompt, rubric, chain-of-thought instructions) assembled into a cacheable prefix + per-call dynamic suffix, so providers can cache the stable part of the prompt across submissions.
- `src/llm/` — provider implementations behind a common interface: OpenAI, Anthropic, and Gemini (API key or Vertex AI / Application Default Credentials).
- `src/services/grading_service.py` — orchestrates validate → build prompt → call LLM → parse response, with optional SSE progress callbacks.

**API endpoints** (`/grade/...`): `inline` (JSON body), `file` (single file upload), `batch` (zip of submissions → Excel report), each with an `/stream` SSE variant.

**Frontend** — `ui/`: React 19 + TypeScript + Vite, Tailwind CSS 4, shadcn/base-ui components, TanStack Query. Three submission modes (Inline / File / Batch) mirroring the backend's input paths, sharing a rubric/few-shot editor (`CommonFields.tsx`) and live SSE progress display.

**Experiment harness** — `experiments/`: a checkpointed CLI (`python -m experiments.runner {status|phase1|phase2|all|reset}`) that evaluates LLM grading against real human TA grades. Phase 1 runs a full factorial of 8 prompting scenarios (structured rubric × chain-of-thought × few-shot) across ~144 student submissions, scoring each by MAE and Pearson correlation to human grades. Phase 2 stress-tests the winning scenario with repeated gradings to compute inter-rater reliability (ICC). `analysis.py` holds the statistics (MAE, Pearson, ANOVA, ICC) backing the thesis's results chapter (`docs/thesis/`).

## Setup

```bash
uv sync
cp .env.example .env   # fill in LLM_PROVIDER, LLM_API_KEY / Vertex settings, etc.
uv run main.py
```

API docs are served at `/docs` once running.

### Frontend

```bash
cd ui
npm install
npm run dev
```

## Testing

```bash
uv run pytest
```

Live tests that hit a real LLM provider (`test_b_live.py`, `test_nonfunctional_live.py`) are excluded by default; run them explicitly when you have credentials configured.

## Experiments

```bash
uv run python -m experiments.runner status
uv run python -m experiments.runner all
```

See `experiments/results/summary.txt` for the latest aggregated results and `docs/thesis/hasil-eksperimen.md` for the full write-up. Raw per-scenario response dumps are not checked into the repo (see `.gitignore`); only aggregated summaries are versioned.
