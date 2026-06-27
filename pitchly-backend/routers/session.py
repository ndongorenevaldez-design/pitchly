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
    job_id = job_store.create_job(session_id, user.id)
    logger.info("Session reserved: session_id=%s job_id=%s", session_id, job_id)
    return SessionResponse(session_id=session_id, job_id=job_id, status="processing")


@router.post("/questions")
async def generate_questions(
    payload: dict,
    user=Depends(get_current_user),
) -> dict:
    """Generate context-specific questions using Gemini."""
    from services.ai_analysis import generate_interview_questions
    mode = payload.get("mode", "interview")
    job_title = payload.get("jobTitle")
    scenario = payload.get("scenario")
    try:
        questions = generate_interview_questions(mode, job_title, scenario)
        return {"questions": questions}
    except Exception as e:
        logger.warning("Question generation failed: %s", str(e))
        if mode == "interview":
            fallback = [
                "Tell me about yourself and why you're interested in this role.",
                "What are your greatest strengths and how do they apply to this position?",
                "Describe a challenging project you worked on and how you handled it.",
                "Where do you see yourself in five years?",
                "Do you have any questions for us?",
            ]
        else:
            fallback = [
                "How would you introduce yourself at a networking event?",
                "Can you tell me about a recent experience that made you happy?",
                "How do you typically start a conversation with someone new?",
                "What topics do you enjoy discussing with friends?",
                "How do you handle awkward silences in conversation?",
            ]
        return {"questions": fallback}


@router.get("/status/{job_id}")
async def get_session_status(
    job_id: str,
    user=Depends(get_current_user),
) -> dict[str, str | None]:
    job = job_store.get_job(job_id)

    if job:
        session = session_store.get_session_for_user(job.get("session_id") or "", user.id)
        if not session:
            raise HTTPException(status_code=404, detail="Job not found")
        return {"job_id": job_id, **job}

    session = session_store.find_processing_session_for_user(user.id)
    if session and session.get("status") == "complete":
        return {"job_id": job_id, "status": "complete", "session_id": session.get("id"), "error": None}
    if session and session.get("status") == "error":
        return {"job_id": job_id, "status": "error", "session_id": session.get("id"), "error": "Analysis failed"}

    raise HTTPException(status_code=404, detail="Job not found")
