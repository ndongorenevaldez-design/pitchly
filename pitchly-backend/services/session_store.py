# Responsibility: Supabase sessions + results tables only

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from app.supabase_client import get_supabase_admin
from schemas.session import SessionCreate

logger = logging.getLogger(__name__)


def create_session(user_id: str, payload: SessionCreate) -> str:
    session_id = str(uuid4())
    data = {
        "id": session_id,
        "user_id": user_id,
        "mode": payload.mode,
        "job_title": payload.job_title,
        "scenario": payload.scenario,
        "duration_s": payload.duration_s,
        "status": "processing",
    }
    get_supabase_admin().table("sessions").insert(data).execute()
    logger.info("Session created: session_id=%s user_id=%s", session_id, user_id)
    return session_id


def get_session(session_id: str) -> dict[str, Any] | None:
    response = (
        get_supabase_admin()
        .table("sessions")
        .select("*")
        .eq("id", session_id)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None


def get_session_for_user(session_id: str, user_id: str) -> dict[str, Any] | None:
    session = get_session(session_id)
    if session and session.get("user_id") == user_id:
        return session
    return None


def attach_video_url(session_id: str, signed_url: str) -> None:
    get_supabase_admin().table("sessions").update({"video_url": signed_url}).eq(
        "id", session_id
    ).execute()


def update_session_status(session_id: str, status: str) -> None:
    get_supabase_admin().table("sessions").update({"status": status}).eq(
        "id", session_id
    ).execute()


def get_result(session_id: str) -> dict[str, Any] | None:
    response = (
        get_supabase_admin()
        .table("results")
        .select("*")
        .eq("session_id", session_id)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None


def save_result(session_id: str, result: dict[str, Any]) -> None:
    payload = {
        "session_id": session_id,
        "transcript": result.get("transcript"),
        "score_clarity": _clamp_score(result.get("score_clarity")),
        "score_confidence": _clamp_score(result.get("score_confidence")),
        "score_structure": _clamp_score(result.get("score_structure")),
        "score_relevance": _clamp_score(result.get("score_relevance")),
        "score_listening": _clamp_score(result.get("score_listening")),
        "score_global": _clamp_score(result.get("score_global")),
        "feedback_text": result.get("feedback_text"),
        "posture_notes": result.get("posture_notes"),
        "emotion_summary": result.get("emotion_summary") or {},
        "created_at": datetime.now(UTC).isoformat(),
    }
    get_supabase_admin().table("results").upsert(payload).execute()
    logger.info("Result saved: session_id=%s score=%s", session_id, payload["score_global"])


def _clamp_score(value: Any) -> int:
    try:
        score = int(value)
    except (TypeError, ValueError):
        score = 0
    return max(0, min(100, score))
