from pathlib import Path


TEMPLATES_DIR = Path(__file__).parent / "templates"

DEFAULT_RUBRIC = (
    "1. Correctness (50%): Does the code produce correct output and satisfy "
    "every requirement stated in the problem?\n"
    "2. Readability (25%): Is the code easy to read? "
    "(naming, structure, indentation, comments where they help)\n"
    "3. Efficiency (25%): Does the code use a reasonable approach without "
    "unnecessary work or redundancy for the input sizes implied by the problem?"
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

        parts = ["Below are example gradings showing the expected style and rigor.\n"]
        for i, ex in enumerate(examples, start=1):
            parts.append(
                f"--- Example {i} ---\n"
                f"Problem: {ex.get('problem', '')}\n"
                f"Student code:\n```\n{ex.get('code', '')}\n```\n"
                f"Grading:\n{ex.get('grading', '')}\n"
                f"--- End of example {i} ---"
            )
        parts.append(
            "\nMatch the structure, depth, and tone of these examples in your own grading."
        )
        return "\n\n".join(parts)
