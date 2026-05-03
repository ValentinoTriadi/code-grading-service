import asyncio
import logging
import time
from collections import deque
from collections.abc import Awaitable, Callable

from src.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class RequestRateLimiter:
    """Async sliding-window limiter for LLM requests."""

    def __init__(
        self,
        max_requests_per_minute: int,
        window_seconds: float = 60.0,
        clock: Callable[[], float] | None = None,
        sleeper: Callable[[float], Awaitable[None]] | None = None,
    ) -> None:
        self.max_requests_per_minute = max(0, int(max_requests_per_minute))
        self.window_seconds = window_seconds
        self._clock = clock or time.monotonic
        self._sleep = sleeper or asyncio.sleep
        self._timestamps: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait until the next request is allowed under the configured rate."""
        if self.max_requests_per_minute <= 0:
            return

        while True:
            wait_seconds = 0.0
            async with self._lock:
                now = self._clock()
                cutoff = now - self.window_seconds
                while self._timestamps and self._timestamps[0] <= cutoff:
                    self._timestamps.popleft()

                if len(self._timestamps) < self.max_requests_per_minute:
                    self._timestamps.append(now)
                    return

                wait_seconds = max(0.0, self._timestamps[0] + self.window_seconds - now)

            logger.debug("LLM rate limit reached, sleeping %.2fs", wait_seconds)
            await self._sleep(wait_seconds)


class LLMInterface:
    """Sends constructed prompts to the configured LLM provider."""

    def __init__(
        self, provider: BaseLLMProvider, rate_limiter: RequestRateLimiter | None = None
    ) -> None:
        self.provider = provider
        self.rate_limiter = rate_limiter

    async def generate(self, prompt: str) -> str:
        """Send prompt to the LLM and return the raw text response."""
        provider_name = type(self.provider).__name__
        if self.rate_limiter is not None:
            await self.rate_limiter.acquire()
        logger.info("Sending prompt to %s (%d chars)", provider_name, len(prompt))
        raw = await self.provider.generate(prompt)
        logger.info("Response received from %s (%d chars)", provider_name, len(raw))
        return raw
