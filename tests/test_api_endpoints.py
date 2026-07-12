"""TF-API — Pengujian fungsional endpoint HTTP (offline, FakeProvider).

Menggunakan FastAPI TestClient dengan dependency override pada get_llm_provider.
Semua test memeriksa bahwa request HTTP yang valid menghasilkan respons sesuai
kontrak schema (score + feedback + feedback_detail + reasoning).
"""

from __future__ import annotations

import io
import json
import zipfile

import pytest
from fastapi.testclient import TestClient

from tests._fakes import FakeProvider, canned_raw
from tests.conftest import MINIMAL_INLINE_PAYLOAD


# ─────────────────────────── /health ──────────────────────────────────────────


class TestHealthEndpoint:
    """TF-API-00 — Liveness check."""

    def test_tf_api_00_health_returns_ok(self, api_client: TestClient):
        """TF-API-00: GET /health mengembalikan {status: ok} dengan HTTP 200."""
        r = api_client.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


# ─────────────────────────── /grade/inline ────────────────────────────────────


class TestInlineEndpoint:
    """TF-API-01 hingga TF-API-06 — POST /api/v1/grade/inline."""

    def test_tf_api_01_valid_request_returns_200(self, api_client: TestClient):
        """TF-API-01: request valid menghasilkan HTTP 200."""
        r = api_client.post("/api/v1/grade/inline", json=MINIMAL_INLINE_PAYLOAD)
        assert r.status_code == 200

    def test_tf_api_02_response_contains_score(self, api_client: TestClient):
        """TF-API-02: respons mengandung field 'score' bernilai float 0–100."""
        r = api_client.post("/api/v1/grade/inline", json=MINIMAL_INLINE_PAYLOAD)
        body = r.json()
        assert "score" in body
        assert 0.0 <= body["score"] <= 100.0

    def test_tf_api_03_response_contains_feedback(self, api_client: TestClient):
        """TF-API-03: respons mengandung field 'feedback' berupa string tidak kosong."""
        r = api_client.post("/api/v1/grade/inline", json=MINIMAL_INLINE_PAYLOAD)
        body = r.json()
        assert "feedback" in body
        assert isinstance(body["feedback"], str)
        assert body["feedback"] != ""

    def test_tf_api_04_response_contains_feedback_detail_criteria(
        self, api_client: TestClient
    ):
        """TF-API-04: feedback_detail.criteria berisi daftar penilaian per kriteria."""
        r = api_client.post("/api/v1/grade/inline", json=MINIMAL_INLINE_PAYLOAD)
        body = r.json()
        detail = body.get("feedback_detail")
        assert detail is not None
        assert isinstance(detail["criteria"], list)
        assert len(detail["criteria"]) > 0
        for c in detail["criteria"]:
            assert "name" in c
            assert "score" in c
            assert "max_score" in c
            assert "comment" in c

    def test_tf_api_05_reasoning_absent_when_with_reason_false(
        self, api_client: TestClient
    ):
        """TF-API-05: reasoning = null saat with_reason=false (default)."""
        payload = {**MINIMAL_INLINE_PAYLOAD, "with_reason": False}
        r = api_client.post("/api/v1/grade/inline", json=payload)
        assert r.json().get("reasoning") is None

    def test_tf_api_06_reasoning_present_when_with_reason_true(self, fake_provider):
        """TF-API-06: reasoning terisi saat with_reason=true."""
        from main import app
        from src.api.dependencies import get_llm_provider

        fake_provider.response = canned_raw(with_thinking=True)
        app.dependency_overrides[get_llm_provider] = lambda: fake_provider
        with TestClient(app) as client:
            r = client.post(
                "/api/v1/grade/inline",
                json={**MINIMAL_INLINE_PAYLOAD, "with_reason": True},
            )
        app.dependency_overrides.clear()

        body = r.json()
        assert body["reasoning"] is not None
        assert len(body["reasoning"]) > 0

    def test_tf_api_07_missing_code_returns_422(self, api_client: TestClient):
        """TF-API-07: request tanpa field 'code' wajib menghasilkan HTTP 422."""
        r = api_client.post(
            "/api/v1/grade/inline", json={"problems": "Tulis fungsi penjumlahan."}
        )
        assert r.status_code == 422

    def test_tf_api_08_missing_problems_returns_422(self, api_client: TestClient):
        """TF-API-08: request tanpa field 'problems' wajib menghasilkan HTTP 422."""
        r = api_client.post(
            "/api/v1/grade/inline",
            json={"code": "def f(): pass"},
        )
        assert r.status_code == 422

    def test_tf_api_09_empty_code_returns_422(self, api_client: TestClient):
        """TF-API-09: kode yang hanya berisi spasi ditolak dengan HTTP 422."""
        r = api_client.post(
            "/api/v1/grade/inline",
            json={"problems": "Soal", "code": "   "},
        )
        assert r.status_code == 422

    def test_tf_api_10_score_value_matches_provider_response(self, fake_provider):
        """TF-API-10: nilai skor di respons HTTP = nilai skor dari FakeProvider."""
        from main import app
        from src.api.dependencies import get_llm_provider

        fake_provider.response = canned_raw(score=73)
        app.dependency_overrides[get_llm_provider] = lambda: fake_provider
        with TestClient(app) as client:
            r = client.post("/api/v1/grade/inline", json=MINIMAL_INLINE_PAYLOAD)
        app.dependency_overrides.clear()

        assert r.json()["score"] == 73.0


