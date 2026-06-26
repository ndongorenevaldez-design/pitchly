# Responsibility: upload and retrieve video files via Supabase Storage
# No AWS, no Cloudflare R2 — Supabase handles everything

import logging

from supabase import create_client

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_supabase = create_client(
    settings.supabase_url,
    settings.supabase_service_role_key,  # service role bypasses RLS for backend ops
)

BUCKET = settings.supabase_storage_bucket  # "pitchly-videos" from .env


def upload_video(file_bytes: bytes, filename: str) -> str:
    """
    Upload a video file to Supabase Storage.
    Returns a signed URL valid for signed_url_ttl_s seconds (default 1 hour).
    Raises on failure — caller is responsible for error handling.
    """
    path = f"sessions/{filename}"
    try:
        _supabase.storage.from_(BUCKET).upload(
            path,
            file_bytes,
            {"content-type": "video/webm"},
        )
        result = _supabase.storage.from_(BUCKET).create_signed_url(
            path,
            settings.signed_url_ttl_s,
        )
        logger.info("Video uploaded to Supabase Storage: path=%s", path)
        return result["signedURL"]
    except Exception as e:
        logger.error("Storage upload failed: path=%s error=%s", path, str(e))
        raise


def delete_video(filename: str) -> None:
    """
    Delete a video from Supabase Storage.
    Called when AI processing fails — removes orphaned files.
    """
    path = f"sessions/{filename}"
    try:
        _supabase.storage.from_(BUCKET).remove([path])
        logger.info("Video deleted from Supabase Storage: path=%s", path)
    except Exception as e:
        logger.error("Storage delete failed: path=%s error=%s", path, str(e))