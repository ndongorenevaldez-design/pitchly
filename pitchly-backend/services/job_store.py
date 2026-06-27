# Responsibility: analysis job tracking via database
# Survives server restarts — replaces in-memory dict

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from app.supabase_client import get_supabase_admin

logger = logging.getLogger(__name__)


def create_job(session_id: str, user_id: str) -> str:
    job_id = str(uuid4())
    get_supabase_admin().table("analysis_jobs").insert({
        "id": job_id,
        "session_id": session_id,
        "user_id": user_id,
        "status": "pending_upload",
    }).execute()
    logger.info("Job created: job_id=%s session_id=%s", job_id, session_id)
    return job_id


def get_job(job_id: str) -> dict[str, Any] | None:
    response = (
        get_supabase_admin()
        .table("analysis_jobs")
        .select("*")
        .eq("id", job_id)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None


def get_job_id_for_session(session_id: str) -> str | None:
    response = (
        get_supabase_admin()
        .table("analysis_jobs")
        .select("id")
        .eq("session_id", session_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    rows = response.data or []
    return rows[0]["id"] if rows else None


def bind_storage_path(job_id: str, storage_path: str) -> None:
    get_supabase_admin().table("analysis_jobs").update(
        {"storage_path": storage_path}
    ).eq("id", job_id).execute()


def mark_processing(job_id: str, session_id: str) -> None:
    get_supabase_admin().table("analysis_jobs").update({
        "status": "processing",
        "started_at": datetime.now(UTC).isoformat(),
    }).eq("id", job_id).execute()


def mark_complete(job_id: str, session_id: str) -> None:
    now = datetime.now(UTC).isoformat()
    job = get_job(job_id)
    duration_ms = None
    if job and job.get("started_at"):
        try:
            started = datetime.fromisoformat(job["started_at"].replace("Z", "+00:00"))
            duration_ms = int((datetime.now(UTC) - started).total_seconds() * 1000)
        except Exception:
            pass

    get_supabase_admin().table("analysis_jobs").update({
        "status": "complete",
        "completed_at": now,
        "duration_ms": duration_ms,
    }).eq("id", job_id).execute()
    logger.info("Job complete: job_id=%s duration_ms=%s", job_id, duration_ms)


def mark_error(job_id: str, session_id: str, error: str) -> None:
    get_supabase_admin().table("analysis_jobs").update({
        "status": "error",
        "error_message": error[:2000],
        "completed_at": datetime.now(UTC).isoformat(),
    }).eq("id", job_id).execute()
    logger.error("Job failed: job_id=%s error=%s", job_id, error[:200])
