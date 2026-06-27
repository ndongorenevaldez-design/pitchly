import logging

from fastapi import APIRouter, Depends

from dependencies import get_current_user
from services import user_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
async def get_dashboard(user=Depends(get_current_user)):
    try:
        profile = user_store.get_profile(user.id)
    except Exception as e:
        logger.error("Failed to fetch profile: %s", str(e))
        profile = None

    try:
        sessions = user_store.list_recent_sessions(user.id)
    except Exception as e:
        logger.error("Failed to fetch sessions: %s", str(e))
        sessions = []

    return {
        "profile": profile,
        "sessions": sessions,
    }
