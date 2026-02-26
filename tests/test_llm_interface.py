from src.engine.llm_interface import LLMInterface


class TestLLMInterface:
    """Tests for LLMInterface."""

    def test_placeholder(self):
        # Cannot instantiate without a provider, just test import
        assert LLMInterface is not None
