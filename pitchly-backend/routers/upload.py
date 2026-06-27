import logging

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile

from dependencies import get_current_user
from services import job_store, session_store
from services.analysis_pipeline import run_analysis_pipeline
from services.storage import upload_session_video

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/{session_id}")
async def upload_video(
    session_id: str,
    background_tasks: BackgroundTasks,
    video: UploadFile = File(...),
    user=Depends(get_current_user),
) -> dict[str, str]:
    """Upload video and queue the analysis pipeline."""
    if not session_store.get_session_for_user(session_id, user.id):
        raise HTTPException(status_code=404, detail="Session not found")

    job_id = job_store.get_job_id_for_session(session_id)
    if not job_id:
        raise HTTPException(status_code=400, detail="No analysis job found for this session")

    try:
        stored = await upload_session_video(
            user_id=user.id,
            session_id=session_id,
            upload=video,
        )
        session_store.update_processing_stage(session_id, "uploaded", 10)

        session_store.save_video_metadata(
            session_id=session_id,
            user_id=user.id,
            storage_path=stored["path"],
            signed_url=stored["signed_url"],
            filename=video.filename or "pitchly-session.webm",
            content_type=stored.get("content_type", "video/webm"),
            file_size=video.size or 0,
        )

        job_store.bind_storage_path(job_id, stored["path"])
        job_store.mark_processing(job_id, session_id)
        background_tasks.add_task(
            run_analysis_pipeline,
            job_id,
            session_id,
            stored["path"],
        )
        logger.info("Upload complete: session_id=%s job_id=%s", session_id, job_id)
        return {"job_id": job_id, **stored}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
