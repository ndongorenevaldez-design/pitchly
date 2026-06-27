# Responsibility: Admin-only endpoints for dashboard and user management

import logging

from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_current_user
from app.supabase_client import get_supabase_admin

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])

ADMIN_EMAIL = "admin@gmail.com"


def require_admin(user):
    """Check if the current user is the admin."""
    email = getattr(user, "email", None)
    if email != ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.get("/stats")
async def get_admin_stats(user=Depends(get_current_user)):
    require_admin(user)
    admin = get_supabase_admin()

    users_resp = admin.table("users").select("id", count="exact").execute()
    total_users = users_resp.count or 0

    sessions_resp = admin.table("sessions").select("id", count="exact").execute()
    total_sessions = sessions_resp.count or 0

    complete_resp = admin.table("sessions").select("id", count="exact").eq("status", "complete").execute()
    complete_sessions = complete_resp.count or 0

    error_resp = admin.table("sessions").select("id", count="exact").eq("status", "error").execute()
    error_sessions = error_resp.count or 0

    results_resp = admin.table("results").select("score_global").execute()
    scores = [r["score_global"] for r in (results_resp.data or []) if r.get("score_global")]
    avg_score = round(sum(scores) / len(scores), 2) if scores else 0

    return {
        "total_users": total_users,
        "total_sessions": total_sessions,
        "completed_sessions": complete_sessions,
        "error_sessions": error_sessions,
        "processing_sessions": total_sessions - complete_sessions - error_sessions,
        "average_score": avg_score,
        "total_analyses": len(scores),
    }


@router.get("/users")
async def get_all_users(user=Depends(get_current_user)):
    require_admin(user)
    admin = get_supabase_admin()

    resp = admin.table("users").select(
        "id, full_name, email, avatar_url, total_sessions, avg_global_score, "
        "interview_sessions, social_sessions, best_score, streak_days, created_at, last_session_at"
    ).order("created_at", desc=True).execute()

    return {"users": resp.data or []}


@router.get("/sessions")
async def get_all_sessions(user=Depends(get_current_user), limit: int = 50):
    require_admin(user)
    admin = get_supabase_admin()

    resp = admin.table("sessions").select(
        "id, user_id, mode, job_title, scenario, status, processing_stage, "
        "completion_pct, created_at, completed_at"
    ).order("created_at", desc=True).limit(limit).execute()

    return {"sessions": resp.data or []}


@router.get("/results")
async def get_all_results(user=Depends(get_current_user), limit: int = 50):
    require_admin(user)
    admin = get_supabase_admin()

    resp = admin.table("results").select(
        "id, session_id, score_global, score_clarity, score_confidence, "
        "score_structure, score_relevance, score_listening, created_at"
    ).order("created_at", desc=True).limit(limit).execute()

    return {"results": resp.data or []}


@router.get("/sessions/{session_id}")
async def get_admin_session_detail(session_id: str, user=Depends(get_current_user)):
    require_admin(user)
    admin = get_supabase_admin()

    session_resp = admin.table("sessions").select("*").eq("id", session_id).execute()
    sessions = session_resp.data or []
    if not sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    result_resp = admin.table("results").select("*").eq("session_id", session_id).execute()
    results = result_resp.data or []

    return {
        "session": sessions[0],
        "result": results[0] if results else None,
    }
