from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.auth import get_user_id_from_authorization
from app.config import get_settings
from app.storage import upload_session_video

settings = get_settings()

app = FastAPI(title="Pitchly API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "environment": settings.environment,
        "storage_bucket": settings.supabase_storage_bucket,
    }


@app.post("/sessions/{session_id}/video")
async def upload_video(
    session_id: str,
    video: UploadFile = File(...),
    authorization: str | None = Header(default=None),
) -> dict[str, str]:
    try:
        user_id = get_user_id_from_authorization(authorization)
        return await upload_session_video(
            user_id=user_id,
            session_id=session_id,
            upload=video,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
