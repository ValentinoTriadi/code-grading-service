from src.api.schemas.request import GradingRequest
from src.engine.prompt_orchestrator import PromptOrchestrator
from src.prompts.builder import PromptBuilder


def _make_orchestrator() -> PromptOrchestrator:
    return PromptOrchestrator(prompt_builder=PromptBuilder())


def _make_request(**kwargs) -> GradingRequest:
    defaults = dict(
        problem_description="Write a sum function",
        student_code="def sum(a,b): return a+b",
    )
    return GradingRequest(**{**defaults, **kwargs})


class TestPromptOrchestrator:
    def test_build_contains_problem_and_code(self):
        prompt = _make_orchestrator().build(_make_request())

        assert "Write a sum function" in prompt
        assert "def sum(a,b): return a+b" in prompt

    def test_build_uses_default_rubric_when_none_given(self):
        prompt = _make_orchestrator().build(_make_request())

        assert "Correctness" in prompt
        assert "{{rubric}}" not in prompt

    def test_build_injects_custom_rubric(self):
        prompt = _make_orchestrator().build(
            _make_request(rubric="Custom criterion: 100%")
        )

        assert "Custom criterion: 100%" in prompt

    def test_build_includes_thinking_format_when_with_reason_true(self):
        prompt = _make_orchestrator().build(_make_request(with_reason=True))

        # </THINKING> only appears in the response shape when reasoning is requested.
        assert "</THINKING>" in prompt

    def test_build_excludes_thinking_format_when_with_reason_false(self):
        prompt = _make_orchestrator().build(_make_request(with_reason=False))

        # The closing tag must not appear as part of the response shape.
        assert "</THINKING>" not in prompt

    def test_build_always_includes_result_block(self):
        for with_reason in (True, False):
            prompt = _make_orchestrator().build(_make_request(with_reason=with_reason))
            assert "<RESULT>" in prompt
            assert "</RESULT>" in prompt
            assert '"score"' in prompt
            assert '"summary"' in prompt
            assert '"criteria"' in prompt
            assert '"suggestions"' in prompt

    def test_build_does_not_emit_legacy_tags(self):
        # The new format consolidates SCORE / FEEDBACK / FEEDBACK_JSON into RESULT.
        prompt = _make_orchestrator().build(_make_request(with_reason=True))
        assert "<SCORE>" not in prompt
        assert "<FEEDBACK>" not in prompt
        assert "<FEEDBACK_JSON>" not in prompt

    def test_build_includes_few_shot_when_provided(self):
        examples = [
            {
                "problem": "Add two numbers",
                "code": "return a+b",
                "grading": "Score: 100",
            }
        ]
        prompt = _make_orchestrator().build(_make_request(few_shot_examples=examples))

        assert "Add two numbers" in prompt
        assert "Score: 100" in prompt
        assert "Example 1" in prompt

    def test_build_skips_few_shot_when_not_provided(self):
        prompt = _make_orchestrator().build(_make_request())

        assert "Example 1" not in prompt

    def test_build_returns_prefix_suffix_split(self):
        prompt = _make_orchestrator().build(_make_request())

        # Task content is the per-call dynamic suffix.
        assert "Write a sum function" in prompt.dynamic_suffix
        assert "def sum(a,b): return a+b" in prompt.dynamic_suffix
        # Stable framing (system, rubric, output format) is the cacheable prefix.
        assert "Correctness" in prompt.cacheable_prefix
        assert "<RESULT>" in prompt.cacheable_prefix
        # Task must NOT leak into the cacheable prefix.
        assert "Write a sum function" not in prompt.cacheable_prefix

    def test_build_places_output_format_before_task_in_joined_text(self):
        # Output-format header is part of the cacheable prefix and therefore
        # precedes the task section in the final prompt sent to the LLM.
        prompt = _make_orchestrator().build(_make_request())
        text = prompt.text
        assert text.index("<RESULT>") < text.index("Write a sum function")
