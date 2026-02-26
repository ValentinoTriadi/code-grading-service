# Design LLM Usage Plan

## Overview

This document outlines the plan for integrating and using Large Language Models (LLMs) within the **Code Grading Service**. It covers the selection of LLM providers, API usage strategy, cost management, rate limiting, fallback mechanisms, and ethical considerations.

---

## LLM Role in the System

The LLM serves as the **core intelligence layer** of the Code Grading Service. It is responsible for:

1. **Automated Code Evaluation** — Parsing and understanding student code submissions and scoring them according to the rubric.
2. **Feedback Generation** — Producing human-readable, constructive feedback for students.
3. **Plagiarism Detection (Optional)** — Identifying suspiciously similar code submissions.
4. **Code Review (Optional)** — Providing additional code quality analysis independent of the rubric score.

---

## LLM Provider Selection

### Primary Provider: OpenAI

| Model         | Use Case                        | Context Window | Estimated Cost         |
|--------------|---------------------------------|----------------|------------------------|
| `gpt-4o`     | Grading complex code            | 128K tokens    | ~$5 / 1M input tokens  |
| `gpt-4o-mini`| Lightweight feedback generation | 128K tokens    | ~$0.15 / 1M input tokens |

### Backup Provider: Google Gemini

| Model                  | Use Case             | Context Window | Estimated Cost             |
|-----------------------|----------------------|----------------|-----------------------------|
| `gemini-1.5-pro`      | Grading complex code | 1M tokens      | ~$3.50 / 1M input tokens   |
| `gemini-1.5-flash`    | High-throughput tasks| 1M tokens      | ~$0.075 / 1M input tokens  |

### Local Fallback: Ollama (Open-Source)

For environments where cloud APIs are unavailable or cost-prohibitive:

| Model              | Use Case               | Notes                       |
|-------------------|------------------------|-----------------------------|
| `codellama:13b`   | Code analysis          | Requires local GPU           |
| `llama3.2:3b`     | Lightweight feedback   | CPU-compatible               |

---

## API Integration Strategy

### Architecture

```
                ┌───────────────────────┐
                │    GradingService     │
                └───────────┬───────────┘
                            │
                ┌───────────▼───────────┐
                │      LLMClient        │  ◄── abstraction layer
                └───────────┬───────────┘
                            │
             ┌──────────────┼──────────────┐
             │              │              │
   ┌─────────▼─────┐ ┌──────▼──────┐ ┌────▼────────────┐
   │  OpenAI API   │ │ Gemini API  │ │  Ollama (Local) │
   └───────────────┘ └─────────────┘ └─────────────────┘
```

- The `LLMClient` class abstracts provider-specific implementations behind a common interface.
- Provider selection is configurable via environment variables (`LLM_PROVIDER=openai|gemini|ollama`).
- The system supports **hot-swapping** providers without code changes.

### Retry and Fallback Logic

```
Request → Primary Provider (OpenAI)
    ├── Success → Return response
    └── Failure (rate limit / timeout / error)
            └── Retry (up to 3 times with exponential backoff)
                    └── Still failing → Switch to Backup Provider (Gemini)
                                └── Still failing → Use Local Fallback (Ollama)
                                            └── Still failing → Return error to user
```

**Retry Configuration:**

| Attempt | Delay Before Retry |
|---------|--------------------|
| 1st     | 1 second           |
| 2nd     | 2 seconds          |
| 3rd     | 4 seconds          |

---

## Token Budget and Cost Management

### Token Usage Estimation Per Submission

| Prompt Component     | Estimated Tokens |
|---------------------|------------------|
| System prompt        | ~100             |
| Assignment description | ~200           |
| Rubric               | ~150             |
| Student code         | ~500 (average)   |
| LLM response         | ~400             |
| **Total per grading**| **~1,350**       |

### Cost Projection (GPT-4o)

| Submissions/Day | Tokens/Day        | Estimated Daily Cost |
|----------------|-------------------|----------------------|
| 100            | 135,000           | ~$0.68               |
| 500            | 675,000           | ~$3.38               |
| 1,000          | 1,350,000         | ~$6.75               |
| 10,000         | 13,500,000        | ~$67.50              |

