from pydantic import BaseModel, ConfigDict, Field


class CriterionResult(BaseModel):
    """Score and comment for a single rubric criterion."""

    name: str = Field(description="Criterion name from the rubric.")
    score: float = Field(description="Points awarded for this criterion.")
    max_score: float = Field(description="Maximum points available for this criterion.")
    comment: str = Field(description="Evaluator's comment for this criterion.")


class FeedbackDetail(BaseModel):
    """Structured breakdown of the grading feedback."""

    summary: str = Field(description="Overall grading summary.")
    criteria: list[CriterionResult] = Field(description="Per-criterion score and comment.")
    suggestions: list[str] = Field(
        default_factory=list,
        description="Specific, actionable improvement suggestions.",
    )


class GradingResponse(BaseModel):
    """Grading result for a single code submission."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "score": 85.0,
                "feedback": "Fungsi bekerja dengan benar. Penamaan variabel bisa lebih deskriptif.",
                "feedback_detail": {
                    "summary": "Fungsi bekerja dengan benar. Penamaan variabel bisa lebih deskriptif.",
                    "criteria": [
                        {
                            "name": "Kebenaran",
                            "score": 50.0,
                            "max_score": 50.0,
                            "comment": "Menghasilkan output yang benar untuk semua kasus.",
                        },
                        {
                            "name": "Keterbacaan",
                            "score": 20.0,
                            "max_score": 25.0,
                            "comment": "Nama fungsi jelas, tapi nama parameter bisa lebih deskriptif.",
                        },
                        {
                            "name": "Efisiensi",
                            "score": 15.0,
                            "max_score": 25.0,
                            "comment": "Pendekatan sudah efisien.",
                        },
                    ],
                    "suggestions": ["Gunakan nama parameter yang lebih deskriptif seperti `bilangan1` dan `bilangan2`."],
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
