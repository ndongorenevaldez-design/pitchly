# Responsibility: Supabase users table only

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from app.supabase_client import get_supabase_admin

logger = logging.getLogger(__name__)


def get_profile(user_id: str) -> dict[str, Any] | None:
    response = (
        get_supabase_admin()
        .table("users")
        .select("*")
        .eq("id", user_id)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None


def list_recent_sessions(user_id: str, limit: int = 10) -> list[dict[str, Any]]:
    response = (
        get_supabase_admin()
        .table("sessions")
        .select("*, results(*)")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data or []


def update_progress(user_id: str, mode: str, global_score: int) -> None:
    """Update aggregate user stats after a completed session."""
    try:
        profile = get_profile(user_id)
        if not profile:
            logger.warning("User profile not found: user_id=%s", user_id)
            return

        total = (profile.get("total_sessions") or 0) + 1
        interview_count = (profile.get("interview_sessions") or 0) + (
            1 if mode == "interview" else 0
        )
        social_count = (profile.get("social_sessions") or 0) + (
            1 if mode == "social" else 0
        )
        old_avg = profile.get("avg_global_score") or 0
        new_avg = round(((old_avg * (total - 1)) + global_score) / total, 2)

        extraversion = profile.get("extraversion_score") or 0
        if mode == "social":
            delta = max(1, (global_score - 50) // 10)
            extraversion = min(100, extraversion + delta)

        get_supabase_admin().table("users").update(
            {
                "total_sessions": total,
                "interview_sessions": interview_count,
                "social_sessions": social_count,
                "avg_global_score": new_avg,
                "extraversion_score": extraversion,
                "last_session_at": datetime.now(UTC).isoformat(),
            }
        ).eq("id", user_id).execute()

        logger.info(
            "User progress updated: user_id=%s total=%d avg=%.1f",
            user_id,
            total,
            new_avg,
        )
    except Exception as exc:
        logger.error("Failed to update user progress: user_id=%s error=%s", user_id, str(exc))
