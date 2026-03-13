import pytest
from pydantic import ValidationError

from src.api.schemas.request import GradingRequest
from src.engine.input_handler import InputHandler


class TestInputHandler:
    """Tests for InputHandler."""

    def test_validate_sanitizes_inline_student_code(self):
        handler = InputHandler()
        request = GradingRequest(
            student_code="print('x')\r\n",
            problem_description=" Desc ",
        )

        validated = handler.validate(request)

        assert validated.student_code == "print('x')"
        assert validated.problem_description == "Desc"

    def test_validate_raises_for_empty_inline_code(self):
        with pytest.raises(ValidationError, match="Provide exactly one input mode"):
            GradingRequest(student_code="   ", problem_description="desc")

    def test_sanitize_code_normalizes_line_endings(self):
        handler = InputHandler()

        assert handler.sanitize_code("a\r\nb\r\n") == "a\nb"
