from pydantic import BaseModel


class GradingResponse(BaseModel):
    """Response model for single-submission grading (inline or file)."""

    score: float
    feedback: str
    reasoning: str | None = None  # Only present when with_reason=True
