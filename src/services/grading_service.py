import logging
from collections.abc import Awaitable, Callable

from src.api.schemas.request import GradingRequest
from src.api.schemas.response import GradingResponse
from src.engine.input_handler import InputHandler
from src.engine.llm_interface import LLMInterface
from src.engine.prompt_orchestrator import PromptOrchestrator
from src.engine.response_parser import ResponseParser

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[int, int, str], Awaitable[None]]

PIPELINE_STEPS = [
    "Validating input…",
    "Building prompt…",
    "Calling LLM…",
    "Parsing response…",
]


class GradingService:
    """Orchestrates the full grading pipeline for a single submission."""

    def __init__(
        self,
        input_handler: InputHandler,
        prompt_orchestrator: PromptOrchestrator,
        llm_interface: LLMInterface,
        response_parser: ResponseParser,
    ) -> None:
        self.input_handler = input_handler
        self.prompt_orchestrator = prompt_orchestrator
        self.llm_interface = llm_interface
        self.response_parser = response_parser

    async def grade(
        self,
        request: GradingRequest,
        on_progress: ProgressCallback | None = None,
    ) -> GradingResponse:
        """Run the full pipeline and return a structured grading result.

        If `on_progress` is provided it is called before each step with
        (step_number, total_steps, message).
        """
        total = len(PIPELINE_STEPS)
        logger.info("Pipeline started — with_reason=%s", request.with_reason)

        async def emit(step: int) -> None:
            if on_progress:
                await on_progress(step, total, PIPELINE_STEPS[step - 1])

        await emit(1)
        logger.debug("Step 1/4: validating input")
        request = self.input_handler.validate(request)

        await emit(2)
        logger.debug("Step 2/4: building prompt")
        prompt = self.prompt_orchestrator.build(request)

        await emit(3)
        logger.info("Step 3/4: calling LLM")
        raw = await self.llm_interface.generate(prompt.text)

        await emit(4)
        logger.debug("Step 4/4: parsing response")
        result = self.response_parser.parse(raw)

        logger.info("Pipeline complete — score=%.1f", result.score)
        return result
