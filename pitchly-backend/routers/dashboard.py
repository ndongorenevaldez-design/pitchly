from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.supabase_client import get_supabase_admin

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
async def get_dashboard(user=Depends(get_current_user)):
    # Responsibility: Return profile and recent practice history.
    client = get_supabase_admin()
    profile = client.table("users").select("*").eq("id", user.id).single().execute()
    sessions = (
        client.table("sessions")
        .select("*, results(*)")
        .eq("user_id", user.id)
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )
    return {"profile": profile.data, "sessions": sessions.data or []}
