from src.api.schemas.request import GradingRequest


class InputHandler:
    """Validates and sanitizes incoming grading requests."""

    def validate(self, request: GradingRequest) -> GradingRequest:
        """Sanitize and verify the grading request in-place.

        - Normalize line endings
        - Strip surrounding whitespace
        - Ensure required fields are non-empty
        """
        request.problem_description = request.problem_description.strip()
        request.student_code = self.sanitize_code(request.student_code)

        if not request.student_code:
            raise ValueError("student_code must not be empty")

        return request

    def sanitize_code(self, code: str) -> str:
        """Normalize line endings and strip surrounding whitespace."""
        return code.replace("\r\n", "\n").strip()
