from src.api.schemas.request import GradingRequest
from src.prompts.builder import PromptBuilder


class PromptOrchestrator:
    """Constructs dynamic prompts by combining system prompt, rubric,
    Chain of Thought instructions, few-shot examples, and student code."""

    def __init__(self, prompt_builder: PromptBuilder):
        self.prompt_builder = prompt_builder

    def build(self, request: GradingRequest) -> str:
        """Assemble the full prompt from all components.

        Combines:
        1. System prompt (persona penilai)
        2. Rubric penilaian (if provided)
        3. Chain of Thought instruction
        4. Few-shot examples (if provided)
        5. Student code + problem description
        """
        # TODO: Implement prompt assembly logic
        raise NotImplementedError
