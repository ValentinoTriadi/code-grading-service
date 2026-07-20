"""The 8 prompt-engineering scenarios for the grading experiment.

Full factorial of three binary factors:
    - structured_rubric: numbered weighted criteria vs free-form paragraph
    - cot:               with_reason=True (THINKING block) vs straight to RESULT
    - few_shot:          worked examples included vs not
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    id: str
    label: str
    structured_rubric: bool
    cot: bool
    few_shot: bool


ALL_SCENARIOS: list[Scenario] = [
    Scenario("S1", "baseline",       False, False, False),
    Scenario("S2", "rubric-only",    True,  False, False),
    Scenario("S3", "cot-only",       False, True,  False),
    Scenario("S4", "fewshot-only",   False, False, True),
    Scenario("S5", "rubric+cot",     True,  True,  False),
    Scenario("S6", "rubric+fewshot", True,  False, True),
    Scenario("S7", "cot+fewshot",    False, True,  True),
    Scenario("S8", "all-on",         True,  True,  True),
]

# Lookups always resolve against the full grid so state written by a full run
# (e.g. best_scenario_id) still maps even under a filtered run.
SCENARIOS_BY_ID: dict[str, Scenario] = {s.id: s for s in ALL_SCENARIOS}


def _active_scenarios() -> list[Scenario]:
    """Restrict the run to EXPERIMENT_SCENARIOS (comma-separated ids) if set.

    Used for the held-out final test, which grades only the winning config
    (e.g. EXPERIMENT_SCENARIOS=S8) instead of the full 8-scenario grid.
    """
    raw = os.environ.get("EXPERIMENT_SCENARIOS", "").strip()
    if not raw:
        return list(ALL_SCENARIOS)
    wanted = [tok.strip() for tok in raw.split(",") if tok.strip()]
    unknown = [w for w in wanted if w not in SCENARIOS_BY_ID]
    if unknown:
        raise ValueError(
            f"EXPERIMENT_SCENARIOS has unknown id(s): {unknown}. "
            f"Valid ids: {list(SCENARIOS_BY_ID)}"
        )
    return [SCENARIOS_BY_ID[w] for w in wanted]


# The scenarios the runner actually iterates (Phase 1 grid + submit/ingest).
SCENARIOS: list[Scenario] = _active_scenarios()
