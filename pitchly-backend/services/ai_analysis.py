# Responsibility: generate AI feedback using Gemini 2.5 Flash
# Acts as an expert communication coach, not just a summarizer

import json
import logging
import re

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
    posture_data: dict,
    emotion_data: dict,
    audio_quality: dict | None = None,
    transcript_meta: dict | None = None,
    questions: list[str] | None = None,
) -> str:
    """Build a comprehensive analysis prompt using ALL AI system outputs."""
    if audio_quality is None:
        audio_quality = {}
    if transcript_meta is None:
        transcript_meta = {}
    context = (
        f"Job title: {job_title}" if mode == "interview" and job_title
        else f"Scenario: {scenario}" if mode == "social" and scenario
        else "General communication practice"
    )

    posture_score = posture_data.get("posture_score", 50)
    gesture_freq = posture_data.get("gesture_frequency", 0)
    shoulder_stability = posture_data.get("shoulder_stability", 50)
    body_movement = posture_data.get("body_movement", 50)
    centered_score = posture_data.get("centered_score", 50)
    posture_notes = posture_data.get("notes", "")

    engagement_score = emotion_data.get("engagement_score", 50)
    emotion_confidence = emotion_data.get("confidence_score", 50)
    stress_level = emotion_data.get("stress_level", 30)
    smile_ratio = emotion_data.get("smile_ratio", 0)
    dominant_emotion = emotion_data.get("dominant_emotion", "neutral")
    emotion_dist = emotion_data.get("emotion_distribution", {})
    emotion_notes = emotion_data.get("notes", "")

    word_count = transcript_meta.get("raw_word_count", len(transcript.split()))
    duration_s = audio_quality.get("duration_s", 0) or transcript_meta.get("duration_s", 0)
    estimated_minutes = max(0.5, duration_s / 60) if duration_s > 0 else max(0.5, word_count / 150)

    wpm = transcript_meta.get("words_per_minute", 0)
    filler_count = transcript_meta.get("filler_count", 0)
    filler_pct = transcript_meta.get("filler_percentage", 0)
    pace_from_whisper = transcript_meta.get("pace_assessment", "unknown")

    vol_db = audio_quality.get("avg_volume_db", -25)
    vol_assess = audio_quality.get("volume_assessment", "unknown")
    silence_ratio = audio_quality.get("silence_ratio", 30)
    silence_assess = audio_quality.get("silence_assessment", "unknown")
    dynamic_range = audio_quality.get("dynamic_range_db", 15)

    truncated_transcript = transcript[:4000] if len(transcript) > 4000 else transcript

    return f"""You are an expert public speaking coach analyzing a {mode} training session.

IMPORTANT: Detect the language of the transcript and respond in THAT SAME LANGUAGE. If the transcript is in French, respond in French. If in Arabic, respond in Arabic. If in English, respond in English. All your feedback, strengths, weaknesses, recommendations, and exercises must be in the same language as the speaker.

CONTEXT:
{context}

{("QUESTIONS THAT WERE ASKED (evaluate how well the speaker answered each):") if questions else ""}
{chr(10).join(f"{i+1}. {q}" for i, q in enumerate(questions)) if questions else "No specific questions were assigned — evaluate the speech freely."}

TRANSCRIPT ({word_count} words, ~{estimated_minutes:.1f} minutes):
\"\"\"
{truncated_transcript}
\"\"\"

BODY LANGUAGE ANALYSIS (from computer vision):
- Posture visibility score: {posture_score}/100
- Shoulder stability: {shoulder_stability}/100
- Hand gesture frequency: {gesture_freq:.1f} gestures/minute
- Body movement level: {body_movement}/100
- Frame centering: {centered_score}/100
- Body language notes: {posture_notes}

FACIAL EXPRESSION ANALYSIS (from emotion AI):
- Facial engagement score: {engagement_score}/100
- Apparent confidence from face: {emotion_confidence}/100
- Stress indicators: {stress_level}/100
- Smile frequency: {smile_ratio}%
- Dominant emotion: {dominant_emotion}
- Emotion distribution: positive {emotion_dist.get('positive', 0)}%, neutral {emotion_dist.get('neutral', 0)}%, negative {emotion_dist.get('negative', 0)}%
- Facial expression notes: {emotion_notes}

AUDIO QUALITY ANALYSIS:
- Duration: {duration_s:.1f}s ({estimated_minutes:.1f} minutes)
- Volume: {vol_db:.1f} dB ({vol_assess})
- Silence ratio: {silence_ratio}% ({silence_assess})
- Dynamic range: {dynamic_range:.1f} dB
- Estimated words per minute: {wpm:.0f}
- Pace assessment: {pace_from_whisper}
- Filler words detected: {filler_count} ({filler_pct}%)

YOUR TASK:
Analyze the transcript content AND combine it with the body language, facial expression, and audio quality data above.
Evaluate the speaker as a professional communication coach would.

Provide a structured JSON response with exactly these fields:
{{
  "score_clarity": <integer 0-100, how clear and understandable the speech is>,
  "score_confidence": <integer 0-100, overall confidence combining words, body, and face>,
  "score_structure": <integer 0-100, organization, opening, closing, transitions>,
  "score_relevance": <integer 0-100, how relevant and focused the content is>,
  "score_listening": <integer 0-100, communication effectiveness and audience awareness>,
  "score_global": <integer 0-100, weighted overall score>,
  "feedback_text": "<3-4 paragraphs of detailed, personalized, actionable coaching feedback. Reference specific observations from the transcript AND the body language/face data. Be specific, not generic.>",
  "strengths": ["<specific strength 1 with evidence from transcript or body language>", "<specific strength 2>", "<specific strength 3>"],
  "weaknesses": ["<specific weakness 1 with evidence>", "<specific weakness 2>", "<specific weakness 3>"],
  "recommendations": ["<specific actionable recommendation 1>", "<specific actionable recommendation 2>", "<specific actionable recommendation 3>", "<specific actionable recommendation 4>"],
  "practice_exercises": ["<specific exercise 1: e.g., Record yourself again and focus on X>", "<specific exercise 2>", "<specific exercise 3>"],
  "filler_words_detected": "<list any filler words detected in transcript or 'None detected'>",
  "speech_pace": "<estimated pace assessment: too slow / optimal / too fast based on word count and duration>",
  "opening_quality": "<assessment of how the speaker started>",
  "closing_quality": "<assessment of how the speaker ended>",
  "vocabulary_assessment": "<assessment of word choice and variety>"
}}

Return ONLY valid JSON. No markdown, no backticks, no explanation outside the JSON.
The feedback_text should be specific and reference actual content from the transcript, not generic advice.""".strip()


