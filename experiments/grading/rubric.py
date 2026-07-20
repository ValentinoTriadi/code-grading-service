"""Parse the per-problem rubric_structured string into typed criteria.

Format expected in problems.json::rubric_structured:

    1. Correctness (60%): description...
    2. Code Quality (25%): description...
    3. Efficiency (15%): description...

Weights are taken as the criterion's max_score on a 0–100 scale, so they sum
to 100 per problem (validated by `parse`). The grader and worksheet tools
consume the parsed criteria so per-criterion entry matches what the LLM is
scored against in the experiment.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


_CRITERION_RE = re.compile(
    r"^\s*\d+\.\s+(?P<name>[^()]+?)\s*\((?P<weight>\d+)%\):\s*(?P<desc>.+)$"
)


@dataclass(frozen=True)
class Criterion:
    name: str
    max_score: int
    description: str


def parse(rubric_structured: str) -> list[Criterion]:
    """Parse a rubric_structured string into Criterion objects.

    Raises ValueError if the rubric is malformed or weights don't sum to 100.
    """
    criteria: list[Criterion] = []
    for raw_line in rubric_structured.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = _CRITERION_RE.match(line)
        if not match:
            continue
        criteria.append(
            Criterion(
                name=match.group("name").strip(),
                max_score=int(match.group("weight")),
                description=match.group("desc").strip(),
            )
        )
    if not criteria:
        raise ValueError(f"No criteria parsed from rubric:\n{rubric_structured}")
    total = sum(c.max_score for c in criteria)
    if total != 100:
        raise ValueError(
            f"Rubric weights sum to {total}, expected 100. "
            f"Criteria: {[(c.name, c.max_score) for c in criteria]}"
        )
    return criteria
