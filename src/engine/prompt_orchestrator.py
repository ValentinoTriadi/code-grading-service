import logging
from dataclasses import dataclass

from src.api.schemas.request import GradingRequest
from src.prompts.builder import PromptBuilder

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StructuredPrompt:
    """A prompt split into a cacheable prefix and a per-call dynamic suffix.

    Prefix = system + rubric + [CoT] + [few-shot] + output-format header.
            Identical across all submissions for a given configuration —
            this is what providers should cache.
    Suffix = task section (problem description + student code).
            Varies per call and must NOT be in the cache target.
    """

    cacheable_prefix: str
    dynamic_suffix: str

    @property
    def text(self) -> str:
        return f"{self.cacheable_prefix}\n\n{self.dynamic_suffix}"

    def __str__(self) -> str:
        return self.text

    def __contains__(self, item: object) -> bool:
        return item in self.text


_RESULT_SCHEMA = """\
<RESULT>
{
  "score": <integer or float between 0 and 100, at most one decimal place>,
  "summary": "<2-4 sentence Markdown headline of the grading. This is what a student sees first.>",
  "criteria": [
    {
      "name": "<criterion name from the rubric, EXACT spelling>",
      "score": <points awarded for this criterion>,
      "max_score": <maximum points available for this criterion>,
      "comment": "<Markdown explanation. Use backticks for `identifiers`, **bold** for key points.>"
    }
  ],
  "suggestions": [
    "<Specific, actionable improvement. Reference the language's standard library, an idiom, or a pattern when relevant. Empty array if the code is already clean.>"
  ],
  "exemplary_points": [
    "<Short bullet describing something the student did well. Empty array if nothing stands out.>"
  ],
  "complexity": {
    "time": "<Big-O time complexity, e.g. 'O(n)' or 'unknown'>",
    "space": "<Big-O space complexity, e.g. 'O(1)' or 'unknown'>"
  },
  "confidence": <float between 0.0 and 1.0 — your confidence in this score>
}
</RESULT>"""


_OUTPUT_RULES_HEADER = (
    "# Output format (STRICT)\n"
    "You MUST end your response with a single `<RESULT>...</RESULT>` block "
    "containing valid JSON that matches the schema below. Nothing may follow "
    "the closing `</RESULT>` tag.\n\n"
    "Hard requirements:\n"
    "- The JSON must parse with a standard JSON parser. No trailing commas, "
    "no comments, no `undefined`.\n"
    "- All string values must be valid JSON strings — escape `\"`, `\\`, and "
    "newlines properly.\n"
    "- `score` is the overall score on a 0–100 scale and MUST equal the sum of "
    "the per-criterion `score` values when the rubric weights are normalized to 100.\n"
    "- The `criteria` array MUST list every rubric criterion in the order they "
    "appear in the rubric, with `name` matching the rubric exactly.\n"
    "- `summary`, `comment`, `suggestions`, and `exemplary_points` entries are all Markdown.\n"
    "- `exemplary_points` is an array of short bullets — empty array if nothing stands out.\n"
    "- `complexity` is an object with `time` and `space` fields, each a Big-O string "
    "or `\"unknown\"`. Estimate from the code as written, not from the canonical solution.\n"
    "- `confidence` is a float in [0.0, 1.0] reflecting how sure you are of the score. "
    "Lower it when the code is ambiguous, partial, or relies on assumptions you had to make.\n"
    "- Do NOT wrap the `<RESULT>` block in code fences. Do NOT add prose after "
    "`</RESULT>`.\n"
)

_OUTPUT_FORMAT_WITH_REASON = (
    _OUTPUT_RULES_HEADER
    + "- Before `<RESULT>`, emit a `<THINKING>...</THINKING>` block containing "
    "your step-by-step reasoning. The thinking block is for analysis only — "
    "do NOT put the final score there.\n\n"
    "Response shape (in this exact order):\n\n"
    "<THINKING>\n"
    "[Your step-by-step reasoning, following the chain-of-thought instructions above.]\n"
    "</THINKING>\n\n"
    + _RESULT_SCHEMA
)

_OUTPUT_FORMAT_WITHOUT_REASON = (
    _OUTPUT_RULES_HEADER
    + "- Do NOT include any `<THINKING>` block — go straight to `<RESULT>`.\n\n"
    "Response shape:\n\n"
    + _RESULT_SCHEMA
)


class PromptOrchestrator:
    """Constructs the full grading prompt by combining all sections."""

    def __init__(self, prompt_builder: PromptBuilder) -> None:
        self.prompt_builder = prompt_builder

    def build(self, request: GradingRequest) -> StructuredPrompt:
        """Assemble the prompt as a (cacheable_prefix, dynamic_suffix) pair.

        Prefix sections (stable across runs of the same configuration):
        1. System prompt
        2. Rubric (custom or default)
        3. Chain-of-thought instruction (only when with_reason=True)
        4. Few-shot examples (only when provided)
        5. Output-format instruction (single <RESULT> JSON block)

        Suffix (per-call):
        6. Task — problem description + student code
        """
        prefix_sections: list[str] = [
            self.prompt_builder.build_system_prompt(),
            self.prompt_builder.build_rubric_section(request.rubric),
        ]

        if request.with_reason:
            prefix_sections.append(self.prompt_builder.build_cot_instruction())

        few_shot = self.prompt_builder.build_few_shot_section(request.few_shot_examples)
        if few_shot:
            prefix_sections.append(few_shot)

        prefix_sections.append(
            _OUTPUT_FORMAT_WITH_REASON
            if request.with_reason
            else _OUTPUT_FORMAT_WITHOUT_REASON
        )

        cacheable_prefix = "\n\n".join(prefix_sections)
        dynamic_suffix = self._build_task_section(request)
        logger.debug(
            "Prompt built — prefix=%d chars, suffix=%d chars",
            len(cacheable_prefix),
            len(dynamic_suffix),
        )
        return StructuredPrompt(
            cacheable_prefix=cacheable_prefix, dynamic_suffix=dynamic_suffix
        )

    def _build_task_section(self, request: GradingRequest) -> str:
        return (
            f"# Submission to grade\n\n"
            f"## Problem\n{request.problem_description}\n\n"
            f"## Student code\n```\n{request.student_code}\n```"
        )
