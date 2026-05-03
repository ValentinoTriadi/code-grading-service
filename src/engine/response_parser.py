import json
import logging
import re

from src.api.schemas.response import FeedbackDetail, GradingResponse

logger = logging.getLogger(__name__)


class ResponseParser:
    """Parses raw LLM output into a structured GradingResponse."""

    def parse(self, raw_response: str) -> GradingResponse:
        """Extract score, feedback, feedback_detail, and optional reasoning.

        Expected tags in the response:
          <SCORE>75</SCORE>
          <FEEDBACK>...</FEEDBACK>
          <FEEDBACK_JSON>{ ... }</FEEDBACK_JSON>
          <REASONING>...</REASONING>  (optional, only when with_reason=True)
        """
        score = self._parse_score(raw_response)
        feedback = self._extract_tag(raw_response, "FEEDBACK") or raw_response.strip()
        feedback_detail = self._parse_feedback_detail(raw_response)
        reasoning = self._extract_tag(raw_response, "REASONING")

        logger.debug(
            "Parsed response — score=%.1f, feedback_detail=%s, reasoning=%s",
            score,
            "present" if feedback_detail else "missing",
            "present" if reasoning else "absent",
        )

        if feedback_detail is None:
            logger.warning(
                "FEEDBACK_JSON tag missing or invalid — feedback_detail will be null"
            )

        return GradingResponse(
            score=score,
            feedback=feedback.strip(),
            feedback_detail=feedback_detail,
            reasoning=reasoning.strip() if reasoning else None,
        )

    def _extract_tag(self, text: str, tag: str) -> str | None:
        # Normal: <TAG>content</TAG>
        match = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1)
        # Fallback: LLM omitted the closing `>` → <TAG\ncontent</TAG>
        match = re.search(rf"<{tag}\s*\n(.*?)</{tag}>", text, re.DOTALL | re.IGNORECASE)
        if match:
            logger.warning(
                "Malformed opening tag <%s> (missing '>') — using fallback parser", tag
            )
            return match.group(1)
        return None

    def _parse_score(self, text: str) -> float:
        raw = self._extract_tag(text, "SCORE")
        if raw:
            number_match = re.search(r"-?[\d]+(?:[.,]\d+)?", raw.strip())
            if number_match:
                try:
                    score = float(number_match.group().replace(",", "."))
                    return max(0.0, min(100.0, score))
                except ValueError:
                    pass
        return 0.0

    def _parse_feedback_detail(self, text: str) -> FeedbackDetail | None:
        raw = self._extract_tag(text, "FEEDBACK_JSON")
        if not raw:
            return None
        try:
            data = json.loads(raw.strip())
            return FeedbackDetail.model_validate(data)
        except (json.JSONDecodeError, ValueError):
            return None
