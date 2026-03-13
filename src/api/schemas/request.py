from pydantic import BaseModel, Field, model_validator


class CodeFileReference(BaseModel):
    """Reference to a remote code file (e.g. S3 pre-signed URL)."""

    url: str
    filename: str | None = None


class GradingRequest(BaseModel):
    """Request model for the grading endpoint.

    Exactly one input mode must be provided:
    - inline student_code
    - single code_file_url
    - batch_code_files
    """

    problem_description: str
    student_code: str | None = None
    code_file_url: str | None = None
    batch_code_files: list[CodeFileReference] | None = None
    rubric: str | None = None
    few_shot_examples: list[dict] | None = Field(default=None)

    @model_validator(mode="after")
    def validate_input_mode(self) -> "GradingRequest":
        modes_selected = sum(
            [
                bool(self.student_code and self.student_code.strip()),
                bool(self.code_file_url and self.code_file_url.strip()),
                bool(self.batch_code_files),
            ]
        )

        if modes_selected != 1:
            raise ValueError(
                "Provide exactly one input mode: student_code, code_file_url, or batch_code_files"
            )

        if self.batch_code_files is not None and len(self.batch_code_files) == 0:
            raise ValueError("batch_code_files must not be empty")

        if not self.problem_description.strip():
            raise ValueError("problem_description must not be empty")

        return self
