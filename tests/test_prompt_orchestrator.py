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

        assert "Kebenaran" in prompt
        assert "{{rubric}}" not in prompt

    def test_build_injects_custom_rubric(self):
        prompt = _make_orchestrator().build(_make_request(rubric="Correctness: 100%"))

        assert "Correctness: 100%" in prompt

    def test_build_includes_reasoning_format_when_with_reason_true(self):
        prompt = _make_orchestrator().build(_make_request(with_reason=True))

        assert "<REASONING>" in prompt

    def test_build_excludes_reasoning_format_when_with_reason_false(self):
        prompt = _make_orchestrator().build(_make_request(with_reason=False))

        assert "<REASONING>" not in prompt

    def test_build_always_includes_score_and_feedback_format(self):
        for with_reason in (True, False):
            prompt = _make_orchestrator().build(_make_request(with_reason=with_reason))
            assert "<SCORE>" in prompt
            assert "<FEEDBACK>" in prompt

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

    def test_build_skips_few_shot_when_not_provided(self):
        prompt = _make_orchestrator().build(_make_request())

        assert "Contoh 1" not in prompt
