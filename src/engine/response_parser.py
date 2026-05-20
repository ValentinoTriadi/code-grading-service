import json
import logging
import re

from src.api.schemas.response import FeedbackDetail, GradingResponse

logger = logging.getLogger(__name__)


class ResponseParser:
    """Parses raw LLM output into a structured GradingResponse.

    Primary format: a single `<RESULT>{...}</RESULT>` JSON block, optionally
    preceded by `<THINKING>...</THINKING>` when reasoning was requested.

    Legacy format (fallback): separate `<SCORE>`, `<FEEDBACK>`, `<FEEDBACK_JSON>`,
    and `<REASONING>` tags. Kept for backward compatibility with cached responses.
    """

    def parse(self, raw_response: str) -> GradingResponse:
        thinking = self._extract_tag(raw_response, "THINKING")
        if thinking is None:
            thinking = self._extract_tag(raw_response, "REASONING")

        result = self._parse_result_block(raw_response)
        if result is not None:
            score, feedback_detail = result
            feedback = feedback_detail.summary if feedback_detail else ""
            logger.debug(
                "Parsed RESULT block — score=%.1f, criteria=%d, suggestions=%d, thinking=%s",
                score,
                len(feedback_detail.criteria) if feedback_detail else 0,
                len(feedback_detail.suggestions) if feedback_detail else 0,
                "present" if thinking else "absent",
            )
            return GradingResponse(
                score=score,
                feedback=feedback.strip(),
                feedback_detail=feedback_detail,
                reasoning=thinking.strip() if thinking else None,
            )

        # Legacy fallback path.
        score = self._parse_legacy_score(raw_response)
        feedback = self._extract_tag(raw_response, "FEEDBACK") or raw_response.strip()
        feedback_detail = self._parse_legacy_feedback_detail(raw_response)

        if feedback_detail is None:
            logger.warning(
                "Neither <RESULT> nor <FEEDBACK_JSON> parsed cleanly — feedback_detail will be null"
            )
        else:
            logger.debug("Parsed legacy multi-tag response — score=%.1f", score)

        return GradingResponse(
            score=score,
            feedback=feedback.strip(),
            feedback_detail=feedback_detail,
            reasoning=thinking.strip() if thinking else None,
        )

    def _parse_result_block(
        self, text: str
    ) -> tuple[float, FeedbackDetail | None] | None:
        """Extract and parse the <RESULT>{...}</RESULT> JSON block.

        Returns (score, feedback_detail) or None if the block is missing or invalid.
        """
        raw = self._extract_tag(text, "RESULT")
        if not raw:
            return None

        cleaned = self._strip_code_fence(raw.strip())

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning(
                "RESULT block is not valid JSON — falling back to legacy parser"
            )
            return None

        if not isinstance(data, dict):
            return None

        score = self._coerce_score(data.get("score"))

        try:
            feedback_detail = FeedbackDetail.model_validate(
                {
                    "summary": data.get("summary", ""),
                    "criteria": data.get("criteria", []),
                    "suggestions": data.get("suggestions", []),
                    "exemplary_points": data.get("exemplary_points", []),
                    "complexity": data.get("complexity"),
                    "confidence": data.get("confidence"),
                }
            )
        except ValueError as exc:
            logger.warning("RESULT block did not match FeedbackDetail schema: %s", exc)
            feedback_detail = None

        return score, feedback_detail

    def _extract_tag(self, text: str, tag: str) -> str | None:
        # Standard form: <TAG>content</TAG>
        match = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1)
        # Tolerant fallback: opening tag with missing `>` (e.g. `<TAG\ncontent`)
        match = re.search(
            rf"<{tag}\s*\n(.*?)</{tag}>", text, re.DOTALL | re.IGNORECASE
        )
        if match:
            logger.warning(
                "Malformed opening tag <%s> (missing '>') — using tolerant parser", tag
            )
            return match.group(1)
        return None

    @staticmethod
    def _strip_code_fence(text: str) -> str:
        """Some models wrap the JSON block in a ``` fence — strip it."""
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z0-9_]*\s*\n?", "", text)
            text = re.sub(r"\n?```\s*$", "", text)
        return text.strip()

    @staticmethod
    def _coerce_score(value: object) -> float:
        if isinstance(value, (int, float)):
            return max(0.0, min(100.0, float(value)))
        if isinstance(value, str):
            number_match = re.search(r"-?[\d]+(?:[.,]\d+)?", value.strip())
            if number_match:
                try:
                    return max(
                        0.0,
                        min(100.0, float(number_match.group().replace(",", "."))),
                    )
                except ValueError:
                    pass
        return 0.0

    # --- legacy parsing helpers (kept for back-compat with old multi-tag output) ---

    def _parse_legacy_score(self, text: str) -> float:
        raw = self._extract_tag(text, "SCORE")
        if not raw:
            return 0.0
        return self._coerce_score(raw)

    def _parse_legacy_feedback_detail(self, text: str) -> FeedbackDetail | None:
        raw = self._extract_tag(text, "FEEDBACK_JSON")
        if not raw:
            return None
        try:
            data = json.loads(self._strip_code_fence(raw.strip()))
            return FeedbackDetail.model_validate(data)
        except (json.JSONDecodeError, ValueError):
            return None
