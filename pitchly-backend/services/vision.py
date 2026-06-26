# Responsibility: posture and facial emotion analysis from video frames
# Uses MediaPipe (posture/gaze) and DeepFace (emotions) — both local, no API cost

import logging

logger = logging.getLogger(__name__)


def analyze_posture(video_path: str) -> dict:
    """
    Analyze posture from video using MediaPipe Pose.
    Samples every 10th frame to balance speed and accuracy.
    Returns a score 0-100 and human-readable notes.
    """
    try:
        import cv2
        import mediapipe as mp

        mp_pose = mp.solutions.pose
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            logger.warning("Could not open video for posture analysis: %s", video_path)
            return {
                "posture_score": 50,
                "frames_analyzed": 0,
                "notes": "Video could not be opened for analysis.",
            }

        frames_with_pose = 0
        total_sampled = 0
        frame_index = 0

        with mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        ) as pose:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                frame_index += 1
                if frame_index % 10 != 0:
                    continue
                total_sampled += 1
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(rgb)
                if results.pose_landmarks:
                    frames_with_pose += 1

        cap.release()

        score = int((frames_with_pose / max(total_sampled, 1)) * 100)

        if score >= 80:
            notes = "Excellent posture maintained throughout the session."
        elif score >= 60:
            notes = "Good posture overall with occasional inconsistencies."
        elif score >= 40:
            notes = "Posture was inconsistent — try to stay upright and centered."
        else:
            notes = "Posture needs improvement — ensure you are visible and upright."

        logger.info("Posture analysis complete: score=%d frames_sampled=%d", score, total_sampled)
        return {
            "posture_score": score,
            "frames_analyzed": total_sampled,
            "notes": notes,
        }

    except ImportError as e:
        logger.error("Vision library not available: %s", str(e))
        return {
            "posture_score": 50,
            "frames_analyzed": 0,
            "notes": "Posture analysis unavailable — library not installed.",
        }
    except Exception as e:
        logger.error("Posture analysis failed: %s", str(e))
        return {
            "posture_score": 50,
            "frames_analyzed": 0,
            "notes": "Posture analysis could not be completed.",
        }


def analyze_emotions(video_path: str) -> dict:
    """
    Analyze facial emotions from video using DeepFace.
    Samples 1 frame per second (every 30th frame).
    Returns emotion counts, dominant emotion, and frame count.
    """
    try:
        import cv2
        from deepface import DeepFace

        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            logger.warning("Could not open video for emotion analysis: %s", video_path)
            return {
                "emotion_summary": {},
                "dominant_emotion": "neutral",
                "frames_analyzed": 0,
            }

        emotions_detected = []
        frame_index = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame_index += 1
            if frame_index % 30 != 0:  # ~1 frame per second at 30fps
                continue
            try:
                analysis = DeepFace.analyze(
                    frame,
                    actions=["emotion"],
                    enforce_detection=False,
                    silent=True,
                )
                if analysis:
                    emotions_detected.append(analysis[0]["dominant_emotion"])
            except Exception:
                pass  # skip frames where face detection fails

        cap.release()

        emotion_counts: dict[str, int] = {}
        for emotion in emotions_detected:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        dominant = (
            max(emotion_counts, key=emotion_counts.get)
            if emotion_counts
            else "neutral"
        )

        logger.info(
            "Emotion analysis complete: dominant=%s frames=%d",
            dominant,
            len(emotions_detected),
        )
        return {
            "emotion_summary": emotion_counts,
            "dominant_emotion": dominant,
            "frames_analyzed": len(emotions_detected),
        }

    except ImportError as e:
        logger.error("DeepFace not available: %s", str(e))
        return {
            "emotion_summary": {},
            "dominant_emotion": "neutral",
            "frames_analyzed": 0,
        }
    except Exception as e:
        logger.error("Emotion analysis failed: %s", str(e))
        return {
            "emotion_summary": {},
            "dominant_emotion": "neutral",
            "frames_analyzed": 0,
        }