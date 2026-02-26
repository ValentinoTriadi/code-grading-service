from pathlib import Path


TEMPLATES_DIR = Path(__file__).parent / "templates"


class PromptBuilder:
    """Loads and assembles prompt templates from text files."""

    def __init__(self, templates_dir: Path = TEMPLATES_DIR):
        self.templates_dir = templates_dir

    def load_template(self, filename: str) -> str:
        """Load a prompt template from file."""
        template_path = self.templates_dir / filename
        return template_path.read_text(encoding="utf-8")

    def build_system_prompt(self) -> str:
        """Load the system prompt template."""
        return self.load_template("system.txt")

    def build_rubric_section(self, rubric: str | None = None) -> str:
        """Build the rubric section of the prompt.

        If a custom rubric is provided, inject it into the template.
        Otherwise, use the default rubric template.
        """
        template = self.load_template("rubric.txt")
        if rubric:
            return template.replace("{{rubric}}", rubric)
        return template

    def build_cot_instruction(self) -> str:
        """Load the Chain of Thought instruction template."""
        return self.load_template("cot_instruction.txt")

    def build_few_shot_section(self, examples: list[dict] | None = None) -> str:
        """Build the few-shot examples section.

        If custom examples are provided, format and inject them.
        Otherwise, use the default examples from the template.
        """
        template = self.load_template("few_shot.txt")
        if examples:
            # TODO: Format and inject custom examples
            pass
        return template
