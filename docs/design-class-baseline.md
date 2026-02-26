# Design Class Baseline

## Overview

This document describes the baseline class design for the **Code Grading Service** — an automated system that evaluates student code submissions using Large Language Models (LLMs). The class design follows object-oriented principles and provides a modular architecture for submission intake, LLM interaction, grading, and result delivery.

---

## Core Classes

### 1. `Submission`

Represents a single student code submission.

| Attribute       | Type       | Description                                  |
|----------------|------------|----------------------------------------------|
| `id`            | `str`      | Unique identifier for the submission          |
| `student_id`    | `str`      | ID of the student who submitted               |
| `assignment_id` | `str`      | ID of the assignment being submitted          |
| `language`      | `str`      | Programming language (e.g., Python, Java)     |
| `code`          | `str`      | The actual source code submitted              |
| `submitted_at`  | `datetime` | Timestamp of submission                       |
| `status`        | `str`      | Status: `pending`, `grading`, `graded`        |

**Methods:**
- `validate() -> bool` — Validates that the submission has required fields and acceptable language.
- `to_dict() -> dict` — Serializes the submission to a dictionary.

---

### 2. `Assignment`

Represents an assignment or task that students are graded on.

| Attribute        | Type       | Description                                    |
|-----------------|------------|------------------------------------------------|
| `id`             | `str`      | Unique assignment identifier                   |
| `title`          | `str`      | Name of the assignment                         |
| `description`    | `str`      | Full description of the problem                |
| `rubric`         | `Rubric`   | Grading rubric associated with the assignment  |
| `language`       | `str`      | Expected programming language                  |
| `max_score`      | `int`      | Maximum possible score                         |
| `deadline`       | `datetime` | Submission deadline                            |

**Methods:**
- `get_rubric() -> Rubric` — Returns the grading rubric.
- `is_active() -> bool` — Checks if the assignment is still accepting submissions.

---

### 3. `Rubric`

Defines the grading criteria for an assignment.

| Attribute      | Type              | Description                               |
|---------------|-------------------|-------------------------------------------|
| `id`           | `str`             | Unique rubric identifier                  |
| `criteria`     | `List[Criterion]` | List of grading criteria                  |
| `total_weight` | `float`           | Total weight (should sum to 1.0 or 100)   |

**Methods:**
- `get_criteria() -> List[Criterion]` — Returns all grading criteria.
- `validate() -> bool` — Validates that weights sum correctly.

---

### 4. `Criterion`

A single grading criterion within a rubric.

| Attribute     | Type    | Description                                    |
|--------------|---------|------------------------------------------------|
| `name`        | `str`   | Name of the criterion (e.g., "Correctness")    |
| `description` | `str`   | Detailed explanation of what is evaluated      |
| `weight`      | `float` | Weight of this criterion in the total score    |
| `max_score`   | `int`   | Maximum score for this criterion               |

---

### 5. `GradingResult`

Stores the outcome of a grading process.

| Attribute        | Type              | Description                                  |
|-----------------|-------------------|----------------------------------------------|
| `id`             | `str`             | Unique result identifier                     |
| `submission_id`  | `str`             | Reference to the graded submission           |
| `total_score`    | `float`           | Final computed score                         |
| `max_score`      | `float`           | Maximum possible score                       |
| `criterion_scores` | `List[CriterionScore]` | Per-criterion breakdown of scores    |
| `feedback`       | `str`             | Overall textual feedback                     |
| `graded_at`      | `datetime`        | Timestamp when grading was completed         |
| `model_used`     | `str`             | Name of LLM model used for grading           |

**Methods:**
- `get_percentage() -> float` — Returns the percentage score.
- `to_dict() -> dict` — Serializes the result.
- `to_report() -> str` — Generates a human-readable report.

---

### 6. `CriterionScore`

Stores the score and feedback for a single criterion.

| Attribute      | Type    | Description                                   |
|---------------|---------|-----------------------------------------------|
| `criterion`    | `Criterion` | The criterion being scored               |
| `score`        | `float` | Score received for this criterion             |
| `feedback`     | `str`   | LLM-generated feedback for this criterion     |

---

### 7. `LLMClient`

Handles communication with the LLM provider (e.g., OpenAI, Google Gemini, etc.).

| Attribute     | Type  | Description                                     |
|--------------|-------|-------------------------------------------------|
| `model`       | `str` | Model name to use (e.g., `gpt-4o`)             |
| `api_key`     | `str` | API key for authentication                      |
| `temperature` | `float` | Sampling temperature (controls creativity)   |
| `max_tokens`  | `int` | Maximum number of tokens per response           |

**Methods:**
- `generate(prompt: str) -> str` — Sends a prompt to the LLM and returns a response.
- `generate_with_schema(prompt: str, schema: dict) -> dict` — Returns a structured JSON response.
- `health_check() -> bool` — Verifies the API connection is healthy.

---

### 8. `PromptBuilder`

Constructs prompts for the LLM based on submission and assignment data.

| Attribute    | Type  | Description                                      |
|-------------|-------|--------------------------------------------------|
| `template`   | `str` | Base prompt template                             |

**Methods:**
- `build_grading_prompt(submission: Submission, assignment: Assignment) -> str` — Builds the complete grading prompt.
- `build_feedback_prompt(submission: Submission, result: GradingResult) -> str` — Builds a prompt for additional feedback.