def analyze(
    transcript: str,
    mode: str,
    job_title: str | None = None,
    scenario: str | None = None,
    posture_data: dict | None = None,
    emotion_data: dict | None = None,
    audio_quality: dict | None = None,
    transcript_meta: dict | None = None,
    questions: list[str] | None = None,
) -> dict:
    """
    Send transcript, body language data, emotion data, and audio quality to Gemini.
    Returns structured coaching analysis dict.
    """
    if posture_data is None:
        posture_data = {"posture_score": 50, "gesture_frequency": 0, "shoulder_stability": 50,
                        "body_movement": 50, "centered_score": 50, "notes": ""}
    if emotion_data is None:
        emotion_data = {"engagement_score": 50, "confidence_score": 50, "stress_level": 30,
                        "smile_ratio": 0, "dominant_emotion": "neutral", "emotion_distribution": {},
                        "notes": ""}
    if audio_quality is None:
        audio_quality = {}
    if transcript_meta is None:
        transcript_meta = {}

    prompt = _build_prompt(
        transcript, mode, job_title, scenario, posture_data, emotion_data,
        audio_quality, transcript_meta, questions,
    )
    logger.info("Sending to Gemini: transcript=%d chars posture_score=%d engagement=%d wpm=%.0f fillers=%d",
                len(transcript), posture_data.get("posture_score", 0),
                emotion_data.get("engagement_score", 0),
                transcript_meta.get("words_per_minute", 0),
                transcript_meta.get("filler_count", 0))

    try:
        response = _get_model().generate_content(prompt)
        raw = response.text.strip()

        import re
        json_match = re.search(r'\{[\s\S]*\}', raw)
        if json_match:
            raw = json_match.group(0)

        result = json.loads(raw)
        logger.info("Gemini analysis complete: global_score=%s strengths=%d weaknesses=%d",
                     result.get("score_global"),
                     len(result.get("strengths", [])),
                     len(result.get("weaknesses", [])))
        return result

    except json.JSONDecodeError as e:
        logger.error("Gemini returned invalid JSON, attempting recovery: %s", str(e))
        try:
            import re
            cleaned = re.sub(r'[\x00-\x1f]', ' ', raw)
            cleaned = re.sub(r',\s*}', '}', cleaned)
            cleaned = re.sub(r',\s*]', ']', cleaned)
            result = json.loads(cleaned)
            return result
        except Exception:
            raise ValueError("AI analysis returned malformed response") from e
    except Exception as e:
        logger.error("Gemini API call failed: %s", str(e))
        raise


def generate_interview_questions(
    mode: str,
    job_title: str | None = None,
    scenario: str | None = None,
) -> list[str]:
    """Generate 5 context-specific questions using Gemini, in the language of the context."""
    if mode == "interview" and job_title:
        context = f"for a {job_title} position"
    elif mode == "social" and scenario:
        context = f"for a social scenario: {scenario}"
    else:
        context = "for general communication practice"

    prompt = f"""Generate 5 specific, realistic interview or conversation questions {context}.
The questions should be the kind of questions that require thoughtful, detailed answers.

IMPORTANT: Detect the language used in the context. If the job title or scenario is written in French, Arabic, Spanish, or any other language, generate the questions in THAT SAME LANGUAGE. If the context is in English, generate in English. Match the language of the input.

Return ONLY a JSON array of 5 strings. No markdown, no explanation.
Example format: ["Question 1?", "Question 2?", "Question 3?", "Question 4?", "Question 5?"]
"""
    try:
        response = _get_model().generate_content(prompt)
        raw = response.text.strip()
        import re
        json_match = re.search(r'\[[\s\S]*\]', raw)
        if json_match:
            raw = json_match.group(0)
        questions = json.loads(raw)
        if isinstance(questions, list) and len(questions) >= 3:
            return [str(q) for q in questions[:5]]
    except Exception as e:
        logger.warning("Gemini question generation failed: %s", str(e))

    if mode == "interview":
        return [
            f"Tell me about your background and why you're interested in this {job_title or 'role'}.",
            "What are your greatest strengths and how do they apply to this position?",
            "Describe a challenging situation at work and how you handled it.",
            "Where do you see yourself in the next few years?",
            "Do you have any questions for us?",
        ]
    return [
        "How would you introduce yourself at a social gathering?",
        "Can you tell me about something interesting that happened to you recently?",
        "How do you usually start conversations with new people?",
        "What topics are you most passionate about discussing?",
        "How do you handle situations where you don't know what to say?",
    ]
