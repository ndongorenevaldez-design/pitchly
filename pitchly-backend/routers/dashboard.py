import logging

from fastapi import APIRouter, Depends

from dependencies import get_current_user
from services import user_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
async def get_dashboard(user=Depends(get_current_user)):
    return {
        "profile": user_store.get_profile(user.id),
        "sessions": user_store.list_recent_sessions(user.id),
    }
