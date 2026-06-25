# Responsibility: upload and retrieve video files via Supabase Storage
# Uses Supabase service role client — no AWS or R2 dependency
# Note: the primary upload logic lives in app/storage.py (with UploadFile support).
# This module provides simpler convenience functions for raw bytes upload/delete.

import logging

from app.config import get_settings
from app.supabase_client import get_supabase_admin

logger = logging.getLogger(__name__)

settings = get_settings()
BUCKET = settings.supabase_storage_bucket


def upload_video(file_bytes: bytes, filename: str) -> str:
    """
    Upload a video file to Supabase Storage.
    Returns a presigned URL valid for 1 hour.
    Raises on failure — caller handles error state.
    """
    path = f"sessions/{filename}"
    try:
        get_supabase_admin().storage.from_(BUCKET).upload(
            path,
            file_bytes,
            {"content-type": "video/webm"},
        )
        result = get_supabase_admin().storage.from_(BUCKET).create_signed_url(
            path,
            settings.signed_url_ttl_s,
        )
        logger.info("Video uploaded to Supabase Storage: path=%s", path)
        return result["signedURL"]
    except Exception as e:
        logger.error("Supabase Storage upload failed: path=%s error=%s", path, str(e))
        raise


def delete_video(filename: str) -> None:
    """
    Delete a video from Supabase Storage.
    Called when AI processing fails — cleans up orphan files.
    """
    path = f"sessions/{filename}"
    try:
        get_supabase_admin().storage.from_(BUCKET).remove([path])
        logger.info("Video deleted from Supabase Storage: path=%s", path)
    except Exception as e:
        logger.error("Supabase Storage delete failed: path=%s error=%s", path, str(e))
