import logging

import google.genai as genai
from google.genai import types

from src.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    """LLM provider backed by the Google Gemini API.

    Supports two auth modes:
    - Vertex AI: pass `use_vertex=True` with `project` and `location` —
      the SDK picks up Application Default Credentials
      (`gcloud auth application-default login` for local dev, or the
      runtime service account on GCP).
    - AI Studio: pass `api_key` (from https://aistudio.google.com).
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.0,
        use_vertex: bool = False,
        project: str | None = None,
        location: str | None = None,
    ) -> None:
        if use_vertex:
            if not project or not location:
                raise ValueError(
                    "Vertex AI mode requires GOOGLE_CLOUD_PROJECT and "
                    "GOOGLE_CLOUD_LOCATION (set GEMINI_USE_VERTEX=false to "
                    "fall back to API key auth)."
                )
            self.client = genai.Client(
                vertexai=True, project=project, location=location
            )
            logger.info(
                "GeminiProvider initialised on Vertex AI — project=%s location=%s",
                project,
                location,
            )
        else:
            if not api_key:
                raise ValueError(
                    "AI Studio mode requires LLM_API_KEY (or set "
                    "GEMINI_USE_VERTEX=true with project/location)."
                )
            self.client = genai.Client(api_key=api_key)
            logger.info("GeminiProvider initialised on AI Studio (API key)")

        self.model_name = model
        self.config = types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )

    async def generate(self, prompt: str, **kwargs) -> str:
        logger.debug("Gemini request — model=%s", self.model_name)
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=self.config,
        )
        if response.usage_metadata:
            m = response.usage_metadata
            logger.info(
                "Gemini usage — prompt=%d, candidates=%d, total=%d tokens",
                m.prompt_token_count,
                m.candidates_token_count,
                m.total_token_count,
            )
        return response.text or ""
