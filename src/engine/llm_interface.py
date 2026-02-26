from src.llm.base import BaseLLMProvider


class LLMInterface:
    """Sends constructed prompts to the LLM provider and returns raw responses."""

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    async def generate(self, prompt: str) -> str:
        """Send prompt to LLM and return the raw text response."""
        # TODO: Implement LLM request logic
        raise NotImplementedError
