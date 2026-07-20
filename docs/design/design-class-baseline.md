# Design Class Baseline

## Objective

Define a clean, testable class baseline for the grading pipeline:
`InputParser -> InputHandler -> PromptOrchestrator -> LLMInterface -> ResponseParser`.

## Baseline Architecture

### 1. `InputParser`

**Responsibility**

- Resolve request input mode into one normalized `student_code` payload.
- Support three mutually exclusive modes in `GradingRequest`:
  - `student_code` (inline payload)
  - `code_file_url` (single remote file)
  - `batch_code_files` (multiple remote files)
- Fetch remote files through `httpx` with S3-compatible object storage URL normalization
  (AWS S3, Cloudflare R2, MinIO via pre-signed URLs).
- Merge batch files into one code block with filename separators.

**Public methods**

- `parse(request: GradingRequest) -> ParsedInput` (async)

### 2. `InputHandler`

**Responsibility**

- Validate `GradingRequest` fields (`problem_description`, selected input mode).
- Normalize code input (`\r\n` to `\n`, trim trailing spaces where needed).
- Provide a safe, sanitized code payload.

**Public methods**

- `validate(request: GradingRequest) -> GradingRequest`
- `sanitize_code(code: str) -> str`

### 3. `PromptOrchestrator`

**Responsibility**

- Assemble final prompt from templates and request context.
- Compose sections in deterministic order:
  1. system prompt
  2. rubric section
  3. CoT instruction section
  4. few-shot section
  5. problem + student code payload

**Public method**

- `build(request: GradingRequest) -> str`

### 4. `LLMInterface`

**Responsibility**

- Call provider via `BaseLLMProvider` abstraction.
- Inject runtime settings (model, temperature, max tokens) consistently.
- Return raw LLM text.

**Public method**

- `generate(prompt: str) -> str` (async)

### 5. `ResponseParser`

**Responsibility**

- Parse raw LLM output into `GradingResponse`.
- Extract: `score`, `feedback`, `reasoning`.
- Handle malformed outputs with robust fallback errors.

**Public method**

- `parse(raw_response: str) -> GradingResponse`

## Dependency Direction

- API layer depends on engine classes.
- Engine depends on:
  - schemas (`request/response`)
  - prompts (`PromptBuilder`)
  - LLM provider abstraction (`BaseLLMProvider`)
- Engine classes should not depend on FastAPI route internals.

## Baseline Data Flow

1. `grading.py` receives `GradingRequest`.
2. `InputParser.parse` resolves inline/single URL/batch URL into normalized code.
3. `InputHandler.validate` performs sanitization and request normalization.
4. `PromptOrchestrator.build` returns complete prompt text.
5. `LLMInterface.generate` returns raw model output.
6. `ResponseParser.parse` returns `GradingResponse`.
7. API returns structured response to client.

## Error Baseline

- Validation errors: explicit `ValueError`/custom domain error from `InputHandler`.
- Provider/runtime errors: surfaced as infrastructure error from `LLMInterface`.
- Parsing errors: structured parser error with safe fallback message.

## Definition of Done

- `InputParser` supports inline, single-file URL, and batch-file URL with S3-compatible object storage.
- Input-related engine classes have concrete implementation (no TODO or `NotImplementedError`).
- `grade_code` route executes full pipeline.
- Unit tests cover success and failure paths for each class.
- `uv run pytest` passes for baseline class tests.
