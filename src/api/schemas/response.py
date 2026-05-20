from pydantic import BaseModel, ConfigDict, Field


class CriterionResult(BaseModel):
    """Score and comment for a single rubric criterion."""

    name: str = Field(description="Criterion name from the rubric.")
    score: float = Field(description="Points awarded for this criterion.")
    max_score: float = Field(description="Maximum points available for this criterion.")
    comment: str = Field(description="Evaluator's comment for this criterion.")


class ComplexityEstimate(BaseModel):
    """Estimated time/space complexity of the submitted code."""

    time: str = Field(description="Big-O time complexity, e.g. 'O(n)' or 'unknown'.")
    space: str = Field(description="Big-O space complexity, e.g. 'O(1)' or 'unknown'.")


class FeedbackDetail(BaseModel):
    """Structured breakdown of the grading feedback."""

    summary: str = Field(description="Overall grading summary.")
    criteria: list[CriterionResult] = Field(
        description="Per-criterion score and comment."
    )
    suggestions: list[str] = Field(
        default_factory=list,
        description="Specific, actionable improvement suggestions.",
    )
    exemplary_points: list[str] = Field(
        default_factory=list,
        description="Things the submission did well. Empty if nothing stands out.",
    )
    complexity: ComplexityEstimate | None = Field(
        default=None,
        description="Estimated time/space complexity. None if not applicable.",
    )
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Grader's confidence in the score, 0.0 to 1.0.",
    )


class GradingResponse(BaseModel):
    """Grading result for a single code submission."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "score": 85.0,
                "feedback": "The function works correctly. Parameter names could be more descriptive.",
                "feedback_detail": {
                    "summary": "The function works correctly. Parameter names could be more descriptive.",
                    "criteria": [
                        {
                            "name": "Correctness",
                            "score": 50.0,
                            "max_score": 50.0,
                            "comment": "Produces the correct output for every test case.",
                        },
                        {
                            "name": "Readability",
                            "score": 20.0,
                            "max_score": 25.0,
                            "comment": "Function name is clear, but parameter names `a` and `b` are not descriptive.",
                        },
                        {
                            "name": "Efficiency",
                            "score": 15.0,
                            "max_score": 25.0,
                            "comment": "The approach is already efficient for the input sizes given.",
                        },
                    ],
                    "suggestions": [
                        "Rename parameters `a` and `b` to something descriptive like `lhs` and `rhs`, or to domain-specific names if the problem implies them."
                    ],
                },
                "reasoning": None,
            }
        }
    )

    score: float = Field(description="Numeric score between 0 and 100.")
    feedback: str = Field(description="Plain-text constructive feedback.")
    feedback_detail: FeedbackDetail | None = Field(
        default=None,
        description="Structured per-criterion breakdown. None if the LLM did not produce parseable JSON.",
    )
    reasoning: str | None = Field(
        default=None,
        description="LLM chain-of-thought reasoning. Only present when with_reason=true.",
    )
