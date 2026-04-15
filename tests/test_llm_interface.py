import pytest

from src.engine.llm_interface import LLMInterface, RequestRateLimiter


class DummyProvider:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def generate(self, prompt: str, **kwargs) -> str:
        self.calls.append(prompt)
        return f"ok:{prompt}"


class TestLLMInterface:
    @pytest.mark.anyio
    async def test_generate_calls_provider(self):
        provider = DummyProvider()
        interface = LLMInterface(provider=provider)

        result = await interface.generate("hello")

        assert result == "ok:hello"
        assert provider.calls == ["hello"]

    @pytest.mark.anyio
    async def test_rate_limiter_enforced(self):
        current_time = 0.0
        sleeps: list[float] = []

        def clock() -> float:
            return current_time

        async def fake_sleep(seconds: float) -> None:
            nonlocal current_time
            sleeps.append(seconds)
            current_time += seconds

        limiter = RequestRateLimiter(
            max_requests_per_minute=2,
            window_seconds=60.0,
            clock=clock,
            sleeper=fake_sleep,
        )
        provider = DummyProvider()
        interface = LLMInterface(provider=provider, rate_limiter=limiter)

        await interface.generate("a")
        await interface.generate("b")
        await interface.generate("c")

        assert provider.calls == ["a", "b", "c"]
        assert sleeps == [60.0]

    @pytest.mark.anyio
    async def test_rate_limiter_disabled_when_zero(self):
        current_time = 0.0
        sleeps: list[float] = []

        def clock() -> float:
            return current_time

        async def fake_sleep(seconds: float) -> None:
            sleeps.append(seconds)

        limiter = RequestRateLimiter(
            max_requests_per_minute=0,
            clock=clock,
            sleeper=fake_sleep,
        )
        provider = DummyProvider()
        interface = LLMInterface(provider=provider, rate_limiter=limiter)

        await interface.generate("x")
        await interface.generate("y")

        assert provider.calls == ["x", "y"]
        assert sleeps == []
