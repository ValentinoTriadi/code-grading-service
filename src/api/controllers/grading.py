import io
import zipfile

from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from src.api.schemas.request import GradingRequest, InlineGradingRequest
from src.api.schemas.response import GradingResponse
from src.services.grading_service import GradingService


class GradingController:
    """Handles HTTP-level concerns for grading endpoints.

    Responsible for decoding uploads, dispatching to GradingService,
    and formatting responses (JSON or Excel).
    """

    def __init__(self, service: GradingService) -> None:
        self.service = service

    async def grade_inline(self, request: InlineGradingRequest) -> GradingResponse:
        internal = GradingRequest(
            problem_description=request.problems,
            student_code=request.code,
            rubric=request.rubric,
            with_reason=request.with_reason,
        )
        result = await self.service.grade(internal)
        if not request.with_reason:
            result.reasoning = None
        return result

    async def grade_file(
        self,
        problems: str,
        code: UploadFile,
        rubric: str | None,
        with_reason: bool,
    ) -> GradingResponse:
        try:
            content = (await code.read()).decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File could not be decoded as UTF-8 text")

        internal = GradingRequest(
            problem_description=problems,
            student_code=content,
            rubric=rubric,
            with_reason=with_reason,
        )
        result = await self.service.grade(internal)
        if not with_reason:
            result.reasoning = None
        return result

    async def grade_batch(
        self,
        problems: str,
        files: UploadFile,
        rubric: str | None,
        with_reason: bool,
    ) -> StreamingResponse:
        zip_bytes = await files.read()

        try:
            zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid zip archive")

        code_files = [name for name in zf.namelist() if not name.endswith("/")]
        if not code_files:
            raise HTTPException(status_code=400, detail="Zip archive contains no files")

        results: list[dict] = []
        for filename in code_files:
            try:
                content = zf.read(filename).decode("utf-8")
            except UnicodeDecodeError:
                results.append({"filename": filename, "error": f"Could not decode {filename} as UTF-8"})
                continue

            internal = GradingRequest(
                problem_description=problems,
                student_code=content,
                rubric=rubric,
                with_reason=with_reason,
            )

            try:
                grading_result = await self.service.grade(internal)
                entry: dict = {
                    "filename": filename,
                    "score": grading_result.score,
                    "feedback": grading_result.feedback,
                }
                if with_reason:
                    entry["reasoning"] = grading_result.reasoning
            except Exception as exc:
                entry = {"filename": filename, "error": str(exc)}

            results.append(entry)

        excel_bytes = self._build_excel(results, with_reason=with_reason)

        return StreamingResponse(
            io.BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=grading_results.xlsx"},
        )

    @staticmethod
    def _build_excel(results: list[dict], with_reason: bool) -> bytes:
        import openpyxl
        from openpyxl.styles import Alignment, Font, PatternFill

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Grading Results"

        headers = ["No", "Filename", "Score", "Feedback"]
        if with_reason:
            headers.append("Reasoning")
        headers.append("Error")

        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")

        for col_idx, header in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")

        for row_idx, result in enumerate(results, start=2):
            col = 1
            ws.cell(row=row_idx, column=col, value=row_idx - 1); col += 1
            ws.cell(row=row_idx, column=col, value=result.get("filename", "")); col += 1
            ws.cell(row=row_idx, column=col, value=result.get("score")); col += 1
            ws.cell(row=row_idx, column=col, value=result.get("feedback", "")); col += 1
            if with_reason:
                ws.cell(row=row_idx, column=col, value=result.get("reasoning")); col += 1
            ws.cell(row=row_idx, column=col, value=result.get("error", ""))

        for col in ws.columns:
            max_len = max((len(str(cell.value or "")) for cell in col), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 80)

        buf = io.BytesIO()
        wb.save(buf)
        return buf.getvalue()
