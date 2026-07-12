"""TF-GS — Pengujian fungsional GradingService (pipeline end-to-end tanpa HTTP).

GradingService mengorkestrasikan empat modul engine:
  InputHandler → PromptOrchestrator → LLMInterface → ResponseParser

Semua test berjalan offline (LLM di-mock via FakeProvider).
"""

from __future__ import annotations

import pytest

from src.api.schemas.request import GradingRequest
from tests._fakes import FakeProvider, canned_raw, make_service


# ------------------------------------------------------------------ fixtures --


def _req(**kw) -> GradingRequest:
    defaults = dict(
        problem_description="Tulis fungsi menjumlahkan elemen array.",
        student_code="def sum_array(arr):\n    return sum(arr)",
    )
    return GradingRequest(**{**defaults, **kw})


# -------------------------------------------------------------------- tests ---


class TestGradingServicePipeline:
    """TF-GS-01 hingga TF-GS-05 — Pipeline fungsional."""

    @pytest.mark.anyio
    async def test_tf_gs_01_returns_valid_grading_response(self):
        """TF-GS-01: grade() mengembalikan GradingResponse dengan skor 0–100."""
        svc = make_service(FakeProvider())
        result = await svc.grade(_req())

        assert 0.0 <= result.score <= 100.0
        assert result.feedback != ""

    @pytest.mark.anyio
    async def test_tf_gs_02_score_matches_provider_output(self):
        """TF-GS-02: skor yang dikembalikan cocok dengan nilai di respons LLM."""
        svc = make_service(FakeProvider(response=canned_raw(score=72)))
        result = await svc.grade(_req())

        assert result.score == 72.0

    @pytest.mark.anyio
    async def test_tf_gs_03_feedback_detail_criteria_present(self):
        """TF-GS-03: feedback_detail berisi daftar kriteria yang tidak kosong."""
        svc = make_service(FakeProvider())
        result = await svc.grade(_req())

        assert result.feedback_detail is not None
        assert len(result.feedback_detail.criteria) > 0

    @pytest.mark.anyio
    async def test_tf_gs_04_reasoning_populated_when_with_reason_true(self):
        """TF-GS-04: reasoning terisi saat with_reason=True dan LLM memberi <THINKING>."""
        svc = make_service(FakeProvider(response=canned_raw(with_thinking=True)))
        result = await svc.grade(_req(with_reason=True))

        assert result.reasoning is not None
        assert len(result.reasoning) > 0

    @pytest.mark.anyio
    async def test_tf_gs_05_pipeline_calls_provider_exactly_once(self):
        """TF-GS-05: LLM dipanggil tepat satu kali per request grading."""
        provider = FakeProvider()
        svc = make_service(provider)
        await svc.grade(_req())

        assert len(provider.calls) == 1

    @pytest.mark.anyio
    async def test_tf_gs_06_provider_receives_problem_in_prompt(self):
        """TF-GS-06: prompt yang dikirim ke LLM mengandung deskripsi soal."""
        provider = FakeProvider()
        svc = make_service(provider)
        req = _req(problem_description="Implementasikan LRU Cache.")
        await svc.grade(req)

        assert "Implementasikan LRU Cache." in provider.calls[0]

    @pytest.mark.anyio
    async def test_tf_gs_07_provider_receives_student_code_in_prompt(self):
        """TF-GS-07: prompt yang dikirim ke LLM mengandung kode mahasiswa."""
        provider = FakeProvider()
        svc = make_service(provider)
        req = _req(student_code="class Node:\n    pass")
        await svc.grade(req)

        assert "class Node:" in provider.calls[0]

    @pytest.mark.anyio
    async def test_tf_gs_08_progress_callback_called_four_times(self):
        """TF-GS-08: on_progress dipanggil tepat 4 kali (satu per tahap pipeline)."""
        svc = make_service(FakeProvider())
        steps: list[tuple[int, int, str]] = []

        async def capture(step, total, msg):
            steps.append((step, total, msg))

        await svc.grade(_req(), on_progress=capture)

        assert len(steps) == 4
        assert [s[0] for s in steps] == [1, 2, 3, 4]

    @pytest.mark.anyio
    async def test_tf_gs_09_empty_code_raises_before_calling_provider(self):
        """TF-GS-09: kode kosong gagal di InputHandler; provider tidak pernah dipanggil."""
        from pydantic import ValidationError

        provider = FakeProvider()
        with pytest.raises(ValidationError):
            GradingRequest(
                problem_description="Soal",
                student_code="   ",
            )

        assert len(provider.calls) == 0

    @pytest.mark.anyio
    async def test_tf_gs_10_llm_error_propagates_as_exception(self):
        """TF-GS-10: jika LLM gagal, exception diteruskan ke caller (tidak ditelan)."""
        svc = make_service(FakeProvider(raises=RuntimeError("timeout")))
        with pytest.raises(RuntimeError, match="timeout"):
            await svc.grade(_req())

    @pytest.mark.anyio
    async def test_tf_gs_11_parser_fallback_gives_zero_score_on_garbage(self):
        """TF-GS-11: jika LLM menghasilkan teks tidak terstruktur, skor = 0.0 (fallback)."""
        svc = make_service(FakeProvider(response="maaf, saya tidak mengerti."))
        result = await svc.grade(_req())

        assert result.score == 0.0
        assert result.feedback_detail is None

    @pytest.mark.anyio
    async def test_tf_gs_12_custom_rubric_injected_into_prompt(self):
        """TF-GS-12: rubrik kustom muncul di prompt yang dikirim ke LLM."""
        provider = FakeProvider()
        svc = make_service(provider)
        custom_rubric = "Correctness 50, Style 50"
        await svc.grade(_req(rubric=custom_rubric))

        assert custom_rubric in provider.calls[0]
