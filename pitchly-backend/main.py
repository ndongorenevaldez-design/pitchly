import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from routers import auth, dashboard, results, session, upload

settings = get_settings()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(title="Pitchly API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(session.router)
app.include_router(upload.router)
app.include_router(results.router)
app.include_router(dashboard.router)


@app.get("/health")
def health() -> dict[str, str]:
    # Responsibility: Report API health and active storage backend.
    return {
        "status": "ok",
        "environment": settings.environment,
        "storage_bucket": settings.supabase_storage_bucket,
    }
