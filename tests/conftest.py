"""Shared pytest fixtures for the code-grading-service test suite."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


def pytest_configure(config):
    """Metadata yang muncul di header report HTML."""
    config.stash["metadata"] = getattr(config, "_metadata", {})


def pytest_html_report_title(report):
    report.title = "Laporan Pengujian — Layanan Penilaian Kode Berbasis LLM"


def pytest_html_results_summary(prefix, summary, postfix):
    prefix.extend([
        "<p><strong>Proyek:</strong> Layanan Penilaian Kode Program Mahasiswa Berbasis LLM dengan Prompt Engineering</p>",
        "<p><strong>Pengembang:</strong> Valentino Triadi · NIM 13522164 · IF4092 Tugas Akhir</p>",
        "<p><strong>Lapis pengujian:</strong> "
        "A — Fungsional per-modul (unit) · "
        "B — Fungsional end-to-end (pipeline + HTTP) · "
        "C — Non-fungsional live (dijalankan terpisah)</p>",
        "<p><strong>LLM:</strong> FakeProvider (deterministik, offline) untuk lapis A &amp; B.</p>",
    ])

from main import app
from src.api.dependencies import get_llm_provider
from tests._fakes import FakeProvider, canned_raw


@pytest.fixture()
def fake_provider() -> FakeProvider:
    return FakeProvider()


@pytest.fixture()
def api_client(fake_provider: FakeProvider) -> TestClient:
    """TestClient with the LLM provider overridden to FakeProvider."""
    app.dependency_overrides[get_llm_provider] = lambda: fake_provider
    with TestClient(app, raise_server_exceptions=True) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture()
def api_client_llm_error() -> TestClient:
    """TestClient whose LLM always raises a RuntimeError (simulates LLM outage)."""
    broken = FakeProvider(raises=RuntimeError("LLM service unavailable"))
    app.dependency_overrides[get_llm_provider] = lambda: broken
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture()
def api_client_score(score: int) -> TestClient:
    """Parameterisable client — override `score` fixture in the test."""
    provider = FakeProvider(response=canned_raw(score=score))
    app.dependency_overrides[get_llm_provider] = lambda: provider
    with TestClient(app, raise_server_exceptions=True) as client:
        yield client
    app.dependency_overrides.clear()


# ------------------------------------------------------------------ helpers --

MINIMAL_INLINE_PAYLOAD = {
    "problems": "Tulis fungsi yang menjumlahkan semua elemen array.",
    "code": "def sum_array(arr):\n    return sum(arr)",
}

# ---------------------------------------------------------- live fixtures ----

import os as _os

_LIVE = (
    _os.getenv("GEMINI_USE_VERTEX", "").lower() in ("1", "true")
    and _os.getenv("LLM_PROVIDER", "").lower() == "gemini"
    and _os.getenv("GOOGLE_CLOUD_PROJECT", "") != ""
)


@pytest.fixture()
def live_provider():
    """GeminiProvider nyata — skip seluruh test jika env tidak diset."""
    if not _LIVE:
        pytest.skip(
            "Live provider tidak tersedia — set GEMINI_USE_VERTEX=true, "
            "LLM_PROVIDER=gemini, GOOGLE_CLOUD_PROJECT"
        )
    from src.config.settings import settings
    from src.llm.gemini import GeminiProvider

    return GeminiProvider(
        api_key=settings.llm_api_key,
        model=settings.llm_model_name,
        max_tokens=settings.llm_max_tokens,
        temperature=settings.llm_temperature,
        use_vertex=settings.gemini_use_vertex,
        project=settings.google_cloud_project or None,
        location=settings.google_cloud_location or None,
    )


@pytest.fixture()
def api_client_live(live_provider) -> TestClient:
    """TestClient dengan GeminiProvider asli diinjeksi via dependency override."""
    app.dependency_overrides[get_llm_provider] = lambda: live_provider
    with TestClient(app, raise_server_exceptions=True) as client:
        yield client
    app.dependency_overrides.clear()
