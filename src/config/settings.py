from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Configuration
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model_name: str = ""
    llm_provider: str = ""  # e.g. "openai", "gemini", "anthropic"
    llm_max_tokens: int = 8192
    llm_temperature: float = 0
    llm_requests_per_minute: int = 5

    # Gemini-on-Vertex (alternative to LLM_API_KEY when LLM_PROVIDER=gemini).
    # When true the provider authenticates via Application Default Credentials
    # against the given project/location instead of an API key.
    gemini_use_vertex: bool = False
    google_cloud_project: str = ""
    google_cloud_location: str = ""

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    batch_concurrency: int = 5

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
