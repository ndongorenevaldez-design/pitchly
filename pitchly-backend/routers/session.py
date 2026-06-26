import logging

from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_current_user
from schemas.session import SessionCreate, SessionResponse
from services import job_store, session_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/session", tags=["session"])


@router.post("/analyze", response_model=SessionResponse)
async def analyze_session(
    payload: SessionCreate,
    user=Depends(get_current_user),
) -> SessionResponse:
    """Create a session and reserve a job. Analysis starts after video upload."""
    session_id = session_store.create_session(user.id, payload)
    job_id = job_store.create_job(session_id)
    logger.info("Session reserved: session_id=%s job_id=%s", session_id, job_id)
    return SessionResponse(session_id=session_id, job_id=job_id, status="processing")


@router.get("/status/{job_id}")
async def get_session_status(
    job_id: str,
    user=Depends(get_current_user),
) -> dict[str, str | None]:
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    session = session_store.get_session_for_user(job.get("session_id") or "", user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Job not found")

    return {"job_id": job_id, **job}
