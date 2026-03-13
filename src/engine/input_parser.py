from dataclasses import dataclass

import httpx

from src.api.schemas.request import GradingRequest
from src.engine.input_handler import InputHandler
from src.utils.s3 import normalize_object_storage_reference


@dataclass
class ParsedInput:
    """Normalized code payload after input parsing."""

    student_code: str
    source_files: list[str]


class InputParser:
    """Build normalized student code from inline or URL-based requests."""

    def __init__(
        self,
        input_handler: InputHandler | None = None,
        timeout_seconds: float = 30.0,
        max_file_size_bytes: int = 1_000_000,
        max_batch_files: int = 20,
    ):
        self.input_handler = input_handler or InputHandler()
        self.timeout_seconds = timeout_seconds
        self.max_file_size_bytes = max_file_size_bytes
        self.max_batch_files = max_batch_files

    async def parse(self, request: GradingRequest) -> ParsedInput:
        validated = self.input_handler.validate(request)

        if validated.student_code is not None:
            return ParsedInput(student_code=validated.student_code, source_files=["inline"])

        if validated.code_file_url is not None:
            content = await self._fetch_code_file(validated.code_file_url)
            return ParsedInput(student_code=self.input_handler.sanitize_code(content), source_files=[validated.code_file_url])

        if validated.batch_code_files is None:
            raise ValueError("No input source provided")

        if len(validated.batch_code_files) > self.max_batch_files:
            raise ValueError(
                f"batch_code_files exceeds max allowed files ({self.max_batch_files})"
            )

        merged_parts: list[str] = []
        source_files: list[str] = []

        for index, file_ref in enumerate(validated.batch_code_files, start=1):
            content = await self._fetch_code_file(file_ref.url)
            filename = file_ref.filename or f"file_{index}"
            merged_parts.append(f"# File: {filename}\n{self.input_handler.sanitize_code(content)}")
            source_files.append(file_ref.url)

        return ParsedInput(student_code="\n\n".join(merged_parts), source_files=source_files)

    async def _fetch_code_file(self, raw_url: str) -> str:
        url = normalize_object_storage_reference(raw_url.strip())

        async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            content = response.text

        encoded_length = len(content.encode("utf-8"))
        if encoded_length > self.max_file_size_bytes:
            raise ValueError(
                f"Remote file too large ({encoded_length} bytes), limit is {self.max_file_size_bytes}"
            )

        return content
