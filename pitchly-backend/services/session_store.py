from __future__ import annotations

from datetime import UTC, datetime
from threading import Lock
from uuid import uuid4

from app.supabase_client import get_supabase_admin
from schemas.session import SessionCreate

_jobs: dict[str, dict[str, str | None]] = {}
_lock = Lock()


def create_session(user_id: str, payload: SessionCreate) -> str:
    # Responsibility: Persist session metadata in Supabase.
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
    return session_id


def create_job(session_id: str) -> str:
    job_id = str(uuid4())
    with _lock:
        _jobs[job_id] = {"status": "processing", "session_id": session_id, "error": None}
    return job_id


def get_job(job_id: str) -> dict[str, str | None] | None:
    with _lock:
        job = _jobs.get(job_id)
        return dict(job) if job else None


def mark_job_complete(job_id: str, session_id: str) -> None:
    with _lock:
        _jobs[job_id] = {"status": "complete", "session_id": session_id, "error": None}


def mark_job_error(job_id: str, session_id: str, error: str) -> None:
    with _lock:
        _jobs[job_id] = {"status": "error", "session_id": session_id, "error": error}


def attach_video_url(session_id: str, signed_url: str) -> None:
    get_supabase_admin().table("sessions").update({"video_url": signed_url}).eq(
        "id", session_id
    ).execute()


def update_session_status(session_id: str, status: str) -> None:
    get_supabase_admin().table("sessions").update({"status": status}).eq(
        "id", session_id
    ).execute()


def create_demo_result(session_id: str, mode: str) -> None:
    now = datetime.now(UTC).isoformat()
    result = {
        "session_id": session_id,
        "transcript": "Demo transcript generated for the local presentation flow.",
        "score_clarity": 82,
        "score_confidence": 76,
        "score_structure": 79,
        "score_relevance": 84,
        "score_listening": 72 if mode == "social" else 80,
        "score_global": 79,
        "feedback_text": "Strong opening and clear intent. Add one concrete example, slow down slightly on transitions, and close with a sharper summary.",
        "posture_notes": "Camera framing is stable. Keep shoulders relaxed and hold eye contact during key points.",
        "emotion_summary": {"dominant": "confident", "hesitations": "moderate"},
        "created_at": now,
    }
    get_supabase_admin().table("results").upsert(result).execute()
