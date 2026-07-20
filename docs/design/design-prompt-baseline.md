# Design Prompt Baseline

## Objective

Define a predictable prompt design that is modular, auditable, and reusable using existing templates in `src/prompts/templates/`.

## Prompt Components

Baseline prompt is composed from these templates:

- `system.txt`
- `rubric.txt`
- `cot_instruction.txt`
- `few_shot.txt`

## Assembly Contract

`PromptOrchestrator.build(request)` must produce one final string in this order:

1. System role and grading behavior
2. Rubric instructions (custom rubric if provided)
3. Reasoning/analysis instruction block
4. Few-shot examples (custom examples if provided)
5. Task payload containing:

- problem description
- student code (from inline payload or normalized URL-based parser output)

## Template Rules

- Templates are plain UTF-8 text loaded through `PromptBuilder.load_template`.
- Placeholder standard:
  - `{{rubric}}` for rubric injection in `rubric.txt`.
- Few-shot custom examples should be rendered in stable format:
  - Example #
  - Input/problem
  - Code
  - Expected scoring rationale

## Prompt Quality Baseline

- Deterministic section order.
- Explicit scoring constraints (numeric score expected).
- Explicit output schema cues for parser compatibility.
- Minimize ambiguity and avoid contradictory instructions across sections.

## Suggested Output Contract for Parsing

To simplify `ResponseParser`, instruct model to output clear blocks, for example:

- `Score: <0-100>`
- `Feedback:`
- `Reasoning:`

This format should be enforced in template text so parsing can remain stable.

## Safety and Scope Guardrails

- Prompt must evaluate only submitted code/problem context.
- Avoid unrelated policy or off-task content.
- Keep grading criteria grounded in rubric and assignment description.

## Versioning Baseline

- Treat each template as versioned prompt artifact.
- Any template change should:
  - include changelog note in commit/PR
  - trigger prompt regression tests for parser compatibility

## Definition of Done

- `PromptOrchestrator.build` implemented with deterministic composition.
- Custom rubric and custom few-shot examples both supported.
- Prompt includes explicit machine-parseable output instructions.
- Prompt-related unit tests verify section ordering and injection behavior.