---

### 9. `GradingService`

The main orchestrator that coordinates the grading pipeline.

| Attribute        | Type             | Description                              |
|-----------------|------------------|------------------------------------------|
| `llm_client`     | `LLMClient`      | LLM interface                            |
| `prompt_builder` | `PromptBuilder`  | Prompt construction utility              |
| `result_repo`    | `ResultRepository` | Storage layer for results              |

**Methods:**
- `grade(submission: Submission, assignment: Assignment) -> GradingResult` — Runs the full grading pipeline.
- `regrade(submission_id: str) -> GradingResult` — Re-grades a previously submitted submission.

---

### 10. `SubmissionRepository`

Handles persistence of submissions.

**Methods:**
- `save(submission: Submission) -> Submission`
- `find_by_id(id: str) -> Submission`
- `find_by_student(student_id: str) -> List[Submission]`
- `find_by_assignment(assignment_id: str) -> List[Submission]`
- `update_status(id: str, status: str) -> None`

---

### 11. `ResultRepository`

Handles persistence of grading results.

**Methods:**
- `save(result: GradingResult) -> GradingResult`
- `find_by_id(id: str) -> GradingResult`
- `find_by_submission(submission_id: str) -> GradingResult`
- `find_by_student(student_id: str) -> List[GradingResult]`

---

### 12. `AssignmentRepository`

Handles persistence of assignments.

**Methods:**
- `save(assignment: Assignment) -> Assignment`
- `find_by_id(id: str) -> Assignment`
- `find_all_active() -> List[Assignment]`

---

## Class Relationships

```
Assignment ─────────────────┐
    │                       │
    └──── Rubric            │
              │             │
              └──── Criterion

Submission ──── references ──── Assignment

GradingService
    ├── uses ──── LLMClient
    ├── uses ──── PromptBuilder
    └── produces ──── GradingResult
                          │
                          └──── CriterionScore ──── Criterion

Repositories:
    SubmissionRepository  ──── manages ──── Submission
    ResultRepository      ──── manages ──── GradingResult
    AssignmentRepository  ──── manages ──── Assignment
```

---

## Class Diagram (UML Notation)

```
┌──────────────────────────┐         ┌──────────────────────────┐
│         Assignment        │         │         Rubric            │
├──────────────────────────┤   1   1 ├──────────────────────────┤
│ + id: str                │─────────│ + id: str                 │
│ + title: str             │         │ + criteria: List[Criterion]│
│ + description: str       │         │ + total_weight: float     │
│ + rubric: Rubric         │         ├──────────────────────────┤
│ + language: str          │         │ + get_criteria()          │
│ + max_score: int         │         │ + validate()              │
│ + deadline: datetime     │         └──────────────────────────┘
├──────────────────────────┤                    │ 1..*
│ + get_rubric()           │                    │
│ + is_active()            │         ┌──────────▼───────────────┐
└──────────────────────────┘         │         Criterion         │
              △                      ├──────────────────────────┤
              │ references           │ + name: str               │
┌──────────────────────────┐         │ + description: str        │
│         Submission        │         │ + weight: float           │
├──────────────────────────┤         │ + max_score: int          │
│ + id: str                │         └──────────────────────────┘
│ + student_id: str        │
│ + assignment_id: str     │         ┌──────────────────────────┐
│ + language: str          │         │       GradingResult       │
│ + code: str              │         ├──────────────────────────┤
│ + submitted_at: datetime │─────────│ + id: str                 │
│ + status: str            │  grades │ + submission_id: str      │
├──────────────────────────┤         │ + total_score: float      │
│ + validate()             │         │ + feedback: str           │
│ + to_dict()              │         │ + criterion_scores: List  │
└──────────────────────────┘         │ + graded_at: datetime     │
                                     ├──────────────────────────┤
┌──────────────────────────┐         │ + get_percentage()        │
│      GradingService       │         │ + to_dict()               │
├──────────────────────────┤         │ + to_report()             │
│ + llm_client: LLMClient  │─────────└──────────────────────────┘
│ + prompt_builder: ...    │  creates
│ + result_repo: ...       │
├──────────────────────────┤
│ + grade()                │         ┌──────────────────────────┐
│ + regrade()              │         │         LLMClient         │
└──────────────────────────┘         ├──────────────────────────┤
              │ uses                 │ + model: str              │
              └─────────────────────│ + api_key: str            │
                                     │ + temperature: float      │
                                     │ + max_tokens: int         │
                                     ├──────────────────────────┤
                                     │ + generate()              │
                                     │ + generate_with_schema()  │
                                     │ + health_check()          │
                                     └──────────────────────────┘
```

---

## Design Principles Applied

- **Single Responsibility Principle (SRP):** Each class has a single, well-defined responsibility (e.g., `PromptBuilder` only builds prompts; `LLMClient` only communicates with the LLM).
- **Dependency Injection:** `GradingService` receives its dependencies (`LLMClient`, `PromptBuilder`, `ResultRepository`) via constructor injection, enabling easier testing and swapping of implementations.
- **Repository Pattern:** Data persistence is abstracted behind repository interfaces (`SubmissionRepository`, `ResultRepository`, `AssignmentRepository`).
- **Open/Closed Principle:** New LLM providers can be supported by implementing an `LLMClient` interface without modifying existing code.
