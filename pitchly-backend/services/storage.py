# Responsibility: upload and download video files via Supabase Storage only

import logging
from pathlib import PurePosixPath
from uuid import uuid4

from fastapi import UploadFile

from app.config import get_settings
from app.supabase_client import get_supabase_admin

logger = logging.getLogger(__name__)


def _resolve_content_type(upload: UploadFile) -> str:
    content_type = upload.content_type or ""
    filename = (upload.filename or "").lower()
    if content_type in {"video/webm", "video/mp4", "video/quicktime"}:
        return content_type
    if filename.endswith(".webm"):
        return "video/webm"
    if filename.endswith(".mp4"):
        return "video/mp4"
    if filename.endswith(".mov"):
        return "video/quicktime"
    raise ValueError("Unsupported video type. Upload a .webm, .mp4, or .mov recording.")


def _build_path(user_id: str, session_id: str, filename: str) -> str:
    suffix = PurePosixPath(filename or "recording.webm").suffix or ".webm"
    return f"{user_id}/{session_id}/{uuid4().hex}{suffix.lower()}"


async def upload_session_video(
    *,
    user_id: str,
    session_id: str,
    upload: UploadFile,
) -> dict[str, str]:
    settings = get_settings()
    content_type = _resolve_content_type(upload)
    path = _build_path(user_id, session_id, upload.filename or "recording.webm")
    data = await upload.read()

    if not data:
        raise ValueError("Uploaded video file is empty")
    if len(data) > settings.max_upload_size_bytes:
        raise ValueError("Video exceeds the upload size limit")

    bucket = get_supabase_admin().storage.from_(settings.supabase_storage_bucket)
    bucket.upload(path, data, {"content-type": content_type, "upsert": "false"})
    signed = bucket.create_signed_url(path, settings.signed_url_ttl_s)
    logger.info("Video uploaded: session_id=%s path=%s", session_id, path)

    return {
        "bucket": settings.supabase_storage_bucket,
        "path": path,
        "signed_url": signed["signedURL"],
    }


def download_video_to_file(storage_path: str, dest_path: str) -> None:
    settings = get_settings()
    data = (
        get_supabase_admin()
        .storage.from_(settings.supabase_storage_bucket)
        .download(storage_path)
    )
    if not data:
        raise RuntimeError("Downloaded video data is empty")

    with open(dest_path, "wb") as handle:
        handle.write(data)
    logger.info("Video downloaded: path=%s bytes=%d", storage_path, len(data))
