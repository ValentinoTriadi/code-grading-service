# Design Testing Plan

## Overview

This document defines the testing plan for the **Code Grading Service**. It covers all layers of testing — from unit tests of individual components to end-to-end validation of the full grading pipeline — ensuring the system is correct, reliable, and produces fair and consistent grades.

---

## Testing Objectives

1. **Correctness** — The system correctly processes submissions, builds prompts, and parses LLM responses.
2. **Consistency** — Identical code submissions receive the same (or very similar) scores across multiple runs.
3. **Robustness** — The system gracefully handles invalid inputs, API failures, and edge cases.
4. **Fairness** — Grading scores align with human-expert evaluations within an acceptable tolerance.
5. **Performance** — The system meets latency and throughput requirements under expected load.
6. **Security** — No sensitive student data is leaked to external APIs or logs.

---

## Test Layers

### Layer 1: Unit Tests

Test individual classes and functions in isolation, using mocks for external dependencies.

#### 1.1 `Submission` Class

| Test Case                                | Expected Result                                      |
|-----------------------------------------|------------------------------------------------------|
| Create submission with valid data        | Submission object created successfully               |
| `validate()` with all required fields    | Returns `True`                                       |
| `validate()` with missing `code` field   | Returns `False`                                      |
| `validate()` with unsupported language   | Returns `False`                                      |
| `to_dict()` serialization                | Returns correct dictionary representation           |

#### 1.2 `Rubric` and `Criterion` Classes

| Test Case                                | Expected Result                                      |
|-----------------------------------------|------------------------------------------------------|
| Create rubric with valid criteria        | Rubric object created successfully                   |
| `validate()` with weights summing to 1.0 | Returns `True`                                       |
| `validate()` with weights not summing    | Returns `False`                                      |
| `get_criteria()` returns all criteria    | Returns the full list of `Criterion` objects         |

#### 1.3 `PromptBuilder` Class

| Test Case                                            | Expected Result                                       |
|-----------------------------------------------------|-------------------------------------------------------|
| `build_grading_prompt()` with valid submission/assignment | Returns non-empty string containing code and rubric |
| `build_grading_prompt()` inserts assignment title    | Prompt contains assignment title                     |
| `build_grading_prompt()` inserts student code        | Prompt contains the submitted code                   |
| `build_grading_prompt()` inserts all rubric criteria | Prompt contains all criterion names                  |
| `build_feedback_prompt()` with completed result      | Returns non-empty feedback prompt string             |

#### 1.4 `LLMClient` Class

| Test Case                                            | Expected Result                                      |
|-----------------------------------------------------|------------------------------------------------------|
| `generate()` with valid prompt (mocked API)          | Returns string response                              |
| `generate()` when API returns 429 (rate limit)       | Retries with backoff                                 |
| `generate()` after max retries exceeded              | Raises `LLMUnavailableError`                         |
| `generate_with_schema()` with valid response         | Returns parsed dictionary                            |
| `generate_with_schema()` with invalid JSON response  | Raises `LLMResponseParseError`                       |
| `health_check()` with live API connection (mocked)   | Returns `True`                                       |
| `health_check()` with failed connection (mocked)     | Returns `False`                                      |

#### 1.5 `GradingResult` Class

| Test Case                                | Expected Result                                      |
|-----------------------------------------|------------------------------------------------------|
| `get_percentage()` for 80/100 score      | Returns `80.0`                                       |
| `get_percentage()` for 0/100 score       | Returns `0.0`                                        |
| `to_dict()` serialization                | Returns correct dictionary                           |
| `to_report()` generates readable text    | Returns non-empty formatted string                   |

---

### Layer 2: Integration Tests

Test interaction between multiple components within the service boundaries (no external API calls; LLM is mocked).

#### 2.1 `GradingService` Integration

| Test Case                                                       | Expected Result                                            |
|----------------------------------------------------------------|------------------------------------------------------------|
| `grade()` with valid submission and assignment (mocked LLM)     | Returns `GradingResult` with scores for all criteria       |
| `grade()` with LLM returning malformed JSON                     | Retries and returns error or flags for manual grading      |
| `grade()` with empty code submission                            | Returns `GradingResult` with total score of 0              |
| `grade()` saves result to `ResultRepository`                    | Result is persisted and retrievable by ID                  |
| `regrade()` with existing submission ID                         | Returns new `GradingResult` with updated timestamp         |

#### 2.2 Repository Integration (with In-Memory or SQLite Store)

| Test Case                                              | Expected Result                                      |
|-------------------------------------------------------|------------------------------------------------------|
| Save and retrieve `Submission` by ID                   | Retrieved submission matches saved submission        |
| Save and retrieve `GradingResult` by submission ID     | Retrieved result matches saved result                |
| `find_by_student()` returns all submissions for a student | Returns correct list of submissions               |
| `update_status()` changes submission status            | Status updated and persisted correctly               |

#### 2.3 End-to-End Grading Pipeline (Mocked LLM)

| Test Case                                                       | Expected Result                                        |
|----------------------------------------------------------------|--------------------------------------------------------|
| Submit code → Grade → Retrieve result                           | Full pipeline completes and result is accessible       |
| Submit code with wrong language → Validate → Reject             | Submission rejected before reaching LLM               |
| Grade 10 submissions concurrently                               | All submissions graded correctly without race conditions|

---

### Layer 3: LLM Evaluation Tests (Grading Quality)

These tests measure the **accuracy and consistency** of the LLM's grading compared to human-expert grades. Use a curated benchmark dataset.

#### 3.1 Benchmark Dataset

The benchmark dataset contains:

