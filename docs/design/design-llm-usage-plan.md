# Design LLM Usage Plan

## Objective
Provide a practical plan to integrate and operate LLM calls reliably through `BaseLLMProvider` and `LLMInterface`.

## Scope
- Provider abstraction stays in `src/llm/base.py`.
- Runtime orchestration happens in `src/engine/llm_interface.py`.
- Configuration sourced from `src/config/settings.py`.

## Provider Strategy

### Phase 1 (Baseline)
- Implement one concrete provider (e.g., OpenAI or Gemini) that satisfies:
  - `async generate(prompt: str, **kwargs) -> str`
- Inject provider into `LLMInterface` through constructor.

### Phase 2 (Extensibility)
- Add provider factory by `settings.llm_provider`.
- Standardize provider kwargs mapping (`model`, `temperature`, `max_tokens`).

## Runtime Request Policy
For each generation call:
- Use configured defaults from settings.
- Keep `temperature` low (default `0.0`) for grading consistency.
- Set explicit max tokens (`llm_max_tokens`) to cap cost and latency.

## Reliability Plan
- Add timeout for every LLM request.
- Add retry policy for transient network/provider failures.
- Return meaningful errors when provider is unavailable.

## Observability Plan
- Log metadata only (provider, model, latency, token usage if available).
- Do not log raw student code or full LLM output at high verbosity in production.
- Add correlation ID per request for end-to-end tracing.

## Cost and Performance Plan
- Track per-request token usage and latency.
- Set budget guardrails (max requests/minute, optional rate limiting).
- Consider short-term response caching only for identical deterministic prompts.

## Security Plan
- Load API keys from environment via `Settings` (`.env` for local dev).
- Never commit secrets.
- Validate outbound payload size to reduce abuse risk.

## Rollout Milestones
1. Implement concrete provider + wire into `LLMInterface`.
2. Add timeout/retry and structured errors.
3. Add metrics/logging hooks.
4. Validate against integration tests with mocked provider.

## Definition of Done
- One production-ready provider implementation is usable from API route.
- `LLMInterface.generate` is fully async, robust, and configurable.
- Failure cases are handled with explicit error paths.
- Usage metrics (at least latency and provider/model tags) are emitted.
