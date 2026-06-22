from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from app.auth import get_current_user
from schemas.session import SessionCreate
from services.analysis_pipeline import run_analysis_pipeline
from services.session_store import create_job, create_session, get_job

router = APIRouter(prefix="/session", tags=["session"])


@router.post("/analyze")
async def analyze_session(
    payload: SessionCreate,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user),
) -> dict[str, str]:
    # Responsibility: Start a background analysis job for a configured session.
    session_id = create_session(user.id, payload)
    job_id = create_job(session_id)
    background_tasks.add_task(run_analysis_pipeline, job_id, session_id, payload.mode)
    return {"job_id": job_id, "session_id": session_id, "status": "processing"}


@router.get("/status/{job_id}")
async def get_session_status(
    job_id: str,
    user=Depends(get_current_user),
) -> dict[str, str | None]:
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, **job}