| Category                    | Count | Description                                          |
|-----------------------------|-------|------------------------------------------------------|
| Correct solutions           | 20    | Code that fully solves the assignment                |
| Partially correct solutions | 20    | Code with minor bugs or incomplete logic             |
| Incorrect solutions         | 20    | Code that does not solve the problem                 |
| Edge case solutions         | 10    | Solutions with unusual but valid approaches          |
| Empty/invalid submissions   | 10    | Empty files or syntax errors                         |
| **Total**                   | **80**| —                                                    |

Each sample has:
- Student code
- Assignment and rubric
- Human-expert score and feedback (ground truth)

#### 3.2 Grading Accuracy Tests

| Metric                     | Acceptable Threshold      | Description                                                 |
|---------------------------|--------------------------|-------------------------------------------------------------|
| Mean Absolute Error (MAE) | ≤ 5 points (out of 100)  | Average score difference from human expert                  |
| Score correlation          | ≥ 0.85 (Pearson r)        | Correlation between LLM scores and human scores             |
| Exact agreement rate       | ≥ 60%                    | Percentage where LLM and human agree within ±2 points       |
| False pass rate            | ≤ 5%                     | Incorrect submissions scored above passing threshold        |
| False fail rate            | ≤ 5%                     | Correct submissions scored below passing threshold          |

#### 3.3 Consistency Tests

| Test Case                                          | Expected Result                                              |
|---------------------------------------------------|--------------------------------------------------------------|
| Grade same submission 5 times                      | Score variance ≤ 3 points across all runs                   |
| Grade semantically equivalent submissions          | Scores within ±5 points of each other                       |
| Grade refactored code with same logic              | Score should not drop more than 5 points vs. original       |

---

### Layer 4: Performance Tests

#### 4.1 Load Testing

| Test Scenario               | Target                          | Tool              |
|----------------------------|---------------------------------|-------------------|
| Throughput                  | ≥ 50 submissions/minute         | Locust / k6       |
| P95 grading latency         | ≤ 15 seconds per submission     | Locust / k6       |
| Concurrent submissions      | 100 concurrent without failures | Locust / k6       |

#### 4.2 Stress Testing

| Test Scenario               | Target                          | Tool              |
|----------------------------|---------------------------------|-------------------|
| Ramp up to 500 req/min      | No crashes; graceful degradation| Locust            |
| Sustained load (30 min)     | Memory usage stable, no leaks   | Locust + profiler |
| LLM API timeout simulation  | Fallback activates within 5s    | Manual / mocking  |

---

### Layer 5: Security Tests

| Test Case                                             | Expected Result                                       |
|------------------------------------------------------|-------------------------------------------------------|
| Submission containing PII (name, email in code)       | PII stripped before sending to LLM API               |
| API key exposure check in logs                        | No API keys appear in application logs               |
| Prompt injection in student code                      | System prompt remains intact; injection ignored       |
| Unauthorized access to grading results                | Returns 403 Forbidden for unauthorized users         |
| SQL/NoSQL injection in submission metadata            | Input sanitized; no database errors                  |

---

## Test Infrastructure

### Testing Stack

| Layer           | Tool/Framework                      |
|----------------|-------------------------------------|
| Unit tests      | `pytest`                            |
| Mocking         | `pytest-mock` / `unittest.mock`     |
| Integration     | `pytest` + in-memory SQLite          |
| LLM mocking     | `respx` / `responses` (HTTP mocking)|
| Performance     | `locust`                            |
| Coverage        | `pytest-cov`                        |
| CI/CD           | GitHub Actions                      |

### Test Directory Structure

```
tests/
├── unit/
│   ├── test_submission.py
│   ├── test_rubric.py
│   ├── test_prompt_builder.py
│   ├── test_llm_client.py
│   └── test_grading_result.py
├── integration/
│   ├── test_grading_service.py
│   ├── test_repositories.py
│   └── test_grading_pipeline.py
├── evaluation/
│   ├── benchmark_dataset/
│   │   └── (80 sample submissions with ground truth)
│   └── test_grading_accuracy.py
├── performance/
│   └── locustfile.py
├── security/
│   └── test_security.py
└── conftest.py
```

---

## Coverage Requirements

| Component          | Minimum Coverage |
|-------------------|------------------|
| `GradingService`   | 90%              |
| `LLMClient`        | 85%              |
| `PromptBuilder`    | 90%              |
| `Repositories`     | 80%              |
| Overall            | 85%              |

---

## CI/CD Pipeline Integration

All tests are integrated into the GitHub Actions CI/CD pipeline:

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run unit & integration tests
        run: pytest tests/unit tests/integration --cov=src --cov-report=xml
      - name: Check coverage threshold
        run: pytest --cov=src --cov-fail-under=85
```

LLM evaluation and performance tests run on a scheduled basis (weekly) rather than on every commit to avoid excessive API costs.

---

## Test Execution Schedule

| Test Suite              | Trigger                       | Environment         |
|------------------------|-------------------------------|---------------------|
| Unit tests              | Every commit / PR             | CI (no LLM calls)   |
| Integration tests       | Every commit / PR             | CI (mocked LLM)     |
| LLM evaluation tests    | Weekly scheduled run          | Staging (real LLM)  |
| Performance tests       | Pre-release                   | Staging             |
| Security tests          | Monthly / Pre-release         | Staging             |

---

## Acceptance Criteria

The system is considered ready for production when:

- [ ] All unit and integration tests pass with ≥ 85% code coverage.
- [ ] LLM grading accuracy achieves MAE ≤ 5 points and correlation ≥ 0.85 on benchmark dataset.
- [ ] Grading consistency: score variance ≤ 3 points for identical submissions.
- [ ] P95 grading latency ≤ 15 seconds under normal load.
- [ ] No critical security vulnerabilities found.
- [ ] Fallback mechanism successfully activates when primary LLM is unavailable.
