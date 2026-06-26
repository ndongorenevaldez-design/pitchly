# Responsibility: generate AI feedback using Gemini 2.5 Flash
# Free tier: 1500 requests/day — no cost for thesis demo

import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_model = None


def _get_model():
    """Lazy-load Gemini model so missing API keys do not crash app startup."""
    global _model
    if _model is None:
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")

        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        _model = genai.GenerativeModel(settings.gemini_model)
        logger.info("Gemini model configured: model=%s", settings.gemini_model)
    return _model


def _build_prompt(
    transcript: str,
    mode: str,
    job_title: str | None,
    scenario: str | None,
    posture_score: int,
    dominant_emotion: str,
) -> str:
    """Build the analysis prompt sent to Gemini."""
    context = (
        f"Job title: {job_title}" if mode == "interview" and job_title
        else f"Scenario: {scenario}" if mode == "social" and scenario
        else "General communication practice"
    )
    return f"""
You are an expert communication coach analyzing a {mode} training session.

Context: {context}
Posture score (0-100): {posture_score}
Dominant facial emotion detected: {dominant_emotion}

User's transcript:
\"\"\"
{transcript}
\"\"\"

Provide a structured JSON response with exactly these fields:
{{
  "score_clarity": <integer 0-100>,
  "score_confidence": <integer 0-100>,
  "score_structure": <integer 0-100>,
  "score_relevance": <integer 0-100>,
  "score_listening": <integer 0-100>,
  "score_global": <integer 0-100>,
  "feedback_text": "<2-3 paragraphs of detailed, actionable feedback>",
  "posture_notes": "<one sentence about posture based on posture_score>",
  "top_strengths": ["<strength 1>", "<strength 2>"],
  "areas_to_improve": ["<area 1>", "<area 2>", "<area 3>"]
}}

Return ONLY valid JSON. No markdown, no backticks, no explanation outside the JSON.
""".strip()


def analyze(
    transcript: str,
    mode: str,
    job_title: str | None = None,
    scenario: str | None = None,
    posture_score: int = 50,
    dominant_emotion: str = "neutral",
) -> dict:
    """
    Send transcript and session context to Gemini.
    Returns structured analysis dict.
    Raises on API failure — caller handles error state.
    """
    import json

    prompt = _build_prompt(
        transcript, mode, job_title, scenario, posture_score, dominant_emotion
    )
    logger.info("Sending transcript to Gemini: chars=%d mode=%s", len(transcript), mode)

    try:
        response = _get_model().generate_content(prompt)
        raw = response.text.strip()

        # Strip markdown code fences if Gemini wraps the JSON
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        result = json.loads(raw)
        logger.info("Gemini analysis complete: global_score=%s", result.get("score_global"))
        return result

    except json.JSONDecodeError as e:
        logger.error("Gemini returned invalid JSON: %s", str(e))
        raise ValueError("AI analysis returned malformed response") from e
    except Exception as e:
        logger.error("Gemini API call failed: %s", str(e))
        raise
