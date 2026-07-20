from src.engine.response_parser import ResponseParser


class TestResponseParser:
    def _parser(self) -> ResponseParser:
        return ResponseParser()

    # --- new <RESULT> / <THINKING> format ----------------------------------

    def test_parses_result_block_with_thinking(self):
        raw = """
<THINKING>
Step 1: Code is correct on all sample inputs.
</THINKING>
<RESULT>
{
  "score": 85,
  "summary": "Good job overall.",
  "criteria": [
    {"name": "Correctness", "score": 85, "max_score": 100, "comment": "Correct."}
  ],
  "suggestions": []
}
</RESULT>
"""
        result = self._parser().parse(raw)

        assert result.score == 85.0
        assert result.feedback == "Good job overall."
        assert result.reasoning is not None and "Step 1" in result.reasoning
        assert result.feedback_detail is not None
        assert result.feedback_detail.summary == "Good job overall."
        assert result.feedback_detail.criteria[0].name == "Correctness"

    def test_parses_result_block_without_thinking(self):
        raw = """
<RESULT>
{
  "score": 70,
  "summary": "Needs improvement.",
  "criteria": [],
  "suggestions": []
}
</RESULT>
"""
        result = self._parser().parse(raw)

        assert result.score == 70.0
        assert result.reasoning is None

    def test_parses_result_block_with_full_criteria(self):
        raw = """
<RESULT>
{
  "score": 80,
  "summary": "Decent work.",
  "criteria": [
    {"name": "Correctness", "score": 40, "max_score": 50, "comment": "Mostly correct."},
    {"name": "Readability", "score": 25, "max_score": 25, "comment": "Very readable."},
    {"name": "Efficiency", "score": 15, "max_score": 25, "comment": "Could be more efficient."}
  ],
  "suggestions": ["Use a more efficient algorithm.", "Add comments."]
}
</RESULT>
"""
        result = self._parser().parse(raw)

        assert result.feedback_detail is not None
        assert len(result.feedback_detail.criteria) == 3
        assert result.feedback_detail.criteria[1].score == 25.0
        assert len(result.feedback_detail.suggestions) == 2

    def test_strips_code_fence_around_result_json(self):
        raw = """
<RESULT>
```json
{
  "score": 90,
  "summary": "Solid.",
  "criteria": [],
  "suggestions": []
}
```
</RESULT>
"""
        result = self._parser().parse(raw)

        assert result.score == 90.0
        assert result.feedback_detail is not None
        assert result.feedback_detail.summary == "Solid."

    def test_clamps_score_above_100_in_result_block(self):
        raw = (
            "<RESULT>"
            '{"score": 150, "summary": "x", "criteria": [], "suggestions": []}'
            "</RESULT>"
        )
        assert self._parser().parse(raw).score == 100.0

    def test_clamps_score_below_0_in_result_block(self):
        raw = (
            "<RESULT>"
            '{"score": -10, "summary": "x", "criteria": [], "suggestions": []}'
            "</RESULT>"
        )
        assert self._parser().parse(raw).score == 0.0

    def test_handles_decimal_score_in_result_block(self):
        raw = (
            "<RESULT>"
            '{"score": 87.5, "summary": "x", "criteria": [], "suggestions": []}'
            "</RESULT>"
        )
        assert self._parser().parse(raw).score == 87.5

    def test_invalid_json_in_result_block_falls_back_to_legacy(self):
        raw = """
<RESULT>not valid json</RESULT>
<SCORE>60</SCORE>
<FEEDBACK>Okay.</FEEDBACK>
"""
        result = self._parser().parse(raw)

        assert result.score == 60.0
        assert result.feedback_detail is None

    # --- legacy multi-tag format (back-compat) -----------------------------

    def test_legacy_format_still_parses(self):
        raw = """
<REASONING>
Step 1: Code is correct.
</REASONING>
<SCORE>85</SCORE>
<FEEDBACK>
Good job overall.
</FEEDBACK>
<FEEDBACK_JSON>
{"summary": "Good job.", "criteria": [{"name": "Correctness", "score": 85, "max_score": 100, "comment": "Correct."}], "suggestions": []}
</FEEDBACK_JSON>
"""
        result = self._parser().parse(raw)

        assert result.score == 85.0
        assert "Good job overall" in result.feedback
        assert result.reasoning is not None and "Step 1" in result.reasoning
        assert result.feedback_detail is not None
        assert result.feedback_detail.criteria[0].name == "Correctness"

    def test_legacy_returns_none_feedback_detail_on_missing_tag(self):
        raw = "<SCORE>60</SCORE>\n<FEEDBACK>Okay.</FEEDBACK>"
        assert self._parser().parse(raw).feedback_detail is None

    def test_legacy_clamps_score_above_100(self):
        raw = "<SCORE>150</SCORE>\n<FEEDBACK>Too high.</FEEDBACK>"
        assert self._parser().parse(raw).score == 100.0

    def test_legacy_clamps_score_below_0(self):
        raw = "<SCORE>-10</SCORE>\n<FEEDBACK>Negative.</FEEDBACK>"
        assert self._parser().parse(raw).score == 0.0

    def test_returns_zero_score_on_completely_unstructured_output(self):
        assert self._parser().parse("No structured output.").score == 0.0

    def test_legacy_is_case_insensitive_on_tags(self):
        raw = "<score>60</score>\n<feedback>Okay.</feedback>"
        result = self._parser().parse(raw)

        assert result.score == 60.0
        assert "Okay" in result.feedback
