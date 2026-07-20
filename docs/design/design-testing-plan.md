# Design Testing Plan

## Objective

Establish a layered testing strategy for the grading pipeline with fast feedback and strong confidence for prompt/LLM-dependent behavior.

## Test Layers

### 1) Unit Tests (Primary)

Target: `src/engine/*`, `src/prompts/builder.py`

Coverage baseline:

- `InputParser`
  - inline mode parsing
  - single `code_file_url` parsing
  - batch `batch_code_files` merge behavior
  - S3-compatible URL normalization and unsupported scheme rejection
  - pre-signed URL compatibility (S3, R2, MinIO)
- `InputHandler`
  - valid request normalization
  - empty/missing field validation
  - sanitize behavior
- `PromptOrchestrator`
  - section ordering
  - custom rubric injection
  - custom few-shot injection
- `LLMInterface`
  - forwards prompt to provider
  - passes runtime kwargs
  - handles provider exceptions
- `ResponseParser`
  - parses expected output format
  - handles malformed/partial output gracefully

### 2) API Contract Tests

Target: `POST /api/v1/grade`

Coverage baseline:

- valid request returns `GradingResponse` schema
- invalid request fields return validation errors
- internal failures map to stable API error response

### 3) Integration Tests (Mocked LLM)

Target: end-to-end pipeline without external network

Coverage baseline:

- complete pipeline executes from request to structured response
- deterministic mock responses ensure reproducibility

## Non-Goals (Initial Baseline)

- Live provider E2E tests against real LLM API in CI.
- Performance/stress testing in first milestone.

## Tooling and Conventions

- Test framework: `pytest`.
- Async tests: `pytest-asyncio` for `LLMInterface`/route async paths.
- Use fixtures for common `GradingRequest` payloads and mock providers.
- Keep tests deterministic; no random outputs without seeding.
- Run sessions use `uv run ...` (e.g., `uv run pytest`).

## Suggested Test Structure

- `tests/test_input_handler.py`
- `tests/test_input_parser.py`
- `tests/test_prompt_orchestrator.py`
- `tests/test_llm_interface.py`
- `tests/test_response_parser.py`
- Add `tests/test_grading_route.py` for API contract coverage.

## Quality Gates

- All tests pass in local and CI.
- No placeholder tests as final baseline.
- Critical path coverage includes both success and failure scenarios.

## Definition of Done

- Placeholder tests replaced with behavior-based assertions.
- New route integration tests added.
- Pipeline regressions are caught by deterministic tests before merge.
