import logging

import anthropic

from src.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseLLMProvider):
    """LLM provider backed by the Anthropic Claude API.

    Defaults to `claude-opus-4-7`. On Opus 4.7 the sampling parameters
    (`temperature`, `top_p`, `top_k`) are removed and `budget_tokens`-style
    extended thinking is gone — adaptive thinking is the only on-mode.
    Our grading prompt already contains an explicit `<THINKING>` block via
    `cot_instruction.txt`, so we keep adaptive thinking off here to avoid
    double-reasoning; flip it on by editing `_thinking` below if you want
    Claude-side reasoning on top of the in-prompt CoT.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        max_tokens: int = 16000,
        # Kept in the constructor for cross-provider symmetry; ignored on Opus
        # 4.7 (which 400s on `temperature`). Used only as a hint for older
        # Claude models if the user pins one via `LLM_MODEL_NAME`.
        temperature: float = 0.0,
    ) -> None:
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self._is_opus_4_7 = model.startswith("claude-opus-4-7")
        self._temperature = temperature

    async def generate(self, prompt: str, **kwargs) -> str:
        logger.debug(
            "Anthropic request — model=%s, max_tokens=%d",
            self.model,
            self.max_tokens,
        )
        request: dict = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        # `temperature` is removed on Opus 4.7 — sending it returns 400.
        if not self._is_opus_4_7:
            request["temperature"] = self._temperature

        response = await self.client.messages.create(**request)

        if response.usage:
            u = response.usage
            logger.info(
                "Anthropic usage — input=%d output=%d "
                "cache_read=%d cache_creation=%d",
                u.input_tokens,
                u.output_tokens,
                getattr(u, "cache_read_input_tokens", 0) or 0,
                getattr(u, "cache_creation_input_tokens", 0) or 0,
            )

        return "".join(b.text for b in response.content if b.type == "text")
