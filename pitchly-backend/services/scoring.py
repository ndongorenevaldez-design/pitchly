# Responsibility: compute final scores and update user aggregate statistics

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def compute_global_score(scores: dict) -> int:
    """
    Compute weighted global score from 5 category scores.
    Weights reflect the importance of each dimension in communication.
    """
    weights = {
        "score_clarity":    0.25,
        "score_confidence": 0.25,
        "score_structure":  0.20,
        "score_relevance":  0.20,
        "score_listening":  0.10,
    }
    total = sum(
        scores.get(key, 0) * weight
        for key, weight in weights.items()
    )
    return int(round(total))


def update_user_progress(user_id: str, mode: str, global_score: int, db_client) -> None:
    """
    Update the user's aggregate statistics after a completed session.
    Extraversion score grows logarithmically in Social Mode — caps at 100.
    """
    try:
        # Fetch current user stats
        response = db_client.table("users") \
            .select("total_sessions, interview_sessions, social_sessions, "
                    "avg_global_score, extraversion_score") \
            .eq("id", user_id) \
            .single() \
            .execute()

        user = response.data
        total = user["total_sessions"] + 1
        interview_count = user["interview_sessions"] + (1 if mode == "interview" else 0)
        social_count = user["social_sessions"] + (1 if mode == "social" else 0)

        # Rolling average
        old_avg = user["avg_global_score"] or 0
        new_avg = round(((old_avg * (total - 1)) + global_score) / total, 2)

        # Extraversion score — only grows in Social Mode
        extraversion = user["extraversion_score"] or 0
        if mode == "social":
            delta = max(1, (global_score - 50) // 10)
            extraversion = min(100, extraversion + delta)

        db_client.table("users").update({
            "total_sessions":    total,
            "interview_sessions": interview_count,
            "social_sessions":   social_count,
            "avg_global_score":  new_avg,
            "extraversion_score": extraversion,
            "last_session_at":   datetime.now(timezone.utc).isoformat(),
        }).eq("id", user_id).execute()

        logger.info(
            "User progress updated: user=%s total=%d avg=%.1f extraversion=%d",
            user_id, total, new_avg, extraversion,
        )

    except Exception as e:
        logger.error("Failed to update user progress: user=%s error=%s", user_id, str(e))
        # Non-fatal — session result is already saved
        