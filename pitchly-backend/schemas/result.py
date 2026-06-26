# Responsibility: Pydantic schemas for session results

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ResultResponse(BaseModel):
    """Full result returned to the frontend after AI analysis."""

    session_id: str
    transcript: str | None = None
    score_clarity: int | None = None
    score_confidence: int | None = None
    score_structure: int | None = None
    score_relevance: int | None = None
    score_listening: int | None = None
    score_global: int | None = None
    feedback_text: str | None = None
    posture_notes: str | None = None
    emotion_summary: dict[str, Any] | None = None
    created_at: str | None = None