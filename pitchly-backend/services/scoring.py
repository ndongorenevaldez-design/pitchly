# Responsibility: weighted score computation only (pure functions, no I/O)

import logging

logger = logging.getLogger(__name__)

_WEIGHTS = {
    "score_clarity": 0.25,
    "score_confidence": 0.25,
    "score_structure": 0.20,
    "score_relevance": 0.20,
    "score_listening": 0.10,
}


def compute_global_score(scores: dict) -> int:
    """Compute weighted global score from five category scores."""
    total = sum(scores.get(key, 0) * weight for key, weight in _WEIGHTS.items())
    return int(round(total))
