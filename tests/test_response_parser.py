from src.engine.response_parser import ResponseParser


class TestResponseParser:
    def _parser(self) -> ResponseParser:
        return ResponseParser()

    def test_parse_extracts_score_feedback_reasoning(self):
        raw = """
<REASONING>
Step 1: Code is correct.
</REASONING>
<SCORE>85</SCORE>
<FEEDBACK>
Good job overall.
</FEEDBACK>
<FEEDBACK_JSON>
{"summary": "Good job.", "criteria": [{"name": "Kebenaran", "score": 85, "max_score": 100, "comment": "Correct."}], "suggestions": []}
</FEEDBACK_JSON>
"""
        result = self._parser().parse(raw)

        assert result.score == 85.0
        assert "Good job overall" in result.feedback
        assert result.reasoning is not None and "Step 1" in result.reasoning
        assert result.feedback_detail is not None
        assert result.feedback_detail.summary == "Good job."
        assert result.feedback_detail.criteria[0].name == "Kebenaran"

    def test_parse_without_reasoning_tag(self):
        raw = "<SCORE>70</SCORE>\n<FEEDBACK>Needs improvement.</FEEDBACK>\n<FEEDBACK_JSON>{\"summary\": \"Needs improvement.\", \"criteria\": [], \"suggestions\": []}</FEEDBACK_JSON>"
        result = self._parser().parse(raw)

        assert result.score == 70.0
        assert result.reasoning is None

    def test_parse_feedback_detail_criteria(self):
        raw = """
<SCORE>80</SCORE>
<FEEDBACK>Decent work.</FEEDBACK>
<FEEDBACK_JSON>
{
  "summary": "Decent work.",
  "criteria": [
    {"name": "Kebenaran", "score": 40, "max_score": 50, "comment": "Mostly correct."},
    {"name": "Keterbacaan", "score": 25, "max_score": 25, "comment": "Very readable."},
    {"name": "Efisiensi", "score": 15, "max_score": 25, "comment": "Could be more efficient."}
  ],
  "suggestions": ["Use more efficient algorithm.", "Add comments."]
}
</FEEDBACK_JSON>
"""
        result = self._parser().parse(raw)

        assert result.feedback_detail is not None
        assert len(result.feedback_detail.criteria) == 3
        assert result.feedback_detail.criteria[1].score == 25.0
        assert len(result.feedback_detail.suggestions) == 2

    def test_parse_returns_none_feedback_detail_on_missing_tag(self):
        raw = "<SCORE>60</SCORE>\n<FEEDBACK>Okay.</FEEDBACK>"
        assert self._parser().parse(raw).feedback_detail is None

    def test_parse_returns_none_feedback_detail_on_invalid_json(self):
        raw = "<SCORE>60</SCORE>\n<FEEDBACK>Okay.</FEEDBACK>\n<FEEDBACK_JSON>not valid json</FEEDBACK_JSON>"
        assert self._parser().parse(raw).feedback_detail is None

    def test_parse_clamps_score_above_100(self):
        raw = "<SCORE>150</SCORE>\n<FEEDBACK>Too high.</FEEDBACK>"
        assert self._parser().parse(raw).score == 100.0

    def test_parse_clamps_score_below_0(self):
        raw = "<SCORE>-10</SCORE>\n<FEEDBACK>Negative.</FEEDBACK>"
        assert self._parser().parse(raw).score == 0.0

    def test_parse_returns_zero_score_on_missing_tag(self):
        assert self._parser().parse("No structured output.").score == 0.0

    def test_parse_handles_decimal_score(self):
        raw = "<SCORE>87.5</SCORE>\n<FEEDBACK>Almost perfect.</FEEDBACK>"
        assert self._parser().parse(raw).score == 87.5

    def test_parse_is_case_insensitive_on_tags(self):
        raw = "<score>60</score>\n<feedback>Okay.</feedback>"
        result = self._parser().parse(raw)

        assert result.score == 60.0
        assert "Okay" in result.feedback