# ─────────────────────────── /grade/file ──────────────────────────────────────


class TestFileEndpoint:
    """TF-API-11 hingga TF-API-13 — POST /api/v1/grade/file."""

    def test_tf_api_11_valid_file_returns_200(self, api_client: TestClient):
        """TF-API-11: upload file Python valid menghasilkan HTTP 200 beserta skor."""
        code = b"def sum_array(arr):\n    return sum(arr)\n"
        r = api_client.post(
            "/api/v1/grade/file",
            data={"problems": "Tulis fungsi penjumlahan."},
            files={"code": ("solution.py", io.BytesIO(code), "text/plain")},
        )
        assert r.status_code == 200
        assert 0.0 <= r.json()["score"] <= 100.0

    def test_tf_api_12_non_utf8_file_returns_400(self, api_client: TestClient):
        """TF-API-12: file binary non-UTF-8 menghasilkan HTTP 400."""
        r = api_client.post(
            "/api/v1/grade/file",
            data={"problems": "Soal"},
            files={"code": ("bad.py", io.BytesIO(b"\xff\xfe\x00"), "text/plain")},
        )
        assert r.status_code == 400

    def test_tf_api_13_file_content_reaches_provider(
        self, fake_provider: FakeProvider
    ):
        """TF-API-13: isi file yang diupload terkirim ke LLM (ada di prompt)."""
        from main import app
        from src.api.dependencies import get_llm_provider

        app.dependency_overrides[get_llm_provider] = lambda: fake_provider
        code = b"def magic():\n    return 42\n"
        with TestClient(app) as client:
            client.post(
                "/api/v1/grade/file",
                data={"problems": "Soal unik."},
                files={"code": ("magic.py", io.BytesIO(code), "text/plain")},
            )
        app.dependency_overrides.clear()

        assert any("def magic()" in call for call in fake_provider.calls)


# ─────────────────────────── /grade/batch ─────────────────────────────────────


class TestBatchEndpoint:
    """TF-API-14 hingga TF-API-16 — POST /api/v1/grade/batch."""

    def _make_zip(self, files: dict[str, bytes]) -> io.BytesIO:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        buf.seek(0)
        return buf

    def test_tf_api_14_batch_returns_xlsx(self, api_client: TestClient):
        """TF-API-14: batch ZIP menghasilkan respons Excel (.xlsx)."""
        zf = self._make_zip(
            {
                "student_a.py": b"def f(): return 1",
                "student_b.py": b"def f(): return 2",
            }
        )
        r = api_client.post(
            "/api/v1/grade/batch",
            data={"problems": "Soal batch."},
            files={"files": ("submissions.zip", zf, "application/zip")},
        )
        assert r.status_code == 200
        assert "spreadsheet" in r.headers["content-type"]

    def test_tf_api_15_batch_empty_zip_returns_400(self, api_client: TestClient):
        """TF-API-15: ZIP kosong (tanpa file kode) menghasilkan HTTP 400."""
        zf = self._make_zip({})
        r = api_client.post(
            "/api/v1/grade/batch",
            data={"problems": "Soal."},
            files={"files": ("empty.zip", zf, "application/zip")},
        )
        assert r.status_code == 400

    def test_tf_api_16_batch_invalid_zip_returns_400(self, api_client: TestClient):
        """TF-API-16: file ZIP rusak/bukan ZIP menghasilkan HTTP 400."""
        r = api_client.post(
            "/api/v1/grade/batch",
            data={"problems": "Soal."},
            files={"files": ("not_a_zip.zip", io.BytesIO(b"ini bukan zip"), "application/zip")},
        )
        assert r.status_code == 400
