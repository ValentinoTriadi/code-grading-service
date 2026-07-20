"""One-off sanity check for the softened rubric.

Grades three submissions that the old rubric scored harshly on syntax errors:
- sum_array_i1 (Python — missing `:` after def, SyntaxError)
- dijkstra_h1  (C++    — missing `#include <queue>`, compile error)
- pool_h2      (Go     — missing `import "sync"`, compile error)

Under the new rubric these should land within ~5 of the human score
(localized syntax / compile defect capped at −5 via Code Quality, not a
Correctness zero).

Run with:
    uv run python -m experiments.sanity_grade
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from src.api.dependencies import get_llm_provider
from src.api.schemas.request import GradingRequest
from src.config.settings import settings
from src.engine.input_handler import InputHandler
from src.engine.llm_interface import LLMInterface, RequestRateLimiter
from src.engine.prompt_orchestrator import PromptOrchestrator
from src.engine.response_parser import ResponseParser
from src.prompts.builder import PromptBuilder
from src.services.grading_service import GradingService

DATASET = Path("experiments/dataset")
TARGETS = ["sum_array_i1", "dijkstra_h1", "pool_h2"]


def build_service() -> GradingService:
    """Wire the production grading service standalone (no FastAPI)."""
    provider = get_llm_provider(cfg=settings)
    return GradingService(
        input_handler=InputHandler(),
        prompt_orchestrator=PromptOrchestrator(prompt_builder=PromptBuilder()),
        llm_interface=LLMInterface(
            provider=provider,
            rate_limiter=RequestRateLimiter(
                max_requests_per_minute=settings.llm_requests_per_minute
            ),
        ),
        response_parser=ResponseParser(),
    )


def load_dataset() -> tuple[dict[str, dict], dict[str, dict]]:
    problems = {
        p["problem_id"]: p
        for p in json.loads((DATASET / "problems.json").read_text())
    }
    submissions = {
        s["submission_id"]: s
        for s in json.loads((DATASET / "submissions.json").read_text())
    }
    return problems, submissions


async def grade_one(
    service: GradingService,
    problem: dict,
    submission: dict,
) -> None:
    request = GradingRequest(
        problem_description=problem["description"],
        student_code=submission["code"],
        rubric=problem["rubric_structured"],
        with_reason=True,
        few_shot_examples=None,
    )
    result = await service.grade(request)
    human = submission["human_score"]
    delta = human - result.score
    print(f"\n=== {submission['submission_id']} "
          f"({problem['problem_id']} {problem['name']}) ===")
    print(f"human score:  {human:5.1f}")
    print(f"llm score:    {result.score:5.1f}")
    print(f"Δ (human-llm):{delta:+5.1f}")
    print("per-criterion:")
    for c in result.criteria:
        print(f"  - {c.name:<22} {c.score:5.1f}/{c.max_score:<3}  {c.comment[:90]}")
    print(f"summary: {result.summary}")


async def main() -> None:
    problems, submissions = load_dataset()
    service = build_service()
    print(f"Provider: {settings.llm_provider}  Model: {settings.llm_model_name}")
    print(f"Targets: {', '.join(TARGETS)}")
    for sid in TARGETS:
        sub = submissions[sid]
        prob = problems[sub["problem_id"]]
        await grade_one(service, prob, sub)


if __name__ == "__main__":
    asyncio.run(main())
