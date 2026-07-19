"""TF-NF — Pengujian non-fungsional: latensi dan reliability (live Gemini via Vertex AI).

CARA MENJALANKAN:
    # Pastikan ADC aktif dan .env berisi konfigurasi Gemini Vertex:
    gcloud auth application-default login
    export GEMINI_USE_VERTEX=true
    export GOOGLE_CLOUD_PROJECT=<project-id>
    export GOOGLE_CLOUD_LOCATION=asia-southeast1
    export LLM_PROVIDER=gemini
    export LLM_MODEL_NAME=gemini-2.5-flash

    uv run pytest tests/test_nonfunctional_live.py -v -s

Test ini di-skip otomatis jika env var GEMINI_USE_VERTEX / LLM_PROVIDER
tidak diset (agar CI offline tetap hijau).
"""

from __future__ import annotations

import asyncio
import os
import statistics
import time

import pytest

# ── skip seluruh modul jika konfigurasi live tidak tersedia ───────────────────
_LIVE = (
    os.getenv("GEMINI_USE_VERTEX", "").lower() in ("1", "true")
    and os.getenv("LLM_PROVIDER", "").lower() == "gemini"
    and os.getenv("GOOGLE_CLOUD_PROJECT", "") != ""
)
pytestmark = pytest.mark.skipif(
    not _LIVE,
    reason="Pengujian live dilewati — set GEMINI_USE_VERTEX=true, LLM_PROVIDER=gemini, GOOGLE_CLOUD_PROJECT",
)

# ── payload representatif (setara 1 submission nyata dari eksperimen) ──────────
_PROBLEM = (
    "Tulis fungsi Python `sum_array(arr: list[int]) -> int` yang mengembalikan "
    "jumlah semua elemen. Tangani: array kosong (kembalikan 0), elemen negatif, "
    "dan array bersarang (nested list)."
)
_CODE = """\
def sum_array(arr):
    if not arr:
        return 0
    total = 0
    for item in arr:
        if isinstance(item, list):
            total += sum_array(item)
        else:
            total += item
    return total
"""
_N_REQUESTS = 10          # jumlah request untuk mengukur latensi
_LATENCY_P95_LIMIT = 10   # detik — batas atas P95 yang masih dianggap acceptable
_RELIABILITY_MIN = 0.90   # 90% sukses = reliable


# ─────────────────────────── helpers ──────────────────────────────────────────

def _build_service():
    from src.api.dependencies import get_grading_service, get_settings
    # Buat service langsung dari dependency factory (sama seperti produksi)
    from src.config.settings import settings
    from src.engine.input_handler import InputHandler
    from src.engine.llm_interface import LLMInterface, RequestRateLimiter
    from src.engine.prompt_orchestrator import PromptOrchestrator
    from src.engine.response_parser import ResponseParser
    from src.llm.gemini import GeminiProvider
    from src.prompts.builder import PromptBuilder
    from src.services.grading_service import GradingService

    provider = GeminiProvider(
        api_key=settings.llm_api_key,
        model=settings.llm_model_name,
        max_tokens=settings.llm_max_tokens,
        temperature=settings.llm_temperature,
        use_vertex=settings.gemini_use_vertex,
        project=settings.google_cloud_project or None,
        location=settings.google_cloud_location or None,
    )
    return GradingService(
        input_handler=InputHandler(),
        prompt_orchestrator=PromptOrchestrator(prompt_builder=PromptBuilder()),
        llm_interface=LLMInterface(
            provider=provider,
            rate_limiter=RequestRateLimiter(max_requests_per_minute=settings.llm_requests_per_minute),
        ),
        response_parser=ResponseParser(),
    )


async def _one_request(service, with_reason: bool = True) -> tuple[float, bool, float | None]:
    """Jalankan satu request grading; kembalikan (latency_s, success, score)."""
    from src.api.schemas.request import GradingRequest

    req = GradingRequest(
        problem_description=_PROBLEM,
        student_code=_CODE,
        with_reason=with_reason,
    )
    t0 = time.perf_counter()
    try:
        result = await service.grade(req)
        elapsed = time.perf_counter() - t0
        return elapsed, True, result.score
    except Exception as exc:  # noqa: BLE001
        elapsed = time.perf_counter() - t0
        print(f"\n  [FAIL] {type(exc).__name__}: {exc}")
        return elapsed, False, None


