import logging

from src.api.schemas.request import GradingRequest

logger = logging.getLogger(__name__)


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
            logger.error("Validation failed — student_code is empty after sanitization")
            raise ValueError("student_code must not be empty")

        logger.debug(
            "Input validated — code length=%d chars, rubric=%s",
            len(request.student_code),
            "custom" if request.rubric else "default",
        )
        return request

    def sanitize_code(self, code: str) -> str:
        """Normalize line endings and strip surrounding whitespace."""
        return code.replace("\r\n", "\n").strip()
