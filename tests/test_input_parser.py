import asyncio

import pytest

from src.api.schemas.request import CodeFileReference, GradingRequest
from src.engine.input_parser import InputParser


class MockResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError("HTTP error")


class MockAsyncClient:
    def __init__(self, responses: dict[str, str], **_kwargs):
        self.responses = responses

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def get(self, url: str):
        if url not in self.responses:
            return MockResponse("", status_code=404)
        return MockResponse(self.responses[url])


class TestInputParser:
    def test_parse_inline_mode(self):
        parser = InputParser()
        request = GradingRequest(student_code="print('ok')", problem_description="desc")

        result = asyncio.run(parser.parse(request))

        assert result.student_code == "print('ok')"
        assert result.source_files == ["inline"]

    def test_parse_single_s3_url_mode(self, monkeypatch: pytest.MonkeyPatch):
        parser = InputParser()
        request = GradingRequest(
            code_file_url="s3://my-bucket/sub/path/main.py",
            problem_description="desc",
        )

        responses = {
            "https://my-bucket.s3.amazonaws.com/sub/path/main.py": "print('from s3')\n"
        }

        monkeypatch.setattr(
            "src.engine.input_parser.httpx.AsyncClient",
            lambda **kwargs: MockAsyncClient(responses=responses, **kwargs),
        )

        result = asyncio.run(parser.parse(request))

        assert result.student_code == "print('from s3')"
        assert result.source_files == ["s3://my-bucket/sub/path/main.py"]

    def test_parse_batch_mode(self, monkeypatch: pytest.MonkeyPatch):
        parser = InputParser()
        request = GradingRequest(
            batch_code_files=[
                CodeFileReference(
                    url="https://example.com/a.py",
                    filename="a.py",
                ),
                CodeFileReference(
                    url="https://example.com/b.py",
                    filename="b.py",
                ),
            ],
            problem_description="desc",
        )

        responses = {
            "https://example.com/a.py": "print('a')\n",
            "https://example.com/b.py": "print('b')\n",
        }

        monkeypatch.setattr(
            "src.engine.input_parser.httpx.AsyncClient",
            lambda **kwargs: MockAsyncClient(responses=responses, **kwargs),
        )

        result = asyncio.run(parser.parse(request))

        assert "# File: a.py\nprint('a')" in result.student_code
        assert "# File: b.py\nprint('b')" in result.student_code
        assert result.source_files == ["https://example.com/a.py", "https://example.com/b.py"]

    def test_rejects_unsupported_scheme(self):
        parser = InputParser()

        with pytest.raises(ValueError, match="Unsupported URL scheme"):
            asyncio.run(parser._fetch_code_file("ftp://example.com/code.py"))

    def test_parse_single_presigned_url_mode(self, monkeypatch: pytest.MonkeyPatch):
        parser = InputParser()
        presigned = (
            "https://my-bucket.s3.amazonaws.com/path/code.py"
            "?X-Amz-Algorithm=AWS4-HMAC-SHA256"
            "&X-Amz-Credential=test"
            "&X-Amz-Date=20260226T010101Z"
            "&X-Amz-Expires=3600"
            "&X-Amz-SignedHeaders=host"
            "&X-Amz-Signature=abc123"
        )
        request = GradingRequest(code_file_url=presigned, problem_description="desc")

        monkeypatch.setattr(
            "src.engine.input_parser.httpx.AsyncClient",
            lambda **kwargs: MockAsyncClient(responses={presigned: "print('from presigned')\n"}, **kwargs),
        )

        result = asyncio.run(parser.parse(request))

        assert result.student_code == "print('from presigned')"
        assert result.source_files == [presigned]
