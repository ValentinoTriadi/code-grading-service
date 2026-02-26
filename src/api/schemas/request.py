from pydantic import BaseModel


class GradingRequest(BaseModel):
    """Request model for the grading endpoint."""

    student_code: str
    problem_description: str
    rubric: str | None = None
    few_shot_examples: list[dict] | None = None
