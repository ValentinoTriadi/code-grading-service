from src.api.schemas.request import GradingRequest
from src.api.schemas.response import GradingResponse
from src.engine.input_handler import InputHandler
from src.engine.llm_interface import LLMInterface
from src.engine.prompt_orchestrator import PromptOrchestrator
from src.engine.response_parser import ResponseParser


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

    async def grade(self, request: GradingRequest) -> GradingResponse:
        """Run the full pipeline and return a structured grading result."""
        request = self.input_handler.validate(request)
        prompt = self.prompt_orchestrator.build(request)
        raw = await self.llm_interface.generate(prompt)
        return self.response_parser.parse(raw)
