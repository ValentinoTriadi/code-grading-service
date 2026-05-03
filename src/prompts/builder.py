from pathlib import Path


TEMPLATES_DIR = Path(__file__).parent / "templates"

DEFAULT_RUBRIC = (
    "1. Kebenaran / Correctness (50%): Apakah kode menghasilkan output yang benar "
    "dan memenuhi semua requirement soal?\n"
    "2. Keterbacaan / Readability (25%): Apakah kode mudah dibaca? "
    "(penamaan variabel, struktur, indentasi)\n"
    "3. Efisiensi / Efficiency (25%): Apakah kode menggunakan pendekatan yang "
    "efisien dan tidak redundan?"
)


class PromptBuilder:
    """Loads and assembles prompt templates from text files."""

    def __init__(self, templates_dir: Path = TEMPLATES_DIR):
        self.templates_dir = templates_dir

    def load_template(self, filename: str) -> str:
        """Load a prompt template from file."""
        return (self.templates_dir / filename).read_text(encoding="utf-8")

    def build_system_prompt(self) -> str:
        return self.load_template("system.txt")

    def build_rubric_section(self, rubric: str | None = None) -> str:
        """Inject a custom rubric, or fall back to the default rubric."""
        template = self.load_template("rubric.txt")
        return template.replace("{{rubric}}", rubric or DEFAULT_RUBRIC)

    def build_cot_instruction(self) -> str:
        return self.load_template("cot_instruction.txt")

    def build_few_shot_section(self, examples: list[dict] | None = None) -> str:
        """Build few-shot examples section from a list of example dicts.

        Each dict should contain: 'problem', 'code', 'grading'.
        Returns an empty string if no examples are provided.
        """
        if not examples:
            return ""

        parts = ["Berikut adalah contoh penilaian yang diharapkan:\n"]
        for i, ex in enumerate(examples, start=1):
            parts.append(
                f"--- Contoh {i} ---\n"
                f"Soal: {ex.get('problem', '')}\n"
                f"Kode Mahasiswa:\n```\n{ex.get('code', '')}\n```\n"
                f"Penilaian:\n{ex.get('grading', '')}\n"
                f"--- Akhir Contoh {i} ---"
            )
        parts.append(
            "\nGunakan format dan gaya penilaian yang konsisten dengan contoh di atas."
        )
        return "\n\n".join(parts)
