from pydantic import BaseModel, ConfigDict, Field, model_validator


class InlineGradingRequest(BaseModel):
    """Request body for the inline grading endpoint."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "problems": "Buatlah fungsi yang menerima dua bilangan bulat dan mengembalikan jumlahnya.",
                "code": "def tambah(a, b):\n    return a + b",
                "rubric": (
                    "1. Kebenaran (70%): Fungsi menghasilkan hasil yang benar untuk semua kasus.\n"
                    "2. Keterbacaan (30%): Penamaan variabel jelas dan kode mudah dipahami."
                ),
                "with_reason": False,
            }
        }
    )

    problems: str = Field(description="Problem statement given to students.")
    code: str = Field(description="Student source code to be graded.")
    rubric: str | None = Field(
        default=None,
        description="Custom grading rubric. Uses a sensible default if omitted.",
    )
    with_reason: bool = Field(
        default=False,
        description="If true, includes the LLM chain-of-thought reasoning in the response.",
    )

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
