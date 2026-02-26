from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Configuration
    llm_api_key: str = ""
    llm_model_name: str = ""
    llm_provider: str = ""  # e.g. "openai", "gemini"
    llm_max_tokens: int = 4096
    llm_temperature: float = 0.0

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
