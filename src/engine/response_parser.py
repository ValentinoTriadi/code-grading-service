from src.api.schemas.response import GradingResponse


class ResponseParser:
    """Parses raw LLM output into structured grading results."""

    def parse(self, raw_response: str) -> GradingResponse:
        """Extract score, feedback, and reasoning from LLM response.

        Expected LLM output format:
        - Reasoning/CoT section
        - Numeric score
        - Qualitative feedback
        """
        # TODO: Implement response parsing logic
        raise NotImplementedError
