from pydantic import BaseModel, Field, model_validator


class InlineGradingRequest(BaseModel):
    """Request model for grading inline code submitted as JSON."""

    problems: str
    code: str
    rubric: str | None = None
    with_reason: bool = False

    @model_validator(mode="after")
    def validate_fields(self) -> "InlineGradingRequest":
        if not self.problems.strip():
            raise ValueError("problems must not be empty")
        if not self.code.strip():
            raise ValueError("code must not be empty")
        return self


class GradingRequest(BaseModel):
    """Internal request model used by the grading engine."""

    problem_description: str
    student_code: str
    rubric: str | None = None
    with_reason: bool = False
    few_shot_examples: list[dict] | None = Field(default=None)

    @model_validator(mode="after")
    def validate_fields(self) -> "GradingRequest":
        if not self.problem_description.strip():
            raise ValueError("problem_description must not be empty")
        if not self.student_code.strip():
            raise ValueError("student_code must not be empty")
        return self
