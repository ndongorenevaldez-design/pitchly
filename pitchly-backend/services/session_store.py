# Responsibility: Supabase sessions, results, and video tables

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
        "difficulty": getattr(payload, "difficulty", "balanced") or "balanced",
        "duration_s": payload.duration_s,
        "status": "processing",
        "processing_stage": "pending",
        "questions": getattr(payload, "questions", None) or [],
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


def find_processing_session_for_user(user_id: str) -> dict[str, Any] | None:
    response = (
        get_supabase_admin()
        .table("sessions")
        .select("*")
        .eq("user_id", user_id)
        .eq("status", "processing")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None


def update_session_status(session_id: str, status: str, error_message: str = None) -> None:
    update: dict[str, Any] = {"status": status}
    if status == "complete":
        update["completed_at"] = datetime.now(UTC).isoformat()
        update["processing_stage"] = "complete"
        update["completion_pct"] = 100
    elif status == "error":
        update["error_message"] = error_message[:1000] if error_message else None
        update["processing_stage"] = "error"
    get_supabase_admin().table("sessions").update(update).eq("id", session_id).execute()


def update_processing_stage(session_id: str, stage: str, pct: int) -> None:
    get_supabase_admin().table("sessions").update({
        "processing_stage": stage,
        "completion_pct": pct,
    }).eq("id", session_id).execute()


def save_video_metadata(session_id: str, user_id: str, storage_path: str,
                        signed_url: str, filename: str = "pitchly-session.webm",
                        content_type: str = "video/webm", file_size: int = 0) -> str:
    video_id = str(uuid4())
    get_supabase_admin().table("videos").insert({
        "id": video_id,
        "session_id": session_id,
        "user_id": user_id,
        "storage_path": storage_path,
        "signed_url": signed_url,
        "original_filename": filename,
        "content_type": content_type,
        "file_size_bytes": file_size,
    }).execute()
    return video_id


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
        "emotion_summary": _safe_json(result.get("emotion_summary")),
        "strengths": _safe_json(result.get("strengths")),
        "weaknesses": _safe_json(result.get("weaknesses")),
        "recommendations": _safe_json(result.get("recommendations")),
        "practice_exercises": _safe_json(result.get("practice_exercises")),
        "filler_words_detected": result.get("filler_words_detected", ""),
        "speech_pace": result.get("speech_pace", ""),
        "opening_quality": result.get("opening_quality", ""),
        "closing_quality": result.get("closing_quality", ""),
        "vocabulary_assessment": result.get("vocabulary_assessment", ""),
        "body_language": _safe_json(result.get("body_language")),
        "facial_expression": _safe_json(result.get("facial_expression")),
        "audio_quality": _safe_json(result.get("audio_quality")),
        "transcript_metadata": _safe_json(result.get("transcript_metadata")),
        "created_at": datetime.now(UTC).isoformat(),
    }
    get_supabase_admin().table("results").upsert(payload).execute()
    logger.info("Result saved: session_id=%s score=%s strengths=%d",
                session_id, payload["score_global"],
                len(result.get("strengths", [])))


def _clamp_score(value: Any) -> int:
    try:
        score = int(value)
    except (TypeError, ValueError):
        score = 0
    return max(0, min(100, score))


def _safe_json(value: Any) -> Any:
    if value is None:
        return {}
    if isinstance(value, (dict, list)):
        return value
    return str(value)
