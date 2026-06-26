# Responsibility: in-memory analysis job tracking (no database, no HTTP)

from __future__ import annotations

from threading import Lock
from uuid import uuid4

_lock = Lock()
_jobs: dict[str, dict[str, str | None]] = {}
_session_to_job: dict[str, str] = {}


def create_job(session_id: str) -> str:
    job_id = str(uuid4())
    with _lock:
        _jobs[job_id] = {
            "status": "pending_upload",
            "session_id": session_id,
            "storage_path": None,
            "error": None,
        }
        _session_to_job[session_id] = job_id
    return job_id


def get_job(job_id: str) -> dict[str, str | None] | None:
    with _lock:
        job = _jobs.get(job_id)
        return dict(job) if job else None


def get_job_id_for_session(session_id: str) -> str | None:
    with _lock:
        return _session_to_job.get(session_id)


def bind_storage_path(job_id: str, storage_path: str) -> None:
    with _lock:
        if job_id in _jobs:
            _jobs[job_id]["storage_path"] = storage_path


def mark_processing(job_id: str, session_id: str) -> None:
    with _lock:
        _jobs[job_id] = {
            "status": "processing",
            "session_id": session_id,
            "storage_path": _jobs.get(job_id, {}).get("storage_path"),
            "error": None,
        }


def mark_complete(job_id: str, session_id: str) -> None:
    with _lock:
        _jobs[job_id] = {
            "status": "complete",
            "session_id": session_id,
            "storage_path": _jobs.get(job_id, {}).get("storage_path"),
            "error": None,
        }


def mark_error(job_id: str, session_id: str, error: str) -> None:
    with _lock:
        _jobs[job_id] = {
            "status": "error",
            "session_id": session_id,
            "storage_path": _jobs.get(job_id, {}).get("storage_path"),
            "error": error,
        }
