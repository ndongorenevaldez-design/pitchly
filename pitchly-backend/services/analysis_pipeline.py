# Responsibility: orchestrate the AI analysis pipeline after video upload

import logging
import os
import shutil
import tempfile

from services.ai_analysis import analyze as gemini_analyze
from services.job_store import mark_complete, mark_error, mark_processing
from services.scoring import compute_global_score
from services.session_store import get_session, save_result, update_session_status
from services.storage import download_video_to_file
from services.transcription import transcribe
from services.user_store import update_progress
from services.video_utils import extract_audio
from services.vision import analyze_emotions, analyze_posture

logger = logging.getLogger(__name__)


def _fallback_analysis(
    transcript: str,
    mode: str,
    posture_score: int,
    posture_notes: str,
    dominant_emotion: str,
    emotion_summary: dict,
) -> dict:
    """Generate sensible scores when Gemini is unavailable."""
    word_count = len(transcript.split())
    scores = {
        "score_clarity": min(100, 40 + word_count // 2),
        "score_confidence": min(100, max(30, posture_score)),
        "score_structure": min(100, 35 + word_count // 3),
        "score_relevance": 70 if mode == "interview" else 65,
        "score_listening": 60 if mode == "social" else 70,
    }
    return {
        **scores,
        "score_global": compute_global_score(scores),
        "feedback_text": (
            "Your session was processed successfully. "
            f"You spoke about {word_count} words. "
            "Focus on structuring your answer with a clear opening, one concrete example, "
            "and a confident closing statement."
        ),
        "posture_notes": posture_notes,
        "emotion_summary": emotion_summary,
        "dominant_emotion": dominant_emotion,
    }


def run_analysis_pipeline(job_id: str, session_id: str, storage_path: str) -> None:
    temp_dir = tempfile.mkdtemp(prefix="pitchly_")
    video_path = os.path.join(temp_dir, "recording.webm")
    audio_path = os.path.join(temp_dir, "audio.wav")

    try:
        mark_processing(job_id, session_id)
        session = get_session(session_id)
        if not session:
            raise RuntimeError("Session not found")

        user_id = session["user_id"]
        mode = session["mode"]
        job_title = session.get("job_title")
        scenario = session.get("scenario")

        logger.info("Pipeline started: job_id=%s session_id=%s", job_id, session_id)

        download_video_to_file(storage_path, video_path)
        extract_audio(video_path, audio_path)

        transcript = transcribe(audio_path).strip() or "No speech was detected in this recording."

        posture = analyze_posture(video_path)
        emotions = analyze_emotions(video_path)
        posture_score = posture["posture_score"]
        posture_notes = posture["notes"]
        dominant_emotion = emotions["dominant_emotion"]
        emotion_summary = emotions["emotion_summary"]

        try:
            ai_result = gemini_analyze(
                transcript=transcript,
                mode=mode,
                job_title=job_title,
                scenario=scenario,
                posture_score=posture_score,
                dominant_emotion=dominant_emotion,
            )
            if not ai_result.get("score_global"):
                ai_result["score_global"] = compute_global_score(ai_result)
            if not ai_result.get("posture_notes"):
                ai_result["posture_notes"] = posture_notes
        except Exception as gemini_exc:
            logger.warning("Gemini unavailable, using fallback: %s", str(gemini_exc))
            ai_result = _fallback_analysis(
                transcript,
                mode,
                posture_score,
                posture_notes,
                dominant_emotion,
                emotion_summary,
            )

        global_score = int(ai_result.get("score_global", 0))

        save_result(
            session_id,
            {
                "transcript": transcript,
                "score_clarity": ai_result.get("score_clarity"),
                "score_confidence": ai_result.get("score_confidence"),
                "score_structure": ai_result.get("score_structure"),
                "score_relevance": ai_result.get("score_relevance"),
                "score_listening": ai_result.get("score_listening"),
                "score_global": global_score,
                "feedback_text": ai_result.get("feedback_text"),
                "posture_notes": ai_result.get("posture_notes", posture_notes),
                "emotion_summary": emotion_summary,
            },
        )

        update_progress(user_id, mode, global_score)
        update_session_status(session_id, "complete")
        mark_complete(job_id, session_id)
        logger.info("Pipeline complete: job_id=%s session_id=%s", job_id, session_id)

    except Exception as exc:
        logger.exception("Pipeline failed: job_id=%s session_id=%s", job_id, session_id)
        update_session_status(session_id, "error")
        mark_error(job_id, session_id, str(exc))
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
