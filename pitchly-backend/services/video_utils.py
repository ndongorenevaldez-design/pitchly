# Responsibility: Extract audio from video files using ffmpeg (required by faster-whisper)

import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_audio(video_path: str, audio_path: str) -> None:
    """
    Extract mono 16 kHz WAV audio from a video file.
    Raises RuntimeError if ffmpeg is missing or extraction fails.
    """
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is not installed or not on PATH")

    cmd = [
        "ffmpeg",
        "-i",
        video_path,
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        audio_path,
        "-y",
    ]
    logger.info("Extracting audio: video=%s", video_path)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("ffmpeg failed: %s", result.stderr[-500:])
        raise RuntimeError("Failed to extract audio from video")

    if not Path(audio_path).exists() or Path(audio_path).stat().st_size == 0:
        raise RuntimeError("Extracted audio file is empty")

    logger.info("Audio extracted: path=%s", audio_path)
