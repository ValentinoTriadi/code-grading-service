from src.engine.prompt_orchestrator import PromptOrchestrator
from src.prompts.builder import PromptBuilder


class TestPromptOrchestrator:
    """Tests for PromptOrchestrator."""

    def test_placeholder(self):
        builder = PromptBuilder()
        orchestrator = PromptOrchestrator(prompt_builder=builder)
        assert orchestrator is not None
