import logging

from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_current_user
from services import session_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/results", tags=["results"])


@router.get("/{session_id}")
async def get_results(session_id: str, user=Depends(get_current_user)):
    session = session_store.get_session_for_user(session_id, user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    result = session_store.get_result(session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Results not ready")

    return {
        "session": {
            "id": session.get("id"),
            "mode": session.get("mode"),
            "job_title": session.get("job_title"),
            "scenario": session.get("scenario"),
            "status": session.get("status"),
            "created_at": session.get("created_at"),
        },
        "result": {
            "transcript": result.get("transcript"),
            "score_clarity": result.get("score_clarity"),
            "score_confidence": result.get("score_confidence"),
            "score_structure": result.get("score_structure"),
            "score_relevance": result.get("score_relevance"),
            "score_listening": result.get("score_listening"),
            "score_global": result.get("score_global"),
            "feedback_text": result.get("feedback_text"),
            "posture_notes": result.get("posture_notes"),
            "emotion_summary": result.get("emotion_summary"),
            "strengths": result.get("strengths") or [],
            "weaknesses": result.get("weaknesses") or [],
            "recommendations": result.get("recommendations") or [],
            "practice_exercises": result.get("practice_exercises") or [],
            "filler_words_detected": result.get("filler_words_detected", ""),
            "speech_pace": result.get("speech_pace", ""),
            "opening_quality": result.get("opening_quality", ""),
            "closing_quality": result.get("closing_quality", ""),
            "vocabulary_assessment": result.get("vocabulary_assessment", ""),
            "body_language": result.get("body_language") or {},
            "facial_expression": result.get("facial_expression") or {},
            "audio_quality": result.get("audio_quality") or {},
            "transcript_metadata": result.get("transcript_metadata") or {},
            "created_at": result.get("created_at"),
        },
    }
