from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import StreamingResponse

from src.api.controllers.grading import GradingController
from src.api.dependencies import get_grading_controller
from src.api.schemas.request import InlineGradingRequest
from src.api.schemas.response import GradingResponse

router = APIRouter(prefix="/api/v1", tags=["grading"])

ControllerDep = Annotated[GradingController, Depends(get_grading_controller)]


@router.post("/grade/inline", response_model=GradingResponse)
async def route_grade_inline(
    request: InlineGradingRequest,
    controller: ControllerDep,
) -> GradingResponse:
    return await controller.grade_inline(request)


@router.post("/grade/file", response_model=GradingResponse)
async def route_grade_file(
    controller: ControllerDep,
    problems: str = Form(...),
    code: UploadFile = File(..., description="Source code file to grade"),
    rubric: str | None = Form(None),
    with_reason: bool = Form(False),
) -> GradingResponse:
    return await controller.grade_file(problems, code, rubric, with_reason)


@router.post("/grade/batch")
async def route_grade_batch(
    controller: ControllerDep,
    problems: str = Form(...),
    files: UploadFile = File(..., description="Zip archive containing one code file per student"),
    rubric: str | None = Form(None),
    with_reason: bool = Form(False),
) -> StreamingResponse:
    return await controller.grade_batch(problems, files, rubric, with_reason)
