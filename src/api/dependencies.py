from fastapi import Depends

from src.api.controllers.grading import GradingController
from src.config.settings import Settings, settings
from src.engine.input_handler import InputHandler
from src.engine.llm_interface import LLMInterface
from src.engine.prompt_orchestrator import PromptOrchestrator
from src.engine.response_parser import ResponseParser
from src.llm.base import BaseLLMProvider
from src.prompts.builder import PromptBuilder
from src.services.grading_service import GradingService


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
    # TODO: Register concrete providers here as they are implemented, e.g.:
    # if cfg.llm_provider == "openai":
    #     from src.llm.openai import OpenAIProvider
    #     return OpenAIProvider(api_key=cfg.llm_api_key, model=cfg.llm_model_name)
    # if cfg.llm_provider == "gemini":
    #     from src.llm.gemini import GeminiProvider
    #     return GeminiProvider(api_key=cfg.llm_api_key, model=cfg.llm_model_name)
    raise NotImplementedError(f"LLM provider '{cfg.llm_provider}' is not configured")


def get_llm_interface(
    provider: BaseLLMProvider = Depends(get_llm_provider),
) -> LLMInterface:
    return LLMInterface(provider=provider)


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
) -> GradingController:
    return GradingController(service=service)
