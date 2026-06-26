import logging

from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_current_user
from services import session_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/results", tags=["results"])


@router.get("/{session_id}")
async def get_results(session_id: str, user=Depends(get_current_user)):
    session = session_store.get_session_for_user(session_id, user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    result = session_store.get_result(session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Results not ready")

    return {"session": session, "result": result}
