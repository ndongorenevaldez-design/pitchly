# Responsibility: posture and facial emotion analysis from video frames
# Uses MediaPipe (posture/gaze) and DeepFace (emotions) — both local, no API cost
# Produces coaching-ready metrics, not raw landmark data

import logging
import math

logger = logging.getLogger(__name__)


def analyze_posture(video_path: str) -> dict:
    """
    Analyze posture from video using MediaPipe Pose.
    Extracts: shoulder alignment, head tilt, body stability, gesture frequency.
    Returns coaching metrics, not raw landmarks.
    """
    try:
        import cv2
        import mediapipe as mp

        mp_pose = mp.solutions.pose
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            logger.warning("Could not open video for posture analysis: %s", video_path)
            return _default_posture("Video could not be opened for analysis.")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_s = total_frames / fps if fps > 0 else 0

        frames_with_pose = 0
        total_sampled = 0
        frame_index = 0

        shoulder_tilts = []
        head_positions = []
        hand_positions_left = []
        hand_positions_right = []
        nose_positions = []

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
                if frame_index % 5 != 0:
                    continue
                total_sampled += 1
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(rgb)
                if results.pose_landmarks:
                    frames_with_pose += 1
                    lm = results.pose_landmarks.landmark

                    left_shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
                    right_shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
                    shoulder_tilts.append(abs(left_shoulder.y - right_shoulder.y))

                    nose = lm[mp_pose.PoseLandmark.NOSE]
                    nose_positions.append((nose.x, nose.y))

                    left_wrist = lm[mp_pose.PoseLandmark.LEFT_WRIST]
                    right_wrist = lm[mp_pose.PoseLandmark.RIGHT_WRIST]
                    hand_positions_left.append((left_wrist.x, left_wrist.y))
                    hand_positions_right.append((right_wrist.x, right_wrist.y))

                    head_positions.append((nose.x, nose.y))

        cap.release()

        detection_rate = (frames_with_pose / max(total_sampled, 1)) * 100
        posture_score = int(detection_rate)

        shoulder_stability = 100
        if shoulder_tilts:
            avg_tilt = sum(shoulder_tilts) / len(shoulder_tilts)
            shoulder_stability = max(0, min(100, int(100 - avg_tilt * 500)))

        gesture_count = 0
        if len(hand_positions_left) > 2:
            for i in range(1, len(hand_positions_left)):
                dx = hand_positions_left[i][0] - hand_positions_left[i-1][0]
                dy = hand_positions_left[i][1] - hand_positions_left[i-1][1]
                if math.sqrt(dx*dx + dy*dy) > 0.03:
                    gesture_count += 1
        if len(hand_positions_right) > 2:
            for i in range(1, len(hand_positions_right)):
                dx = hand_positions_right[i][0] - hand_positions_right[i-1][0]
                dy = hand_positions_right[i][1] - hand_positions_right[i-1][1]
                if math.sqrt(dx*dx + dy*dy) > 0.03:
                    gesture_count += 1

        gestures_per_minute = (gesture_count / max(duration_s, 1)) * 60

        body_movement = 0
        if len(nose_positions) > 2:
            movements = []
            for i in range(1, len(nose_positions)):
                dx = nose_positions[i][0] - nose_positions[i-1][0]
                dy = nose_positions[i][1] - nose_positions[i-1][1]
                movements.append(math.sqrt(dx*dx + dy*dy))
            avg_movement = sum(movements) / len(movements)
            body_movement = min(100, int(avg_movement * 2000))

        centered_score = 50
        if nose_positions:
            avg_x = sum(p[0] for p in nose_positions) / len(nose_positions)
            centered_score = max(0, min(100, int(100 - abs(avg_x - 0.5) * 200)))

        notes_parts = []
        if posture_score >= 80:
            notes_parts.append("Strong body visibility throughout")
        elif posture_score >= 60:
            notes_parts.append("Generally visible with occasional frame drift")
        else:
            notes_parts.append("Body positioning needs improvement — stay centered and visible")

        if shoulder_stability >= 80:
            notes_parts.append("stable shoulders")
        elif shoulder_stability >= 60:
            notes_parts.append("mostly level shoulders")
        else:
            notes_parts.append("noticeable shoulder tilt — try to stay balanced")

        if gestures_per_minute > 15:
            notes_parts.append("active hand gestures")
        elif gestures_per_minute > 5:
            notes_parts.append("moderate gesture use")
        else:
            notes_parts.append("limited hand gestures — consider using more expressive movements")

        if centered_score >= 70:
            notes_parts.append("well-centered in frame")
        else:
            notes_parts.append("position drift detected — try to stay centered")

        notes = ". ".join(notes_parts) + "."

        logger.info(
            "Posture analysis complete: score=%d gestures=%.1f/min shoulder_stability=%d centered=%d",
            posture_score, gestures_per_minute, shoulder_stability, centered_score,
        )
        return {
            "posture_score": posture_score,
            "frames_analyzed": total_sampled,
            "notes": notes,
            "gesture_frequency": round(gestures_per_minute, 1),
            "shoulder_stability": shoulder_stability,
            "body_movement": body_movement,
            "centered_score": centered_score,
            "detection_rate": round(detection_rate, 1),
            "duration_s": round(duration_s, 1),
        }

    except ImportError as e:
        logger.error("Vision library not available: %s", str(e))
        return _default_posture("Posture analysis unavailable — library not installed.")
    except Exception as e:
        logger.error("Posture analysis failed: %s", str(e))
        return _default_posture("Posture analysis could not be completed.")


