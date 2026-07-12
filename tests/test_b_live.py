"""TF-B-LIVE — Pengujian fungsional end-to-end dengan Gemini asli (Vertex AI).

Sama dengan lapis B (test_grading_service.py + test_api_endpoints.py) tapi
provider-nya Gemini nyata — membuktikan pipeline dan endpoint bekerja
dari ujung ke ujung termasuk LLM yang sebenarnya.

Assertion lebih longgar dibanding lapis B offline:
  - Nilai skor tidak dicek presisi (tidak tahu output Gemini); cukup 0–100.
  - Format respons tetap dicek ketat (tipe data, field wajib, HTTP status).

CARA MENJALANKAN:
    gcloud auth application-default login
    export GEMINI_USE_VERTEX=true GOOGLE_CLOUD_PROJECT=ta-project-492309
    export GOOGLE_CLOUD_LOCATION=asia-southeast1
    export LLM_PROVIDER=gemini LLM_MODEL_NAME=gemini-2.5-flash

    uv run pytest tests/test_b_live.py -v -s \\
        --html=docs/snapshot/test-report-b-live.html --self-contained-html
"""

from __future__ import annotations

import io
import zipfile

import pytest
from fastapi.testclient import TestClient

from tests._fakes import make_service
from tests.conftest import MINIMAL_INLINE_PAYLOAD


# ─────────────────────── pipeline (tanpa HTTP) ────────────────────────────────


class TestGradingServiceLive:
    """TF-B-LIVE-GS — Pipeline GradingService dengan Gemini asli."""

    @pytest.mark.anyio
    async def test_pipeline_returns_score_in_range(self, live_provider):
        """TF-B-LIVE-GS-01: pipeline menghasilkan skor 0–100 dari Gemini asli."""
        from src.api.schemas.request import GradingRequest

        svc = make_service(live_provider)
        result = await svc.grade(
            GradingRequest(
                problem_description=MINIMAL_INLINE_PAYLOAD["problems"],
                student_code=MINIMAL_INLINE_PAYLOAD["code"],
            )
        )
        assert 0.0 <= result.score <= 100.0

    @pytest.mark.anyio
    async def test_pipeline_returns_non_empty_feedback(self, live_provider):
        """TF-B-LIVE-GS-02: feedback tidak kosong dari Gemini asli."""
        from src.api.schemas.request import GradingRequest

        svc = make_service(live_provider)
        result = await svc.grade(
            GradingRequest(
                problem_description=MINIMAL_INLINE_PAYLOAD["problems"],
                student_code=MINIMAL_INLINE_PAYLOAD["code"],
            )
        )
        assert result.feedback != ""

    @pytest.mark.anyio
    async def test_pipeline_returns_criteria_list(self, live_provider):
        """TF-B-LIVE-GS-03: feedback_detail.criteria hadir dan tidak kosong."""
        from src.api.schemas.request import GradingRequest

        svc = make_service(live_provider)
        result = await svc.grade(
            GradingRequest(
                problem_description=MINIMAL_INLINE_PAYLOAD["problems"],
                student_code=MINIMAL_INLINE_PAYLOAD["code"],
                with_reason=True,
            )
        )
        assert result.feedback_detail is not None
        assert len(result.feedback_detail.criteria) > 0

    @pytest.mark.anyio
    async def test_pipeline_reasoning_populated_with_reason_true(self, live_provider):
        """TF-B-LIVE-GS-04: reasoning terisi saat with_reason=True."""
        from src.api.schemas.request import GradingRequest

        svc = make_service(live_provider)
        result = await svc.grade(
            GradingRequest(
                problem_description=MINIMAL_INLINE_PAYLOAD["problems"],
                student_code=MINIMAL_INLINE_PAYLOAD["code"],
                with_reason=True,
            )
        )
        assert result.reasoning is not None
        assert len(result.reasoning) > 0

    @pytest.mark.anyio
    async def test_pipeline_custom_rubric_respected(self, live_provider):
        """TF-B-LIVE-GS-05: rubrik kustom diproses tanpa error; skor tetap 0–100."""
        from src.api.schemas.request import GradingRequest

        svc = make_service(live_provider)
        result = await svc.grade(
            GradingRequest(
                problem_description=MINIMAL_INLINE_PAYLOAD["problems"],
                student_code=MINIMAL_INLINE_PAYLOAD["code"],
                rubric="Correctness 70%, Code Style 30%",
            )
        )
        assert 0.0 <= result.score <= 100.0


# ─────────────────────── endpoint HTTP (inline) ───────────────────────────────


