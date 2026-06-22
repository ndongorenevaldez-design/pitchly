import logging

from fastapi import APIRouter, Depends

from app.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/event")
async def log_auth_event(event: dict[str, str], user=Depends(get_current_user)):
    # Responsibility: Record non-sensitive authentication events.
    logger.info("Auth event: user_id=%s event=%s", user.id, event.get("type"))
    return {"status": "logged"}
