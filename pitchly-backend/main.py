# Responsibility: FastAPI application entry point
# Wires together CORS, routers, and logging — NO business logic here

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

settings = get_settings()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Pitchly API",
    description="AI Communication Coaching Backend",
    version="1.0.0",
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Safe imports — app starts even if a router is not yet implemented
try:
    from routers import auth
    app.include_router(auth.router)
    logger.info("Auth router loaded")
except ImportError as e:
    logger.warning("Auth router not available: %s", e)

try:
    from routers import session
    app.include_router(session.router)
    logger.info("Session router loaded")
except ImportError as e:
    logger.warning("Session router not available: %s", e)

try:
    from routers import upload
    app.include_router(upload.router)
    logger.info("Upload router loaded")
except ImportError as e:
    logger.warning("Upload router not available: %s", e)

try:
    from routers import results
    app.include_router(results.router)
    logger.info("Results router loaded")
except ImportError as e:
    logger.warning("Results router not available: %s", e)

try:
    from routers import dashboard
    app.include_router(dashboard.router)
    logger.info("Dashboard router loaded")
except ImportError as e:
    logger.warning("Dashboard router not available: %s", e)


@app.get("/")
async def root():
    return {
        "status": "Pitchly API is running",
        "environment": settings.environment,
    }


@app.get("/health")
async def health():
    # Railway uses this endpoint for liveness checks
    return {"status": "ok"}