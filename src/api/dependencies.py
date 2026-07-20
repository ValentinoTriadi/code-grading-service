from fastapi import Depends

from src.api.controllers.grading import GradingController
from src.config.settings import Settings, settings
from src.engine.input_handler import InputHandler
from src.engine.llm_interface import LLMInterface, RequestRateLimiter
from src.engine.prompt_orchestrator import PromptOrchestrator
from src.engine.response_parser import ResponseParser
from src.llm.base import BaseLLMProvider
from src.prompts.builder import PromptBuilder
from src.services.grading_service import GradingService


llm_rate_limiter = RequestRateLimiter(
    max_requests_per_minute=settings.llm_requests_per_minute
)


def get_settings() -> Settings:
    return settings


def get_prompt_builder() -> PromptBuilder:
    return PromptBuilder()


def get_input_handler() -> InputHandler:
    return InputHandler()


def get_prompt_orchestrator(
    prompt_builder: PromptBuilder = Depends(get_prompt_builder),
) -> PromptOrchestrator:
    return PromptOrchestrator(prompt_builder=prompt_builder)


def get_llm_provider(cfg: Settings = Depends(get_settings)) -> BaseLLMProvider:
    """Select and instantiate the configured LLM provider."""
    provider = cfg.llm_provider.lower()

    if provider == "openai":
        from src.llm.openai import OpenAIProvider

        return OpenAIProvider(
            api_key=cfg.llm_api_key,
            base_url=cfg.llm_base_url,
            model=cfg.llm_model_name,
            max_tokens=cfg.llm_max_tokens,
            temperature=cfg.llm_temperature,
        )

    if provider == "gemini":
        from src.llm.gemini import GeminiProvider

        return GeminiProvider(
            api_key=cfg.llm_api_key,
            model=cfg.llm_model_name,
            max_tokens=cfg.llm_max_tokens,
            temperature=cfg.llm_temperature,
            use_vertex=cfg.gemini_use_vertex,
            project=cfg.google_cloud_project or None,
            location=cfg.google_cloud_location or None,
        )

    if provider == "anthropic":
        from src.llm.anthropic import AnthropicProvider

        return AnthropicProvider(
            api_key=cfg.llm_api_key,
            model=cfg.llm_model_name,
            max_tokens=cfg.llm_max_tokens,
            temperature=cfg.llm_temperature,
        )

    raise ValueError(
        f"Unsupported LLM provider: '{cfg.llm_provider}'. "
        "Set LLM_PROVIDER to 'openai', 'gemini', or 'anthropic' in your .env file."
    )


def get_llm_interface(
    provider: BaseLLMProvider = Depends(get_llm_provider),
) -> LLMInterface:
    return LLMInterface(provider=provider, rate_limiter=llm_rate_limiter)


def get_response_parser() -> ResponseParser:
    return ResponseParser()


def get_grading_service(
    input_handler: InputHandler = Depends(get_input_handler),
    prompt_orchestrator: PromptOrchestrator = Depends(get_prompt_orchestrator),
    llm_interface: LLMInterface = Depends(get_llm_interface),
    response_parser: ResponseParser = Depends(get_response_parser),
) -> GradingService:
    return GradingService(
        input_handler=input_handler,
        prompt_orchestrator=prompt_orchestrator,
        llm_interface=llm_interface,
        response_parser=response_parser,
    )


def get_grading_controller(
    service: GradingService = Depends(get_grading_service),
    cfg: Settings = Depends(get_settings),
) -> GradingController:
    return GradingController(service=service, batch_concurrency=cfg.batch_concurrency)