# ─────────────────────────── tests ────────────────────────────────────────────


class TestLatency:
    """TF-NF-01 dan TF-NF-02 — Latensi response time."""

    @pytest.mark.anyio
    async def test_tf_nf_01_mean_latency_recorded(self):
        """TF-NF-01: Catat rata-rata latensi per request (N=10, sequential).

        Tidak ada assertion pass/fail di sini — tujuannya adalah MENGUKUR dan
        mencetak angka untuk dimasukkan ke laporan.
        """
        svc = _build_service()
        latencies = []
        scores = []

        print(f"\n\n{'='*10}")
        print(f"TF-NF-01 — Pengukuran Latensi (N={_N_REQUESTS} request, sequential)")
        print(f"{'='*10}")

        for i in range(_N_REQUESTS):
            lat, ok, score = await _one_request(svc)
            latencies.append(lat)
            if score is not None:
                scores.append(score)
            print(f"  Request {i+1:02d}: {lat:.2f}s  skor={score}  ok={ok}")

        mean_lat = statistics.mean(latencies)
        median_lat = statistics.median(latencies)
        p95_lat = sorted(latencies)[int(len(latencies) * 0.95)]
        min_lat = min(latencies)
        max_lat = max(latencies)

        print(f"\n  Hasil:")
        print(f"    N request         : {_N_REQUESTS}")
        print(f"    Latensi min       : {min_lat:.2f} s")
        print(f"    Latensi rata-rata : {mean_lat:.2f} s")
        print(f"    Latensi median    : {median_lat:.2f} s")
        print(f"    Latensi P95       : {p95_lat:.2f} s")
        print(f"    Latensi maks      : {max_lat:.2f} s")
        if scores:
            print(f"    Skor rata-rata    : {statistics.mean(scores):.1f}")
        print(f"{'='*10}\n")

        # Soft assertion — P95 harus di bawah batas acceptable
        assert p95_lat < _LATENCY_P95_LIMIT, (
            f"P95 latensi {p95_lat:.1f}s melebihi batas {_LATENCY_P95_LIMIT}s"
        )

    @pytest.mark.anyio
    async def test_tf_nf_02_single_request_latency_under_10s(self):
        """TF-NF-02: Satu request grading selesai dalam 10 detik."""
        svc = _build_service()
        lat, ok, score = await _one_request(svc)

        print(f"\n  TF-NF-02: latensi = {lat:.2f}s  ok={ok}  skor={score}")
        assert ok, "Request gagal (exception dari provider)"
        assert lat < 10.0, f"Latensi {lat:.1f}s > 10s"


class TestReliability:
    """TF-NF-03 — Reliability: persentase request sukses tanpa error/crash."""

    @pytest.mark.anyio
    async def test_tf_nf_03_reliability_above_90_percent(self):
        """TF-NF-03: Minimal 90% dari N=10 request berhasil (tidak crash, ada skor valid).

        'Berhasil' = tidak ada exception + skor 0–100 dikembalikan.
        Ini BERBEDA dari parse rate eksperimen (yang mengukur JSON valid dari LLM);
        ini mengukur keandalan layanan secara keseluruhan termasuk network, auth, quota.
        """
        svc = _build_service()
        results = []

        print(f"\n\n{'='*10}")
        print(f"TF-NF-03 — Pengukuran Reliability (N={_N_REQUESTS} request)")
        print(f"{'='*10}")

        for i in range(_N_REQUESTS):
            lat, ok, score = await _one_request(svc)
            results.append(ok)
            status = "OK  " if ok else "FAIL"
            print(f"  Request {i+1:02d}: [{status}]  {lat:.2f}s  skor={score}")

        n_success = sum(results)
        reliability = n_success / len(results)
        print(f"\n  Hasil:")
        print(f"    N request  : {_N_REQUESTS}")
        print(f"    Sukses     : {n_success}")
        print(f"    Gagal      : {_N_REQUESTS - n_success}")
        print(f"    Reliability: {reliability*100:.1f}%")
        print(f"    Batas min  : {_RELIABILITY_MIN*100:.0f}%")
        print(f"{'='*10}\n")

        assert reliability >= _RELIABILITY_MIN, (
            f"Reliability {reliability*100:.1f}% di bawah batas {_RELIABILITY_MIN*100:.0f}%"
            f" ({n_success}/{_N_REQUESTS} request berhasil)"
        )
