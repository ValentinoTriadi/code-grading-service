from fastapi import APIRouter

from src.api.schemas.request import GradingRequest
from src.api.schemas.response import GradingResponse

router = APIRouter(prefix="/api/v1", tags=["grading"])


@router.post("/grade", response_model=GradingResponse)
async def grade_code(request: GradingRequest) -> GradingResponse:
    """Grade student code based on the provided problem and rubric.

    Pipeline: InputHandler -> PromptOrchestrator -> LLMInterface -> ResponseParser
    """
    # TODO: Implement grading pipeline
    # 1. input_handler.validate(request)
    # 2. prompt = prompt_orchestrator.build(request)
    # 3. raw = llm_interface.generate(prompt)
    # 4. result = response_parser.parse(raw)
    raise NotImplementedError("Grading pipeline not yet implemented")
