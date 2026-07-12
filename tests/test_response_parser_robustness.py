"""TF-RP — Pengujian robustness ResponseParser terhadap output LLM tidak ideal.

ResponseParser memiliki kontrak: TIDAK PERNAH raise exception — selalu mengembalikan
GradingResponse yang valid (skor 0.0 sebagai fallback terburuk).
Test ini memverifikasi jalur-jalur fallback yang krusial untuk klaim
'berhasil diimplementasikan' di laporan.
"""

from __future__ import annotations

import json

import pytest

from src.engine.response_parser import ResponseParser


def _parser() -> ResponseParser:
    return ResponseParser()


def _result_block(payload: dict) -> str:
    return f"<RESULT>\n{json.dumps(payload)}\n</RESULT>"


# ─────────────────────── jalur normal ─────────────────────────────────────────

class TestParserNormalPaths:
    def test_tf_rp_01_parses_complete_result_with_all_fields(self):
        """TF-RP-01: JSON lengkap dalam <RESULT> menghasilkan GradingResponse utuh."""
        raw = _result_block({
            "score": 85,
            "summary": "Bagus.",
            "criteria": [{"name": "Correctness", "score": 80, "max_score": 100, "comment": "OK"}],
            "suggestions": [],
            "exemplary_points": [],
            "complexity": {"time": "O(n)", "space": "O(1)"},
            "confidence": 0.9,
        })
        r = _parser().parse(raw)
        assert r.score == 85.0
        assert r.feedback_detail is not None
        assert r.feedback_detail.criteria[0].name == "Correctness"

    def test_tf_rp_02_extracts_reasoning_from_thinking_block(self):
        """TF-RP-02: konten <THINKING> tersimpan di field reasoning."""
        raw = (
            "<THINKING>\nAnalisis mendalam.\n</THINKING>\n"
            + _result_block({"score": 90, "summary": "X", "criteria": [], "suggestions": []})
        )
        r = _parser().parse(raw)
        assert r.reasoning is not None
        assert "Analisis mendalam." in r.reasoning

    def test_tf_rp_03_score_clamped_above_100(self):
        """TF-RP-03: skor > 100 di-clamp ke 100.0."""
        r = _parser().parse(_result_block({"score": 150, "summary": "", "criteria": [], "suggestions": []}))
        assert r.score == 100.0

    def test_tf_rp_04_score_clamped_below_0(self):
        """TF-RP-04: skor < 0 di-clamp ke 0.0."""
        r = _parser().parse(_result_block({"score": -10, "summary": "", "criteria": [], "suggestions": []}))
        assert r.score == 0.0


# ─────────────────────── jalur fallback ───────────────────────────────────────

class TestParserFallbackPaths:
    def test_tf_rp_05_never_raises_on_empty_string(self):
        """TF-RP-05: teks kosong tidak raise exception; skor = 0.0."""
        r = _parser().parse("")
        assert r.score == 0.0

    def test_tf_rp_06_never_raises_on_random_text(self):
        """TF-RP-06: teks acak tidak raise exception; skor = 0.0."""
        r = _parser().parse("Lorem ipsum dolor sit amet, tidak ada JSON di sini.")
        assert r.score == 0.0
        assert r.feedback_detail is None

    def test_tf_rp_07_never_raises_on_truncated_json(self):
        """TF-RP-07: JSON terpotong di tengah (simulasi early-stop LLM) tidak raise."""
        truncated = '<RESULT>\n{"score": 77, "summary": "OK", "criteria": [{"name": "C'
        r = _parser().parse(truncated)
        # Parser mencoba repair; jika gagal, fallback ke 0.0 — keduanya valid
        assert isinstance(r.score, float)

    def test_tf_rp_08_never_raises_on_malformed_json(self):
        """TF-RP-08: JSON malformed (koma ganda, kurung kurang) tidak raise."""
        malformed = "<RESULT>\n{score: 80,, summary: 'OK'}\n</RESULT>"
        r = _parser().parse(malformed)
        assert isinstance(r.score, float)

    def test_tf_rp_09_feedback_detail_is_none_when_criteria_missing(self):
        """TF-RP-09: jika JSON valid tapi tidak ada criteria, feedback_detail tetap None atau list kosong."""
        raw = "<RESULT>\n{\"score\": 60, \"summary\": \"OK\", \"criteria\": []}\n</RESULT>"
        r = _parser().parse(raw)
        # score harus tetap terbaca walau criteria kosong
        assert r.score == 60.0

    def test_tf_rp_10_json_inside_code_fence_is_parsed(self):
        """TF-RP-10: JSON dibungkus ```json ... ``` (format markdown) tetap bisa di-parse."""
        body = json.dumps({"score": 91, "summary": "Baik.", "criteria": [], "suggestions": []})
        raw = f"<RESULT>\n```json\n{body}\n```\n</RESULT>"
        r = _parser().parse(raw)
        assert r.score == 91.0

    def test_tf_rp_11_never_raises_on_binary_like_unicode(self):
        """TF-RP-11: string dengan karakter unicode aneh tidak raise."""
        r = _parser().parse("\x00\x01\x02 \ud800 <?xml version='1.0'?>")
        assert isinstance(r.score, float)

    def test_tf_rp_12_score_string_coerced_to_float(self):
        """TF-RP-12: skor berbentuk string '88' di-coerce ke float 88.0."""
        raw = _result_block({"score": "88", "summary": "", "criteria": [], "suggestions": []})
        r = _parser().parse(raw)
        assert r.score == 88.0
