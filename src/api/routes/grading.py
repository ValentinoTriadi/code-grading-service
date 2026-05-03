from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from src.api.controllers.grading import GradingController
from src.api.dependencies import get_grading_controller
from src.api.schemas.request import InlineGradingRequest
from src.api.schemas.response import GradingResponse

router = APIRouter(prefix="/api/v1", tags=["grading"])

ControllerDep = Annotated[GradingController, Depends(get_grading_controller)]

_COMMON_ERRORS = {
    400: {
        "description": "Invalid request — missing required fields or malformed input."
    },
    500: {"description": "Internal error — LLM provider failure or parsing error."},
}


@router.post(
    "/grade/inline",
    response_model=GradingResponse,
    summary="Grade inline code",
    responses=_COMMON_ERRORS,
)
async def route_grade_inline(
    request: InlineGradingRequest,
    controller: ControllerDep,
) -> GradingResponse:
    """Grade student code submitted as a **JSON string**.

    - `problems` — problem statement
    - `code` — student source code
    - `rubric` *(optional)* — custom rubric; uses default if omitted
    - `with_reason` *(optional)* — include LLM reasoning in response
    """
    return await controller.grade_inline(request)


@router.post(
    "/grade/file",
    response_model=GradingResponse,
    summary="Grade an uploaded source file",
    responses=_COMMON_ERRORS,
)
async def route_grade_file(
    controller: ControllerDep,
    problems: str = Form(..., description="Problem statement given to students."),
    code: UploadFile = File(..., description="Student source code file (UTF-8 text)."),
    rubric: str | None = Form(
        None, description="Custom rubric. Uses default if omitted."
    ),
    with_reason: bool = Form(
        False, description="Include LLM reasoning in the response."
    ),
) -> GradingResponse:
    """Grade student code submitted as a **file upload** (`multipart/form-data`).

    Accepts any plain-text source file (`.py`, `.java`, `.cpp`, etc.).
    """
    return await controller.grade_file(problems, code, rubric, with_reason)


@router.post(
    "/grade/batch",
    summary="Grade a batch of submissions from a zip archive",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {}
            },
            "description": "Excel file (`grading_results.xlsx`) with one row per submission.",
        },
        400: {"description": "Invalid or empty zip archive."},
        500: {"description": "Internal error during grading."},
    },
)
async def route_grade_batch(
    controller: ControllerDep,
    problems: str = Form(
        ..., description="Problem statement applied to all submissions."
    ),
    files: UploadFile = File(
        ..., description="Zip archive — one source file per student."
    ),
    rubric: str | None = Form(
        None, description="Custom rubric. Uses default if omitted."
    ),
    with_reason: bool = Form(
        False, description="Add a Reasoning column to the Excel output."
    ),
) -> StreamingResponse:
    """Grade multiple submissions from a **zip archive** (`multipart/form-data`).

    Each file inside the zip is treated as one student submission.
    Returns an **Excel file** (`grading_results.xlsx`) with columns:
    `No`, `Filename`, `Score`, `Feedback`, `Reasoning` *(if requested)*, `Error`.
    """
    return await controller.grade_batch(problems, files, rubric, with_reason)


@router.post(
    "/grade/inline/stream",
    summary="Grade inline code with SSE progress",
    response_class=EventSourceResponse,
    responses={
        200: {
            "content": {"text/event-stream": {}},
            "description": (
                "SSE stream. `progress` events carry `step`, `total`, `message`. "
                "Final event is `result` with the full GradingResponse, or `error`."
            ),
        },
        **_COMMON_ERRORS,
    },
)
async def route_grade_inline_stream(
    request: InlineGradingRequest,
    controller: ControllerDep,
) -> EventSourceResponse:
    """Grade inline code and stream pipeline progress via **Server-Sent Events**."""
    return EventSourceResponse(controller.grade_inline_stream(request))


@router.post(
    "/grade/file/stream",
    summary="Grade an uploaded source file with SSE progress",
    response_class=EventSourceResponse,
    responses={
        200: {
            "content": {"text/event-stream": {}},
            "description": (
                "SSE stream. `progress` events carry `step`, `total`, `message`. "
                "Final event is `result` with the full GradingResponse, or `error`."
            ),
        },
        **_COMMON_ERRORS,
    },
)
async def route_grade_file_stream(
    controller: ControllerDep,
    problems: str = Form(...),
    code: UploadFile = File(...),
    rubric: str | None = Form(None),
    with_reason: bool = Form(False),
) -> EventSourceResponse:
    """Grade a file upload and stream pipeline progress via **Server-Sent Events**."""
    return EventSourceResponse(
        controller.grade_file_stream(problems, code, rubric, with_reason)
    )


@router.post(
    "/grade/batch/stream",
    summary="Grade a batch with SSE progress events",
    response_class=EventSourceResponse,
    responses={
        200: {
            "content": {"text/event-stream": {}},
            "description": (
                "SSE stream of progress events. Each event has `type='progress'` with "
                "`done`, `total`, `filename`, `score`, and `error` fields. "
                "Final event has `type='complete'` and contains the Excel file as base64 in `excel`."
            ),
        },
        400: {"description": "Invalid or empty zip archive."},
    },
)
async def route_grade_batch_stream(
    controller: ControllerDep,
    problems: str = Form(
        ..., description="Problem statement applied to all submissions."
    ),
    files: UploadFile = File(
        ..., description="Zip archive — one source file per student."
    ),
    rubric: str | None = Form(
        None, description="Custom rubric. Uses default if omitted."
    ),
    with_reason: bool = Form(
        False, description="Add a Reasoning column to the Excel output."
    ),
) -> EventSourceResponse:
    """Stream grading progress for a batch zip upload via **Server-Sent Events**.

    Emits one `progress` event per file as it finishes, then a final `complete`
    event containing the Excel result as a base64-encoded string.
    """
    return EventSourceResponse(
        controller.grade_batch_stream(problems, files, rubric, with_reason)
    )
