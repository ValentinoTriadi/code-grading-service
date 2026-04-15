import logging

from fastapi import FastAPI

from src.api.routes.grading import router as grading_router
from src.config.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

_DESCRIPTION = """
Layanan penilaian kode program mahasiswa berbasis LLM dengan Prompt Engineering.

## Modes

| Endpoint | Input | Output |
|---|---|---|
| `/grade/inline` | JSON body with code string | JSON |
| `/grade/file` | Multipart form with a source file | JSON |
| `/grade/batch` | Multipart form with a `.zip` archive | Excel (`.xlsx`) |

## Common Parameters

- **problems** — Problem statement given to students.
- **rubric** *(optional)* — Custom grading rubric. Uses a default rubric if omitted.
- **with_reason** *(optional, default `false`)* — Include the LLM's chain-of-thought reasoning in the response.

## Setup

Set the following in your `.env` file:

```
LLM_PROVIDER=openai       # or: gemini
LLM_API_KEY=sk-...
LLM_MODEL_NAME=gpt-4o     # or: gemini-1.5-pro
```
"""

_TAGS = [
    {
        "name": "grading",
        "description": "Endpoints for grading student code submissions.",
    },
    {
        "name": "health",
        "description": "Service liveness check.",
    },
]

app = FastAPI(
    title="Code Grading Service",
    description=_DESCRIPTION,
    version="0.1.0",
    openapi_tags=_TAGS,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(grading_router)
logger.info("Code Grading Service started — docs at /docs")


@app.get("/health", tags=["health"], summary="Health check")
async def health_check():
    """Returns `{"status": "ok"}` when the service is running."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    from src.config.settings import settings

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
