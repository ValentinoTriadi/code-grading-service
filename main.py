from fastapi import FastAPI

from src.api.routes.grading import router as grading_router

app = FastAPI(
    title="Code Grading Service",
    description="Layanan penilaian kode program berbasis LLM dengan Prompt Engineering",
    version="0.1.0",
)

app.include_router(grading_router)


@app.get("/health")
async def health_check():
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