> Cost projections are estimates and may vary based on actual code length and rubric complexity.

### Cost Optimization Strategies

1. **Model Routing** — Use `gpt-4o-mini` for initial drafts and `gpt-4o` only for complex submissions flagged for manual review.
2. **Caching** — Cache LLM responses for identical code+rubric combinations to avoid redundant API calls.
3. **Token Compression** — Truncate excessively long submissions to a configurable max token limit before sending.
4. **Batch Processing** — Where possible, batch grading during off-peak hours to reduce latency costs.

---

## Rate Limiting and Quota Management

### OpenAI Rate Limits (Tier 1)

| Resource          | Limit              |
|------------------|--------------------|
| Requests/minute  | 500 RPM            |
| Tokens/minute    | 200,000 TPM        |
| Tokens/day       | 2,000,000 TPD      |

### Handling Rate Limits

- Implement a **token bucket** algorithm to smooth out bursts.
- Track per-minute token usage and delay requests when approaching limits.
- Use a **job queue** (e.g., Celery + Redis) to schedule grading tasks asynchronously, preventing overload.

---

## Data Privacy and Security

### Data Handling Policies

| Data Type             | Handling Policy                                                    |
|----------------------|--------------------------------------------------------------------|
| Student code          | Transmitted to LLM API; not stored by provider (opt-in policy)    |
| Assignment rubric     | Non-sensitive; transmitted to LLM API                             |
| Student identifiers   | **NEVER** included in prompts — use anonymized submission IDs only |
| Grading results       | Stored locally; not re-transmitted to LLM                         |

### Privacy Safeguards

- **Anonymization:** Strip all Personally Identifiable Information (PII) from code before sending to LLM.
- **Data Minimization:** Only include data necessary for grading in the prompt.
- **API Key Security:** Store API keys in environment variables or secrets managers; never hardcode.
- **Logging:** Log token usage and costs, but never log the actual prompts or responses containing student code.

---

## LLM Output Validation

Before accepting an LLM response as a valid grading result, the service must:

1. **Schema Validation** — Verify the response is valid JSON matching the expected schema.
2. **Score Range Check** — Ensure all scores are within `[0, max_score]`.
3. **Completeness Check** — Confirm all rubric criteria have corresponding scores.
4. **Consistency Check** — Verify `total_score` equals the sum of `criterion_scores`.

If validation fails:
- Retry the LLM call with a clarifying instruction ("Your previous response was not valid JSON. Please try again.").
- After 2 failed retries, flag the submission for manual grading.

---

## Monitoring and Observability

### Metrics to Track

| Metric                     | Purpose                                      |
|---------------------------|----------------------------------------------|
| `llm.requests.total`       | Total LLM API calls made                     |
| `llm.tokens.input`         | Total input tokens consumed                  |
| `llm.tokens.output`        | Total output tokens consumed                 |
| `llm.latency.p50/p95/p99`  | Latency percentiles for LLM responses        |
| `llm.errors.total`         | Total failed LLM API calls                   |
| `llm.fallbacks.total`      | Number of times fallback provider was used   |
| `llm.cost.daily`           | Estimated daily API cost                     |
| `grading.validation_failures` | Responses that failed output validation  |

### Alerting Thresholds

| Alert                          | Condition                                    |
|-------------------------------|----------------------------------------------|
| High error rate                | Error rate > 5% in last 5 minutes            |
| Approaching rate limit         | > 80% of RPM/TPM quota used                 |
| High daily cost                | Daily cost exceeds budget threshold          |
| Slow response                  | P95 latency > 10 seconds                     |

---

## LLM Upgrade and Deprecation Plan

| Activity                         | Frequency      | Owner               |
|----------------------------------|---------------|---------------------|
| Review new model releases        | Monthly        | ML/Engineering team |
| Benchmark new models vs. baseline| Quarterly      | QA team             |
| Update model if improvement > 5% | As needed      | Engineering team    |
| Deprecate old models             | Per provider timeline | Engineering team |

When upgrading models:
1. Run new model on a held-out validation set.
2. Compare scores with previous model and human ground truth.
3. Roll out to 10% of traffic first (canary deployment).
4. Monitor for regressions before full rollout.