class TestInlineEndpointLive:
    """TF-B-LIVE-API — POST /api/v1/grade/inline dengan Gemini asli."""

    def test_valid_request_returns_200(self, api_client_live: TestClient):
        """TF-B-LIVE-API-01: request valid menghasilkan HTTP 200."""
        r = api_client_live.post("/api/v1/grade/inline", json=MINIMAL_INLINE_PAYLOAD)
        assert r.status_code == 200

    def test_score_in_range(self, api_client_live: TestClient):
        """TF-B-LIVE-API-02: skor dalam respons HTTP berada di rentang 0–100."""
        r = api_client_live.post("/api/v1/grade/inline", json=MINIMAL_INLINE_PAYLOAD)
        assert 0.0 <= r.json()["score"] <= 100.0

    def test_feedback_non_empty(self, api_client_live: TestClient):
        """TF-B-LIVE-API-03: feedback dalam respons tidak kosong."""
        r = api_client_live.post("/api/v1/grade/inline", json=MINIMAL_INLINE_PAYLOAD)
        body = r.json()
        assert isinstance(body["feedback"], str) and body["feedback"] != ""

    def test_feedback_detail_criteria_present(self, api_client_live: TestClient):
        """TF-B-LIVE-API-04: feedback_detail.criteria hadir dan berisi entri."""
        r = api_client_live.post("/api/v1/grade/inline", json=MINIMAL_INLINE_PAYLOAD)
        detail = r.json().get("feedback_detail")
        assert detail is not None
        assert len(detail["criteria"]) > 0

    def test_reasoning_absent_when_with_reason_false(self, api_client_live: TestClient):
        """TF-B-LIVE-API-05: reasoning = null saat with_reason=false."""
        payload = {**MINIMAL_INLINE_PAYLOAD, "with_reason": False}
        r = api_client_live.post("/api/v1/grade/inline", json=payload)
        assert r.json().get("reasoning") is None

    def test_reasoning_present_when_with_reason_true(self, api_client_live: TestClient):
        """TF-B-LIVE-API-06: reasoning terisi saat with_reason=true."""
        payload = {**MINIMAL_INLINE_PAYLOAD, "with_reason": True}
        r = api_client_live.post("/api/v1/grade/inline", json=payload)
        assert r.json().get("reasoning") is not None

    def test_missing_code_still_returns_422(self, api_client_live: TestClient):
        """TF-B-LIVE-API-07: validasi input tetap berlaku (tidak ada kode → 422)."""
        r = api_client_live.post(
            "/api/v1/grade/inline", json={"problems": "Soal tanpa kode."}
        )
        assert r.status_code == 422


# ─────────────────────── endpoint HTTP (file) ─────────────────────────────────


class TestFileEndpointLive:
    """TF-B-LIVE-FILE — POST /api/v1/grade/file dengan Gemini asli."""

    def test_valid_file_returns_200_and_score(self, api_client_live: TestClient):
        """TF-B-LIVE-FILE-01: upload file Python valid menghasilkan HTTP 200 + skor."""
        code = b"def sum_array(arr):\n    return sum(arr)\n"
        r = api_client_live.post(
            "/api/v1/grade/file",
            data={"problems": MINIMAL_INLINE_PAYLOAD["problems"]},
            files={"code": ("solution.py", io.BytesIO(code), "text/plain")},
        )
        assert r.status_code == 200
        assert 0.0 <= r.json()["score"] <= 100.0

    def test_non_utf8_file_returns_400(self, api_client_live: TestClient):
        """TF-B-LIVE-FILE-02: file non-UTF-8 tetap ditolak 400 (validasi tidak tergantung LLM)."""
        r = api_client_live.post(
            "/api/v1/grade/file",
            data={"problems": "Soal"},
            files={"code": ("bad.py", io.BytesIO(b"\xff\xfe\x00"), "text/plain")},
        )
        assert r.status_code == 400


# ─────────────────────── endpoint HTTP (batch) ────────────────────────────────


class TestBatchEndpointLive:
    """TF-B-LIVE-BATCH — POST /api/v1/grade/batch dengan Gemini asli."""

    def _make_zip(self, files: dict[str, bytes]) -> io.BytesIO:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        buf.seek(0)
        return buf

    def test_batch_zip_returns_xlsx(self, api_client_live: TestClient):
        """TF-B-LIVE-BATCH-01: ZIP berisi 2 file menghasilkan respons Excel."""
        zf = self._make_zip(
            {
                "student_a.py": b"def sum_array(arr): return sum(arr)",
                "student_b.py": b"def sum_array(arr): return 0",
            }
        )
        r = api_client_live.post(
            "/api/v1/grade/batch",
            data={"problems": MINIMAL_INLINE_PAYLOAD["problems"]},
            files={"files": ("submissions.zip", zf, "application/zip")},
        )
        assert r.status_code == 200
        assert "spreadsheet" in r.headers["content-type"]
