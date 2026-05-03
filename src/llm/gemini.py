import logging

import google.genai as genai
from google.genai import types

from src.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    """LLM provider backed by the Google Gemini API."""

    def __init__(
        self,
        api_key: str,
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.0,
    ) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model_name = model
        self.config = types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )

    async def generate(self, prompt: str, **kwargs) -> str:
        logger.debug("Gemini request — model=%s", self.model_name)
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=self.config,
        )
        if response.usage_metadata:
            m = response.usage_metadata
            logger.info(
                "Gemini usage — prompt=%d, candidates=%d, total=%d tokens",
                m.prompt_token_count,
                m.candidates_token_count,
                m.total_token_count,
            )
        return response.text or ""
