from src.api.schemas.request import GradingRequest


class InputHandler:
    """Validates and preprocesses incoming grading requests."""

    def validate(self, request: GradingRequest) -> GradingRequest:
        """Validate and sanitize the grading request.

        - Strip whitespace from student code
        - Verify required fields are non-empty
        - Normalize line endings
        """
        request.problem_description = request.problem_description.strip()

        if request.student_code is not None:
            sanitized = self.sanitize_code(request.student_code)
            if not sanitized.strip():
                raise ValueError("student_code must not be empty")
            request.student_code = sanitized

        if request.code_file_url is not None:
            request.code_file_url = request.code_file_url.strip()

        return request

    def sanitize_code(self, code: str) -> str:
        """Remove potentially harmful content from student code."""
        return code.replace("\r\n", "\n").strip()