def _default_posture(notes: str) -> dict:
    return {
        "posture_score": 50,
        "frames_analyzed": 0,
        "notes": notes,
        "gesture_frequency": 0,
        "shoulder_stability": 50,
        "body_movement": 50,
        "centered_score": 50,
        "detection_rate": 0,
        "duration_s": 0,
    }


def analyze_emotions(video_path: str) -> dict:
    """
    Analyze facial emotions from video using DeepFace.
    Produces coaching-ready emotion metrics, not just raw counts.
    """
    try:
        import cv2
        from deepface import DeepFace

        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            logger.warning("Could not open video for emotion analysis: %s", video_path)
            return _default_emotions("Video could not be opened for emotion analysis.")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_s = total_frames / fps if fps > 0 else 0

        emotions_detected = []
        frame_index = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame_index += 1
            if frame_index % 30 != 0:
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
            except Exception as frame_exc:
                logger.debug("Face detection skipped for frame: %s", str(frame_exc))

        cap.release()

        emotion_counts: dict[str, int] = {}
        for emotion in emotions_detected:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        total_emotions = len(emotions_detected)

        dominant = (
            max(emotion_counts, key=emotion_counts.get)
            if emotion_counts
            else "neutral"
        )

        positive_emotions = {"happy", "surprise"}
        negative_emotions = {"sad", "angry", "fear", "disgust"}
        neutral_emotions = {"neutral"}

        positive_count = sum(emotion_counts.get(e, 0) for e in positive_emotions)
        negative_count = sum(emotion_counts.get(e, 0) for e in negative_emotions)
        neutral_count = emotion_counts.get("neutral", 0)

        engagement_score = min(100, int(
            ((positive_count + neutral_count * 0.5) / max(total_emotions, 1)) * 120
        ))

        confidence_emotion = emotion_counts.get("happy", 0) + emotion_counts.get("neutral", 0) * 0.7
        confidence_score = min(100, int((confidence_emotion / max(total_emotions, 1)) * 130))

        stress_level = min(100, int(
            (negative_count / max(total_emotions, 1)) * 150
        ))

        smile_ratio = round(emotion_counts.get("happy", 0) / max(total_emotions, 1) * 100, 1)

        positive_ratio = round(positive_count / max(total_emotions, 1) * 100, 1)
        negative_ratio = round(negative_count / max(total_emotions, 1) * 100, 1)
        neutral_ratio = round(neutral_count / max(total_emotions, 1) * 100, 1)

        timeline = []
        chunk_size = max(1, total_emotions // 10)
        for i in range(0, total_emotions, chunk_size):
            chunk = emotions_detected[i:i+chunk_size]
            if chunk:
                chunk_dominant = max(set(chunk), key=chunk.count)
                timeline.append({
                    "start_pct": round(i / max(total_emotions, 1) * 100),
                    "end_pct": round(min((i + chunk_size), total_emotions) / max(total_emotions, 1) * 100),
                    "emotion": chunk_dominant,
                })

        notes_parts = []
        if engagement_score >= 70:
            notes_parts.append("Strong facial engagement")
        elif engagement_score >= 50:
            notes_parts.append("Moderate engagement — try to show more expression")
        else:
            notes_parts.append("Low facial expressiveness — work on showing more emotion")

        if stress_level > 60:
            notes_parts.append("elevated stress signals detected — practice relaxation techniques")
        elif stress_level > 30:
            notes_parts.append("mild tension visible")
        else:
            notes_parts.append("calm and composed demeanor")

        if smile_ratio > 30:
            notes_parts.append("natural smiling detected")
        elif smile_ratio > 10:
            notes_parts.append("occasional smiles — try to smile more naturally")

        notes = ". ".join(notes_parts) + "."

        logger.info(
            "Emotion analysis complete: dominant=%s frames=%d engagement=%d confidence=%d stress=%d",
            dominant, total_emotions, engagement_score, confidence_score, stress_level,
        )
        return {
            "emotion_summary": emotion_counts,
            "dominant_emotion": dominant,
            "frames_analyzed": total_emotions,
            "engagement_score": engagement_score,
            "confidence_score": confidence_score,
            "stress_level": stress_level,
            "smile_ratio": smile_ratio,
            "positive_ratio": positive_ratio,
            "negative_ratio": negative_ratio,
            "neutral_ratio": neutral_ratio,
            "emotion_timeline": timeline,
            "emotion_distribution": {
                "positive": positive_ratio,
                "negative": negative_ratio,
                "neutral": neutral_ratio,
            },
            "notes": notes,
        }

    except ImportError as e:
        logger.error("DeepFace not available: %s", str(e))
        return _default_emotions("Emotion analysis unavailable — library not installed.")
    except Exception as e:
        logger.error("Emotion analysis failed: %s", str(e))
        return _default_emotions("Emotion analysis could not be completed.")


def _default_emotions(notes: str) -> dict:
    return {
        "emotion_summary": {},
        "dominant_emotion": "neutral",
        "frames_analyzed": 0,
        "engagement_score": 50,
        "confidence_score": 50,
        "stress_level": 30,
        "smile_ratio": 0,
        "positive_ratio": 0,
        "negative_ratio": 0,
        "neutral_ratio": 100,
        "emotion_timeline": [],
        "emotion_distribution": {"positive": 0, "negative": 0, "neutral": 100},
        "notes": notes,
    }