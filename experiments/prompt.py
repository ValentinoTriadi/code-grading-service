"""Per-cell prompt assembly for the experiment.

Thin wrapper around the production `PromptOrchestrator`. The experiment
selects which rubric form (structured vs unstructured) and which
combination of CoT / few-shot to enable, then delegates assembly to
production code so the experiment-winning prompt is byte-for-byte the
same one production will send.
"""

from __future__ import annotations

from src.api.schemas.request import GradingRequest
from src.engine.prompt_orchestrator import PromptOrchestrator, StructuredPrompt
from src.prompts.builder import PromptBuilder

from experiments.scenarios import Scenario

_ORCHESTRATOR = PromptOrchestrator(prompt_builder=PromptBuilder())


def _build_request(
    scenario: Scenario,
    problem: dict,
    submission: dict,
    few_shot_pool: list[dict],
    few_shot_count: int,
) -> GradingRequest:
    rubric = problem["rubric_structured"] if scenario.structured_rubric else None
    few_shot_examples = None
    if scenario.few_shot:
        problem_examples = [
            ex for ex in few_shot_pool if ex.get("problem_id") == problem["problem_id"]
        ]
        pool = problem_examples or few_shot_pool
        few_shot_examples = [
            {k: v for k, v in ex.items() if k != "problem_id"}
            for ex in pool[:few_shot_count]
        ]
    return GradingRequest(
        problem_description=problem["description"],
        student_code=submission["code"],
        rubric=rubric,
        with_reason=scenario.cot,
        few_shot_examples=few_shot_examples,
    )


def build_structured(
    scenario: Scenario,
    problem: dict,
    submission: dict,
    few_shot_pool: list[dict],
    few_shot_count: int,
) -> StructuredPrompt:
    """Return the production `StructuredPrompt` for one experiment cell."""
    request = _build_request(
        scenario, problem, submission, few_shot_pool, few_shot_count
    )
    return _ORCHESTRATOR.build(request)


def build_prefix_suffix(
    scenario: Scenario,
    problem: dict,
    submission: dict,
    few_shot_pool: list[dict],
    few_shot_count: int,
) -> tuple[str, str]:
    sp = build_structured(scenario, problem, submission, few_shot_pool, few_shot_count)
    return sp.cacheable_prefix, sp.dynamic_suffix


def build_full_prompt(
    scenario: Scenario,
    problem: dict,
    submission: dict,
    few_shot_pool: list[dict],
    few_shot_count: int,
) -> str:
    return build_structured(
        scenario, problem, submission, few_shot_pool, few_shot_count
    ).text
