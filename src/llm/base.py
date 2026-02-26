from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers.

    Implement this class for each LLM provider (e.g., OpenAI, Google Gemini).
    """

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Send a prompt to the LLM and return the generated text.

        Args:
            prompt: The constructed prompt string.
            **kwargs: Provider-specific parameters (temperature, max_tokens, etc.)

        Returns:
            The raw text response from the LLM.
        """
        ...
