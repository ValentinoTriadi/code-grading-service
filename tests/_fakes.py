"""Shared test doubles & helpers for the service test suite."""

from __future__ import annotations

import json

from src.engine.input_handler import InputHandler
from src.engine.llm_interface import LLMInterface
from src.engine.prompt_orchestrator import PromptOrchestrator
from src.engine.response_parser import ResponseParser
from src.llm.base import BaseLLMProvider
from src.prompts.builder import PromptBuilder
from src.services.grading_service import GradingService


def canned_result_dict(score: int | float = 88) -> dict:
    """Schema-valid <RESULT> payload."""
    return {
        "score": score,
        "summary": "Solusi benar dan menangani kasus array kosong.",
        "criteria": [
            {
                "name": "Correctness",
                "score": 55,
                "max_score": 60,
                "comment": "Menghasilkan output benar untuk semua input valid.",
            },
            {
                "name": "Efficiency",
                "score": 20,
                "max_score": 25,
                "comment": "Kompleksitas linear, optimal.",
            },
            {
                "name": "Code Quality",
                "score": 13,
                "max_score": 15,
                "comment": "Penamaan jelas.",
            },
        ],
        "suggestions": ["Tambahkan type hints."],
        "exemplary_points": ["Penanganan edge case rapi."],
        "complexity": {"time": "O(n)", "space": "O(1)"},
        "confidence": 0.9,
    }


def canned_raw(score: int | float = 88, with_thinking: bool = True) -> str:
    """Raw LLM response string in production <THINKING>/<RESULT> format."""
    body = json.dumps(canned_result_dict(score), ensure_ascii=False)
    thinking = ""
    if with_thinking:
        thinking = (
            "<THINKING>\n"
            "Menelusuri kode: menjumlahkan elemen array, menangani input kosong.\n"
            "</THINKING>\n"
        )
    return f"{thinking}<RESULT>\n{body}\n</RESULT>"


class FakeProvider(BaseLLMProvider):
    """Deterministic stand-in for a real LLM provider.

    - response: the raw text returned by generate().
    - raises: if set, generate() raises it (to test error propagation).
    Records every prompt it receives in self.calls.
    """

    def __init__(
        self,
        response: str | None = None,
        raises: BaseException | None = None,
    ) -> None:
        self.response = response if response is not None else canned_raw()
        self.raises = raises
        self.calls: list[str] = []

    async def generate(self, prompt: str, **kwargs) -> str:
        self.calls.append(prompt)
        if self.raises is not None:
            raise self.raises
        return self.response


def make_service(provider: BaseLLMProvider) -> GradingService:
    """Wire real engine modules around a provider — same graph as dependencies.py."""
    return GradingService(
        input_handler=InputHandler(),
        prompt_orchestrator=PromptOrchestrator(prompt_builder=PromptBuilder()),
        llm_interface=LLMInterface(provider=provider),
        response_parser=ResponseParser(),
    )
