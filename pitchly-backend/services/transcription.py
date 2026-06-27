# Responsibility: speech-to-text transcription and transcript cleaning
# Uses faster-whisper==1.0.3 — NOT openai-whisper

import logging
import re

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_model = None

FILLER_WORDS = {
    "um", "uh", "er", "ah", "like", "you know", "so", "basically",
    "actually", "literally", "i mean", "kind of", "sort of",
    "right", "okay", "well", "hmm", "huh",
}


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
                compute_type="int8",
            )
            logger.info("faster-whisper model loaded successfully")
        except ImportError:
            logger.error("faster-whisper is not installed")
            raise
    return _model


def transcribe(audio_path: str) -> tuple[str, dict]:
    """
    Transcribe an audio file to text.
    Returns (cleaned_transcript, metadata) where metadata contains
    word count, filler count, and estimated pace.
    """
    model = _get_model()
    logger.info("Starting transcription: %s", audio_path)
    try:
        segments, info = model.transcribe(
            audio_path,
            beam_size=5,
            language=None,
            vad_filter=True,
        )
        raw_text = " ".join(segment.text.strip() for segment in segments)

        word_count = len(raw_text.split())
        duration_s = info.duration if info.duration else 0
        wpm = (word_count / max(duration_s, 1)) * 60

        filler_count = 0
        lower_text = raw_text.lower()
        for filler in FILLER_WORDS:
            filler_count += len(re.findall(r'\b' + re.escape(filler) + r'\b', lower_text))

        cleaned = raw_text
        for filler in FILLER_WORDS:
            cleaned = re.sub(r'\b' + re.escape(filler) + r'\b', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s{2,}', ' ', cleaned).strip()

        pace = "optimal"
        if wpm < 120:
            pace = "too slow"
        elif wpm > 180:
            pace = "too fast"
        elif wpm < 140:
            pace = "slightly slow"
        elif wpm > 160:
            pace = "slightly fast"

        metadata = {
            "language": info.language,
            "duration_s": round(duration_s, 1),
            "raw_word_count": word_count,
            "cleaned_word_count": len(cleaned.split()),
            "filler_count": filler_count,
            "words_per_minute": round(wpm, 1),
            "pace_assessment": pace,
            "filler_percentage": round(filler_count / max(word_count, 1) * 100, 1),
        }

        filler_report = "None detected" if filler_count == 0 else f"{filler_count} filler words ({metadata['filler_percentage']}%)"
        logger.info(
            "Transcription complete: lang=%s dur=%.1fs words=%d fillers=%d wpm=%.0f pace=%s",
            info.language, duration_s, word_count, filler_count, wpm, pace,
        )
        return cleaned, metadata

    except Exception as e:
        logger.error("Transcription failed: %s", str(e))
        raise