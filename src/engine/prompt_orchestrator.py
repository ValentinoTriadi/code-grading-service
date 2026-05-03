import logging

from src.api.schemas.request import GradingRequest
from src.prompts.builder import PromptBuilder

logger = logging.getLogger(__name__)


_FEEDBACK_JSON_SCHEMA = """\
<FEEDBACK_JSON>
{
  "summary": "[Ringkasan singkat dalam Markdown — boleh gunakan **bold** dan backtick]",
  "criteria": [
    {
      "name": "[Nama kriteria sesuai rubrik]",
      "score": [Skor numerik untuk kriteria ini],
      "max_score": [Skor maksimum untuk kriteria ini],
      "comment": "[Komentar dalam Markdown — gunakan backtick untuk nama variabel/fungsi, bold untuk poin penting]"
    }
  ],
  "suggestions": [
    "[Saran perbaikan spesifik dan actionable dalam Markdown. Gunakan pengetahuan pemrograman umum: sebut fungsi bawaan, library standar, idiom, atau pola yang lebih baik jika relevan. Contoh: 'Pertimbangkan menggunakan `sum()` bawaan Python daripada loop manual.' Kosongkan array ini jika kode sudah optimal.]"
  ]
}
</FEEDBACK_JSON>"""

_OUTPUT_FORMAT_WITH_REASON = (
    "Berikan penilaian dalam format berikut (WAJIB diikuti dengan tepat).\n"
    "PENTING: Setiap tag pembuka HARUS ditulis lengkap dengan tanda `>`, contoh: `<REASONING>` bukan `<REASONING`.\n\n"
    "<REASONING>\n"
    "[Gunakan Markdown. Tuliskan proses penalaran langkah demi langkah: "
    "pahami soal, analisis kode, evaluasi per kriteria dengan justifikasi, hitung skor akhir. "
    "Gunakan **bold** untuk nama kriteria, bullet list untuk poin-poin, dan backtick untuk nama variabel/fungsi.]\n"
    "</REASONING>\n\n"
    "<SCORE>[Skor numerik antara 0-100, contoh: 75]</SCORE>\n\n"
    "<FEEDBACK>\n"
    "[Gunakan Markdown. Tulis ringkasan penilaian yang konstruktif dan spesifik. "
    "Gunakan **bold** untuk poin penting, bullet list untuk kelebihan dan kekurangan, "
    "dan backtick untuk menyebut nama variabel atau fungsi.]\n"
    "</FEEDBACK>\n\n" + _FEEDBACK_JSON_SCHEMA
)

_OUTPUT_FORMAT_WITHOUT_REASON = (
    "Berikan penilaian dalam format berikut (WAJIB diikuti dengan tepat).\n"
    "PENTING: Setiap tag pembuka HARUS ditulis lengkap dengan tanda `>`, contoh: `<SCORE>` bukan `<SCORE`.\n\n"
    "<SCORE>[Skor numerik antara 0-100, contoh: 75]</SCORE>\n\n"
    "<FEEDBACK>\n"
    "[Gunakan Markdown. Tulis ringkasan penilaian yang konstruktif dan spesifik. "
    "Gunakan **bold** untuk poin penting, bullet list untuk kelebihan dan kekurangan, "
    "dan backtick untuk menyebut nama variabel atau fungsi.]\n"
    "</FEEDBACK>\n\n" + _FEEDBACK_JSON_SCHEMA
)


class PromptOrchestrator:
    """Constructs the full grading prompt by combining all sections."""

    def __init__(self, prompt_builder: PromptBuilder) -> None:
        self.prompt_builder = prompt_builder

    def build(self, request: GradingRequest) -> str:
        """Assemble the complete prompt for the LLM.

        Section order:
        1. System prompt (persona)
        2. Rubric (custom or default)
        3. Chain-of-Thought instruction (only when with_reason=True)
        4. Few-shot examples (only when provided)
        5. Task: problem description + student code
        6. Output format instruction
        """
        sections: list[str] = [
            self.prompt_builder.build_system_prompt(),
            self.prompt_builder.build_rubric_section(request.rubric),
        ]

        if request.with_reason:
            sections.append(self.prompt_builder.build_cot_instruction())

        few_shot = self.prompt_builder.build_few_shot_section(request.few_shot_examples)
        if few_shot:
            sections.append(few_shot)

        sections.append(self._build_task_section(request))
        sections.append(
            _OUTPUT_FORMAT_WITH_REASON
            if request.with_reason
            else _OUTPUT_FORMAT_WITHOUT_REASON
        )

        prompt = "\n\n".join(sections)
        logger.debug(
            "Prompt built — %d sections, %d chars total", len(sections), len(prompt)
        )
        return prompt

    def _build_task_section(self, request: GradingRequest) -> str:
        return (
            f"Soal:\n{request.problem_description}\n\n"
            f"Kode Mahasiswa:\n```\n{request.student_code}\n```"
        )
