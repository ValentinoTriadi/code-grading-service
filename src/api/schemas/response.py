from pydantic import BaseModel


class GradingResponse(BaseModel):
    """Response model for the grading endpoint."""

    score: float
    feedback: str
    reasoning: str  # Chain of Thought reasoning from LLM
    raw_response: str | None = None
