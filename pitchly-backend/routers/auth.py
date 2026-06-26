import logging

from fastapi import APIRouter
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


class AuthEvent(BaseModel):
    type: str = Field(..., max_length=50, description="Event type: login, logout, signup")


@router.post("/log")
async def log_auth_event(event: AuthEvent) -> dict[str, str]:
    # Responsibility: Record non-sensitive authentication events (no auth required).
    logger.info("Auth event: type=%s", event.type)
    return {"status": "logged"}
