# Responsibility: orchestrate the AI analysis pipeline after video upload
# Connects Whisper → Gemini → DeepFace → MediaPipe into one coherent coaching report

import logging
import os
import shutil
import tempfile

from services.ai_analysis import analyze as gemini_analyze
from services.job_store import mark_complete, mark_error, mark_processing
from services.scoring import compute_global_score
from services.session_store import get_session, save_result, update_processing_stage, update_session_status
from services.storage import download_video_to_file
from services.transcription import transcribe
from services.video_utils import analyze_audio_quality, extract_audio
from services.vision import analyze_emotions, analyze_posture, _default_posture, _default_emotions

logger = logging.getLogger(__name__)


def _fallback_analysis(
    transcript: str,
    mode: str,
    posture_data: dict,
    emotion_data: dict,
    audio_quality: dict,
    transcript_meta: dict,
) -> dict:
    """Generate meaningful scores when Gemini is unavailable, using all available data."""
    word_count = transcript_meta.get("raw_word_count", len(transcript.split()))
    posture_score = posture_data.get("posture_score", 50)
    engagement = emotion_data.get("engagement_score", 50)
    confidence_face = emotion_data.get("confidence_score", 50)
    stress = emotion_data.get("stress_level", 30)
    gesture_freq = posture_data.get("gesture_frequency", 0)
    wpm = transcript_meta.get("words_per_minute", 0)
    filler_pct = transcript_meta.get("filler_percentage", 0)
    vol_db = audio_quality.get("avg_volume_db", -25)
    silence_ratio = audio_quality.get("silence_ratio", 30)

    clarity_base = 50
    if 130 <= wpm <= 170:
        clarity_base += 15
    elif wpm < 100 or wpm > 200:
        clarity_base -= 10
    if filler_pct < 3:
        clarity_base += 10
    elif filler_pct > 10:
        clarity_base -= 15
    if -30 <= vol_db <= -15:
        clarity_base += 10
    clarity = min(100, max(0, clarity_base))

    confidence = min(100, max(0, int(
        (posture_score * 0.3 + confidence_face * 0.3 + (100 - stress) * 0.2 + engagement * 0.2)
    )))

    structure_base = 40
    if word_count > 50:
        structure_base += 10
    if word_count > 150:
        structure_base += 10
    if silence_ratio > 20 and silence_ratio < 50:
        structure_base += 10
    structure = min(100, structure_base)

    relevance = 70 if mode == "interview" else 65
    listening = min(100, max(40, engagement))

    scores = {
        "score_clarity": clarity,
        "score_confidence": confidence,
        "score_structure": structure,
        "score_relevance": relevance,
        "score_listening": listening,
    }

    feedback_parts = [
        f"You spoke {word_count} words over approximately {word_count / max(wpm, 1):.1f} minutes.",
    ]

    if wpm > 0:
        if wpm < 120:
            feedback_parts.append("Your speaking pace is slower than average. Try to speak a bit more briskly to maintain audience engagement.")
        elif wpm > 180:
            feedback_parts.append("You're speaking quite fast. Slow down slightly to ensure clarity and allow your audience to process your points.")
        else:
            feedback_parts.append(f"Your pace of {wpm:.0f} words per minute is in a good range.")

    if filler_pct > 5:
        feedback_parts.append(f"Filler words made up {filler_pct:.1f}% of your speech. Practice pausing instead of using fillers like 'um' or 'like'.")
    elif filler_count > 0:
        feedback_parts.append("Very few filler words detected — good verbal discipline.")

    if posture_score < 60:
        feedback_parts.append(f"Posture needs work (score: {posture_score}/100). Stay centered in frame and keep shoulders level.")
    elif posture_score >= 80:
        feedback_parts.append("Strong body posture maintained throughout the session.")

    if engagement < 50:
        feedback_parts.append("Facial engagement was low. Try to show more expression and vary your facial reactions to match your content.")
    elif engagement >= 70:
        feedback_parts.append("Good facial engagement — your expressions supported your message.")

    if stress > 60:
        feedback_parts.append("Elevated stress was detected. Take deep breaths before starting and focus on your breathing during pauses.")

    strengths = []
    if posture_score >= 70:
        strengths.append("Maintained strong body posture and visibility")
    if engagement >= 60:
        strengths.append("Showed good facial engagement with the camera")
    if filler_pct < 5:
        strengths.append("Clean speech with minimal filler words")
    if 130 <= wpm <= 170:
        strengths.append("Speaking pace was in an optimal range")
    if confidence_face >= 60:
        strengths.append("Projected confidence through facial expressions")
    if not strengths:
        strengths = ["Completed the recording session", "Maintained presence on camera"]

    weaknesses = []
    if posture_score < 60:
        weaknesses.append("Body positioning and posture need improvement")
    if engagement < 50:
        weaknesses.append("Facial expressiveness was limited")
    if filler_pct > 8:
        weaknesses.append(f"High filler word usage ({filler_pct:.1f}%)")
    if wpm < 110 or wpm > 190:
        weaknesses.append("Speaking pace was outside the optimal range")
    if stress > 60:
        weaknesses.append("Visible stress indicators during the session")
    if not weaknesses:
        weaknesses = ["Continue practicing to refine your delivery"]

    recommendations = []
    if posture_score < 70:
        recommendations.append("Practice standing or sitting upright with shoulders level. Position yourself centered in the camera frame.")
    if engagement < 60:
        recommendations.append("Work on varying your facial expressions to match your message. Smile naturally at appropriate moments.")
    if filler_pct > 5:
        recommendations.append("Record yourself and count filler words. Practice pausing silently instead of using 'um' or 'like'.")
    if wpm < 120 or wpm > 180:
        recommendations.append("Use a metronome or practice with a timer to develop a more consistent speaking pace.")
    if stress > 50:
        recommendations.append("Practice deep breathing exercises before recording. Start with shorter sessions to build comfort.")
    recommendations.append("Record yourself daily for 2-3 minutes on a random topic and review the recording.")
    if not recommendations:
        recommendations = [
            "Practice the STAR method for structured responses",
            "Record yourself and review for areas of improvement",
            "Focus on maintaining good posture and eye contact",
        ]

    exercises = [
        "Record a 2-minute elevator pitch about your current project. Time yourself and aim for 140-160 words per minute.",
        "Practice the 4-second pause technique: after making a key point, pause for 4 seconds before continuing.",
        "Record the same presentation twice — once standing, once sitting — and compare your body language.",
        "Practice in front of a mirror to monitor your facial expressions while speaking.",
    ]

    return {
        **scores,
        "score_global": compute_global_score(scores),
        "feedback_text": " ".join(feedback_parts),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations,
        "practice_exercises": exercises,
        "filler_words_detected": f"{transcript_meta.get('filler_count', 0)} filler words ({filler_pct}%)" if transcript_meta.get('filler_count', 0) > 0 else "None detected",
        "speech_pace": f"{wpm:.0f} words per minute — {transcript_meta.get('pace_assessment', 'unknown')}",
        "opening_quality": "Analysis requires Gemini AI",
        "closing_quality": "Analysis requires Gemini AI",
        "vocabulary_assessment": "Analysis requires Gemini AI",
    }
    return {
        **scores,
        "score_global": compute_global_score(scores),
        "feedback_text": (
            "Your session was processed successfully. "
            f"You spoke about {word_count} words. "
            f"Body language analysis: {posture_data.get('notes', 'N/A')}. "
            f"Emotional engagement: {emotion_data.get('notes', 'N/A')}. "
            "Focus on structuring your answer with a clear opening, one concrete example, "
            "and a confident closing statement."
        ),
        "strengths": ["Completed the recording session", "Maintained presence on camera"],
        "weaknesses": ["Could not perform detailed AI analysis — Gemini was unavailable"],
        "recommendations": [
            "Practice structuring your speech with a clear opening, body, and closing",
            "Record yourself and review for filler words",
            "Maintain good posture and eye contact with the camera",
        ],
        "practice_exercises": [
            "Record a 2-minute pitch about your current project and time yourself",
            "Practice the STAR method for interview questions",
        ],
        "filler_words_detected": "Analysis unavailable",
        "speech_pace": "Analysis unavailable",
        "opening_quality": "Analysis unavailable",
        "closing_quality": "Analysis unavailable",
        "vocabulary_assessment": "Analysis unavailable",
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
        questions = session.get("questions") or []

        logger.info("Pipeline started: job_id=%s session_id=%s", job_id, session_id)

        update_processing_stage(session_id, "extracting_audio", 15)
        download_video_to_file(storage_path, video_path)
        extract_audio(video_path, audio_path)

        update_processing_stage(session_id, "transcribing", 25)
        transcript, transcript_meta = transcribe(audio_path)
        if not transcript.strip():
            transcript = "No speech was detected in this recording."

        update_processing_stage(session_id, "analyzing_audio", 35)
        audio_quality = analyze_audio_quality(audio_path)

        update_processing_stage(session_id, "analyzing_posture", 45)
        if not os.path.exists(video_path) or os.path.getsize(video_path) == 0:
            logger.error("Video file missing or empty: %s", video_path)
            posture_data = _default_posture("Video file was not downloaded correctly")
        else:
            posture_data = analyze_posture(video_path)
        logger.info("Posture result: score=%d frames=%d", posture_data.get("posture_score", 0), posture_data.get("frames_analyzed", 0))

        update_processing_stage(session_id, "analyzing_emotion", 55)
        if not os.path.exists(video_path) or os.path.getsize(video_path) == 0:
            emotion_data = _default_emotions("Video file was not downloaded correctly")
        else:
            emotion_data = analyze_emotions(video_path)
        logger.info("Emotion result: dominant=%s engagement=%d", emotion_data.get("dominant_emotion", "unknown"), emotion_data.get("engagement_score", 0))

        logger.info(
            "Analysis complete: posture=%d engagement=%d stress=%d volume=%.1fdB wpm=%.0f fillers=%d",
            posture_data.get("posture_score", 0),
            emotion_data.get("engagement_score", 0),
            emotion_data.get("stress_level", 0),
            audio_quality.get("avg_volume_db", 0),
            transcript_meta.get("words_per_minute", 0),
            transcript_meta.get("filler_count", 0),
        )

        update_processing_stage(session_id, "generating_report", 70)
        try:
            ai_result = gemini_analyze(
                transcript=transcript,
                mode=mode,
                job_title=job_title,
                scenario=scenario,
                posture_data=posture_data,
                emotion_data=emotion_data,
                audio_quality=audio_quality,
                transcript_meta=transcript_meta,
                questions=questions,
            )
            if not ai_result.get("score_global"):
                ai_result["score_global"] = compute_global_score(ai_result)
        except Exception as gemini_exc:
            logger.warning("Gemini unavailable, using fallback: %s", str(gemini_exc))
            ai_result = _fallback_analysis(
                transcript, mode, posture_data, emotion_data, audio_quality, transcript_meta,
            )

        global_score = int(ai_result.get("score_global", 0))

        combined_feedback = ai_result.get("feedback_text", "")
        if posture_data.get("notes"):
            combined_feedback += f"\n\nBody Language: {posture_data['notes']}"
        if emotion_data.get("notes"):
            combined_feedback += f"\n\nFacial Expressions: {emotion_data['notes']}"

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
                "feedback_text": combined_feedback,
                "posture_notes": posture_data.get("notes", ""),
                "emotion_summary": emotion_data.get("emotion_summary", {}),
                "strengths": ai_result.get("strengths", []),
                "weaknesses": ai_result.get("weaknesses", []),
                "recommendations": ai_result.get("recommendations", []),
                "practice_exercises": ai_result.get("practice_exercises", []),
                "filler_words_detected": ai_result.get("filler_words_detected", ""),
                "speech_pace": ai_result.get("speech_pace", transcript_meta.get("pace_assessment", "")),
                "opening_quality": ai_result.get("opening_quality", ""),
                "closing_quality": ai_result.get("closing_quality", ""),
                "vocabulary_assessment": ai_result.get("vocabulary_assessment", ""),
                "body_language": {
                    "posture_score": posture_data.get("posture_score"),
                    "gesture_frequency": posture_data.get("gesture_frequency"),
                    "shoulder_stability": posture_data.get("shoulder_stability"),
                    "centered_score": posture_data.get("centered_score"),
                },
                "facial_expression": {
                    "engagement_score": emotion_data.get("engagement_score"),
                    "confidence_score": emotion_data.get("confidence_score"),
                    "stress_level": emotion_data.get("stress_level"),
                    "smile_ratio": emotion_data.get("smile_ratio"),
                    "dominant_emotion": emotion_data.get("dominant_emotion"),
                    "emotion_distribution": emotion_data.get("emotion_distribution", {}),
                    "emotion_timeline": emotion_data.get("emotion_timeline", []),
                },
                "audio_quality": {
                    "duration_s": audio_quality.get("duration_s"),
                    "avg_volume_db": audio_quality.get("avg_volume_db"),
                    "silence_ratio": audio_quality.get("silence_ratio"),
                    "dynamic_range_db": audio_quality.get("dynamic_range_db"),
                    "volume_assessment": audio_quality.get("volume_assessment"),
                    "silence_assessment": audio_quality.get("silence_assessment"),
                },
                "transcript_metadata": {
                    "words_per_minute": transcript_meta.get("words_per_minute"),
                    "filler_count": transcript_meta.get("filler_count"),
                    "filler_percentage": transcript_meta.get("filler_percentage"),
                    "pace_assessment": transcript_meta.get("pace_assessment"),
                    "language": transcript_meta.get("language"),
                },
            },
        )

        update_session_status(session_id, "complete")
        mark_complete(job_id, session_id)
        logger.info("Pipeline complete: job_id=%s session_id=%s global_score=%d", job_id, session_id, global_score)

    except Exception as exc:
        logger.exception("Pipeline failed: job_id=%s session_id=%s", job_id, session_id)
        update_session_status(session_id, "error")
        mark_error(job_id, session_id, str(exc))
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
