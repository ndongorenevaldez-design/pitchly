from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_current_user
from app.supabase_client import get_supabase_admin

router = APIRouter(prefix="/results", tags=["results"])


@router.get("/{session_id}")
async def get_results(session_id: str, user=Depends(get_current_user)):
    # Responsibility: Return analysis results owned by the authenticated user.
    session = (
        get_supabase_admin()
        .table("sessions")
        .select("*")
        .eq("id", session_id)
        .eq("user_id", user.id)
        .single()
        .execute()
    )
    if not session.data:
        raise HTTPException(status_code=404, detail="Session not found")

    result = (
        get_supabase_admin()
        .table("results")
        .select("*")
        .eq("session_id", session_id)
        .single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Results not ready")
    return {"session": session.data, "result": result.data}
