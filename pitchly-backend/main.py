# Responsibility: FastAPI application entry point
# Wires together CORS, routers, and logging — NO business logic here

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from routers import auth, dashboard, results, session, upload, admin

settings = get_settings()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Pitchly API starting up…")
    try:
        from services.transcription import _get_model
        _get_model()
        logger.info("Whisper model preloaded at startup")
    except Exception as e:
        logger.warning("Whisper preload skipped: %s", str(e))
    yield
    logger.info("Pitchly API shutting down")


app = FastAPI(
    title="Pitchly API",
    description="AI Communication Coaching Backend",
    version="1.0.0",
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(session.router)
app.include_router(upload.router)
app.include_router(results.router)
app.include_router(dashboard.router)
app.include_router(admin.router)

logger.info("All routers loaded")


@app.get("/")
async def root():
    return {
        "status": "Pitchly API is running",
        "environment": settings.environment,
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
