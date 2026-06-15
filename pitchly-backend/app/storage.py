from pathlib import PurePosixPath
from uuid import uuid4

from fastapi import UploadFile

from app.config import get_settings
from app.supabase_client import get_supabase_admin

ALLOWED_VIDEO_TYPES = {"video/webm", "video/mp4", "video/quicktime"}


def build_video_path(user_id: str, session_id: str, filename: str) -> str:
    suffix = PurePosixPath(filename or "recording.webm").suffix or ".webm"
    return f"{user_id}/{session_id}/{uuid4().hex}{suffix.lower()}"


async def upload_session_video(
    *,
    user_id: str,
    session_id: str,
    upload: UploadFile,
) -> dict[str, str]:
    if upload.content_type not in ALLOWED_VIDEO_TYPES:
        allowed = ", ".join(sorted(ALLOWED_VIDEO_TYPES))
        raise ValueError(f"Unsupported video type. Expected one of: {allowed}")

    settings = get_settings()
    path = build_video_path(user_id, session_id, upload.filename or "recording.webm")
    data = await upload.read()

    bucket = get_supabase_admin().storage.from_(settings.supabase_storage_bucket)
    bucket.upload(
        path,
        data,
        {
            "content-type": upload.content_type,
            "upsert": "false",
        },
    )
    signed = bucket.create_signed_url(path, 60 * 60)

    return {
        "bucket": settings.supabase_storage_bucket,
        "path": path,
        "signed_url": signed["signedURL"],
    }
