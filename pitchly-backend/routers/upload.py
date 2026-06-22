from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.auth import get_current_user
from app.storage import upload_session_video
from services.session_store import attach_video_url

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/{session_id}")
async def upload_video(
    session_id: str,
    video: UploadFile = File(...),
    user=Depends(get_current_user),
) -> dict[str, str]:
    # Responsibility: Upload authenticated session videos to Supabase Storage.
    try:
        stored = await upload_session_video(
            user_id=user.id,
            session_id=session_id,
            upload=video,
        )
        attach_video_url(session_id, stored["signed_url"])
        return stored
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
