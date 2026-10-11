from fastapi import FastAPI

from app.config import settings

app = FastAPI(title=settings.service_name)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": settings.service_name}
