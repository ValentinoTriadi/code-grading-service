# Design Prompt Baseline

## Overview

This document defines the baseline prompt designs used in the **Code Grading Service** to interact with LLMs. Well-structured prompts are critical to achieving consistent, accurate, and fair automated code grading. Each prompt template is designed to be reproducible, rubric-aware, and produce structured output.

---

## Prompt Design Principles

1. **Clarity** — Prompts clearly specify what the LLM is expected to do.
2. **Structured Output** — Prompts request responses in a machine-parseable format (JSON).
3. **Rubric-Driven** — Grading prompts embed the rubric so the LLM evaluates based on defined criteria.
4. **Reproducibility** — Prompts use low temperature settings to minimize hallucination and variance.
5. **Role Assignment** — Prompts assign the LLM a specific expert role (e.g., "You are an experienced software engineering instructor").

---

## Prompt Templates

### 1. System Prompt (Global Context)

Used as the system-level instruction for all grading tasks.

```
You are an experienced software engineering instructor and code reviewer.
Your task is to evaluate student code submissions objectively and fairly, 
strictly following the provided grading rubric.

You must:
- Evaluate ONLY based on the provided rubric criteria.
- Provide constructive, specific, and actionable feedback.
- Never penalize students for stylistic choices not mentioned in the rubric.
- Always return your response as valid JSON.
- If the code is empty or unreadable, assign a score of 0 with an appropriate explanation.
```

---

### 2. Code Grading Prompt

This is the primary prompt used when grading a student's code submission.

**Prompt Template:**

```
You are grading a student's code submission for the following assignment.

=== ASSIGNMENT ===
Title: {assignment_title}
Description:
{assignment_description}
Expected Language: {expected_language}

=== GRADING RUBRIC ===
{rubric_json}

=== STUDENT SUBMISSION ===
Language: {submission_language}
Code:
```{submission_language}
{student_code}
```

=== INSTRUCTIONS ===
Evaluate the student's code based on each criterion in the rubric.
For each criterion:
1. Assign a score between 0 and the maximum score for that criterion.
2. Provide a specific explanation of why you assigned that score.

Return your evaluation as a JSON object in the following format:
{
  "criterion_scores": [
    {
      "criterion_name": "<criterion name>",
      "score": <numeric score>,
      "max_score": <maximum score>,
      "feedback": "<specific feedback for this criterion>"
    }
  ],
  "total_score": <sum of all scores>,
  "overall_feedback": "<overall feedback summarizing the submission's strengths and areas for improvement>"
}

Ensure your JSON is valid and complete. Do not include any text outside of the JSON object.
```

**Rubric JSON Format (embedded inside the prompt):**

```json
[
  {
    "criterion_name": "Correctness",
    "description": "The code produces the correct output for all test cases.",
    "max_score": 40
  },
  {
    "criterion_name": "Code Quality",
    "description": "The code is clean, readable, and follows best practices.",
    "max_score": 30
  },
  {
    "criterion_name": "Efficiency",
    "description": "The code uses appropriate algorithms and data structures.",
    "max_score": 20
  },
  {
    "criterion_name": "Documentation",
    "description": "The code contains meaningful comments and docstrings.",
    "max_score": 10
  }
]
```

---

### 3. Detailed Feedback Prompt

Used after grading to generate more elaborate, student-friendly feedback.

**Prompt Template:**

```
A student has submitted code for the assignment: "{assignment_title}".
The student received a score of {total_score}/{max_score}.

Below is their submission and grading result.

=== STUDENT CODE ===
```{submission_language}
{student_code}
```

=== GRADING RESULT ===
{grading_result_json}

=== INSTRUCTIONS ===
Based on the grading result, write detailed, encouraging, and constructive feedback for the student.
- Highlight what they did well.
- Explain clearly what needs improvement and how they can fix it.
- Be encouraging and educational in tone.
- Keep the feedback under 300 words.

Return your feedback as plain text (not JSON).
```

---

### 4. Code Plagiarism Detection Prompt

Used to detect suspicious similarity between two student submissions.

**Prompt Template:**

```
You are a code plagiarism detection expert. Compare the following two code submissions.

=== SUBMISSION A (Student: {student_a_id}) ===
```{language}
{code_a}
```

=== SUBMISSION B (Student: {student_b_id}) ===
```{language}
{code_b}
```

=== INSTRUCTIONS ===
Analyze whether Submission B appears to be copied or derived from Submission A (or vice versa).
Consider:
- Structural similarity
- Variable name patterns
- Logic flow
- Comments and formatting

Return your analysis as a JSON object in the following format:
{
  "similarity_score": <float between 0 and 1>,
  "is_suspicious": <true or false>,
  "reasoning": "<explanation of your analysis>",
  "common_patterns": ["<pattern 1>", "<pattern 2>"]
}
```

---

### 5. Code Review Prompt (Optional Enhancement)

Used to provide code review-style feedback independent of grading.

**Prompt Template:**

```
You are a senior software engineer performing a code review.
Review the following code written in {language} and provide professional feedback.

=== CODE ===
```{language}
{student_code}
```

Focus on:
1. Potential bugs or edge cases
2. Code readability and maintainability
3. Performance considerations
4. Security concerns (if applicable)

Return your review as a JSON object:
{
  "issues": [
    {
      "severity": "<critical|warning|suggestion>",
      "line": <line number or null>,
      "description": "<description of the issue>",
      "suggestion": "<recommended fix>"
    }
  ],
  "summary": "<overall code review summary>"
}
```

---

## Prompt Configuration

| Parameter     | Recommended Value | Description                                           |
|--------------|-------------------|-------------------------------------------------------|
| `temperature` | `0.1`             | Low randomness for consistent grading                 |
| `top_p`       | `0.9`             | Nucleus sampling threshold                            |
| `max_tokens`  | `2048`            | Sufficient for detailed rubric scoring + feedback     |
| `model`       | `gpt-4o` / `gemini-1.5-pro` | High-capability model for accurate evaluation |

---

## Expected LLM Response Schema

All grading responses must conform to the following JSON schema for downstream parsing:

```json
{
  "type": "object",
  "required": ["criterion_scores", "total_score", "overall_feedback"],
  "properties": {
    "criterion_scores": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["criterion_name", "score", "max_score", "feedback"],
        "properties": {
          "criterion_name": { "type": "string" },
          "score": { "type": "number" },
          "max_score": { "type": "number" },
          "feedback": { "type": "string" }
        }
      }
    },
    "total_score": { "type": "number" },
    "overall_feedback": { "type": "string" }
  }
}
```

---

## Prompt Versioning

All prompt templates are versioned to ensure reproducibility and auditability:

| Version | Date       | Changes                                               |
|---------|------------|-------------------------------------------------------|
| `v1.0`  | 2025-01-01 | Initial baseline grading prompt                       |
| `v1.1`  | 2025-02-01 | Added plagiarism detection prompt                     |
| `v1.2`  | 2025-03-01 | Added structured JSON schema enforcement              |

Prompts are stored in `prompts/` directory and loaded at runtime to allow updates without code changes.

---

## Prompt Anti-Patterns to Avoid

- ❌ **Vague instructions:** "Grade this code" — LLM may invent its own criteria.
- ❌ **No structured output requirement:** Without JSON format, parsing becomes unreliable.
- ❌ **High temperature:** Values above 0.5 produce inconsistent scores for identical submissions.
- ❌ **Missing rubric:** Without rubric context, the LLM cannot grade fairly or consistently.
- ❌ **Excessive token limits:** Prompts that are too long may exceed context windows; keep prompts concise.
