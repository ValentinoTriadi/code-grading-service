"""The 8 prompt-engineering scenarios for the grading experiment.

Full factorial of three binary factors:
    - structured_rubric: numbered weighted criteria vs free-form paragraph
    - cot:               with_reason=True (THINKING block) vs straight to RESULT
    - few_shot:          worked examples included vs not
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    id: str
    label: str
    structured_rubric: bool
    cot: bool
    few_shot: bool


SCENARIOS: list[Scenario] = [
    Scenario("S1", "baseline",       False, False, False),
    Scenario("S2", "rubric-only",    True,  False, False),
    Scenario("S3", "cot-only",       False, True,  False),
    Scenario("S4", "fewshot-only",   False, False, True),
    Scenario("S5", "rubric+cot",     True,  True,  False),
    Scenario("S6", "rubric+fewshot", True,  False, True),
    Scenario("S7", "cot+fewshot",    False, True,  True),
    Scenario("S8", "all-on",         True,  True,  True),
]


SCENARIOS_BY_ID: dict[str, Scenario] = {s.id: s for s in SCENARIOS}
