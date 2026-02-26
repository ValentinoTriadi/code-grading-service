from src.api.schemas.request import GradingRequest


class InputHandler:
    """Validates and preprocesses incoming grading requests."""

    def validate(self, request: GradingRequest) -> GradingRequest:
        """Validate and sanitize the grading request.

        - Strip whitespace from student code
        - Verify required fields are non-empty
        - Normalize line endings
        """
        # TODO: Implement validation logic
        raise NotImplementedError

    def sanitize_code(self, code: str) -> str:
        """Remove potentially harmful content from student code."""
        # TODO: Implement code sanitization
        raise NotImplementedError
