import logging

from openai import AsyncOpenAI

from src.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """LLM provider backed by the OpenAI Chat Completions API."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.0,
    ) -> None:
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url or None)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    async def generate(self, prompt: str, **kwargs) -> str:
        logger.debug(
            "OpenAI request — model=%s, max_tokens=%d, temperature=%.1f",
            self.model,
            self.max_tokens,
            self.temperature,
        )
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        usage = response.usage
        if usage:
            logger.info(
                "OpenAI usage — prompt=%d, completion=%d, total=%d tokens",
                usage.prompt_tokens,
                usage.completion_tokens,
                usage.total_tokens,
            )
        return response.choices[0].message.content or ""
