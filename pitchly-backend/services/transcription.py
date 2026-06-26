# Responsibility: speech-to-text transcription using faster-whisper (local, no API cost)
# Uses faster-whisper==1.0.3 — NOT openai-whisper

import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_model = None  # loaded once, reused across requests


def _get_model():
    """Lazy-load the Whisper model on first use — avoids crash at startup."""
    global _model
    if _model is None:
        try:
            from faster_whisper import WhisperModel

            logger.info("Loading faster-whisper model: %s", settings.whisper_model)
            _model = WhisperModel(
                settings.whisper_model,
                device="cpu",
                compute_type="int8",  # int8 is fastest on CPU — critical for Railway
            )
            logger.info("faster-whisper model loaded successfully")
        except ImportError:
            logger.error("faster-whisper is not installed")
            raise
    return _model


def transcribe(audio_path: str) -> str:
    """
    Transcribe an audio file to text.
    Returns the full transcript as a single string.
    Raises on failure — caller handles error state.
    """
    model = _get_model()
    logger.info("Starting transcription: %s", audio_path)
    try:
        segments, info = model.transcribe(
            audio_path,
            beam_size=5,
            language=None,   # auto-detect: supports French and English
            vad_filter=True, # removes silence — faster and cleaner output
        )
        text = " ".join(segment.text.strip() for segment in segments)
        logger.info(
            "Transcription complete: language=%s duration=%.1fs chars=%d",
            info.language,
            info.duration,
            len(text),
        )
        return text
    except Exception as e:
        logger.error("Transcription failed: %s", str(e))
        raise